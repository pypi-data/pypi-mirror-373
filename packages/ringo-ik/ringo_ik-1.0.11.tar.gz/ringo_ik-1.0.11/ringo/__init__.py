import os
import sys
import platform
import json
import multiprocessing

from typing import (
    Optional,
    Any,
    Literal,
)
from .graph_utils import *

__version__ = "1.0.11"
sys.path.insert(0, os.path.dirname(__file__))

if platform.system() == "Windows":
    mypath = os.path.dirname(os.path.realpath(__file__))
    if mypath not in sys.path:
        sys.path.insert(0, mypath)
    os.add_dll_directory(mypath)

from .cpppart import cpppart as base
try:
    from .pyxyz import Confpool, MolProxy
except ImportError:
    pass

import networkx as nx
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
    create_model,
)

DEG2RAD = 0.0174532925199432957692
RAD2DEG = 1 / DEG2RAD
H2KC = 627.509474063
KC2H = 1 / H2KC


class Molecule(base.Molecule):

    def __init__(
        self,
        request_free=None,
        request_fixed=None,
        require_best_sequence=False,
        clear_feed=True,
    ) -> None:
        if clear_feed:
            base.clear_status_feed()

        super().__init__()

        if request_free is not None:
            request_free = [(i - 1, j - 1) for i, j in request_free]
            self._set_requested_dofs(request_free)

        if request_fixed is not None:
            request_fixed = [(i - 1, j - 1) for i, j in request_fixed]
            self._set_fixed_dofs(request_fixed)

        if require_best_sequence:
            self._require_best_sequence()

    @classmethod
    def from_sdf(
        cls,
        sdf_path: str,
        request_free=None,
        request_fixed=None,
        require_best_sequence=False,
        clear_feed=True,
    ) -> 'Molecule':
        """Initializes the molecule using the provided SDF file, optionally setting
        specific degrees of freedom as free or fixed and enforcing the optimal conformer assembly sequence.

        Args:
            sdf_path (str): Path to the input SDF file.
            request_free (list[tuple[int, int]], optional): List of bonds to be made rotatable.
            request_fixed (list[tuple[int, int]], optional): List of additional bonds with fixed dihedrals.
            require_best_sequence (bool, optional): Whether to enforce optimal assembly sequence.
            clear_feed (bool, optional): Whether to clear the status feed before initialization.

        Returns:
            Molecule: The constructed Molecule object.
        """
        assert isinstance(sdf_path,
                          str), "sdf_path must be a string (name of your SDF)"
        mol = cls(
            request_free=request_free,
            request_fixed=request_fixed,
            require_best_sequence=require_best_sequence,
            clear_feed=clear_feed,
        )
        mol._sdf_constructor(sdf_path)
        return mol

    @classmethod
    def from_graph(
        cls,
        graph_input: GraphInput,
        request_free=None,
        require_best_sequence=False,
        clear_feed=True,
    ) -> 'Molecule':
        """Creates a Molecule instance from graph representation and local geometry information
        without using a starting 3D geometry. Optionally, sets specific degrees of freedom as
        free or fixed and forces the optimal conformer assembly sequence.

        Args:
            graph_input (GraphInput): Molecular representation.
            request_free (list[tuple[int, int]], optional): List of bonds to be made rotatable.
            require_best_sequence (bool, optional): Whether to enforce optimal assembly sequence.
            clear_feed (bool, optional): Whether to clear the status feed before initialization.

        Returns:
            Molecule: The constructed Molecule object.
        """
        mol = cls(
            request_free=request_free,
            require_best_sequence=require_best_sequence,
            clear_feed=clear_feed,
        )
        mol._graph_constructor(graph_input)
        return mol

    def get_xyzless_input(self) -> GraphInput:
        """Returns a graph representation and local geometry information about the molecule
        without using a starting 3D geometry. Can be modified and used for running initialization
        of another Molecule object.
        Only rigid fragments (e.g. benzene rings) are explicitly saved using 3D coordinates.

        Returns:
            GraphInput: the resulting molecule representation
        """
        raw_data = self._build_xyzless_input()
        graph = raw_data['graph']
        rigid_fragments = raw_data['rigid_fragments']
        for node, attrs in graph.nodes(data=True):
            attrs['data'] = AtomAttr(
                symbol=attrs['symbol'],
                poly=Polyhedron(coords={
                    i: np.array(xyz)
                    for i, xyz in attrs['poly'].items()
                }),
            )
            del attrs['poly']

        for nA, nB, attrs in graph.edges(data=True):
            if 'fixed_value' in attrs:
                data = attrs['fixed_value']
                fixed_value = DihedralValue(
                    atoms=data[0],
                    value=data[1],
                )
                del attrs['fixed_value']
            else:
                fixed_value = None

            attrs['data'] = BondAttr(
                bond_type=attrs['bond_type'],
                length=attrs['bond_length'],
                fixed_value=fixed_value,
            )
            del attrs['bond_type']
            del attrs['bond_length']

        return GraphInput(
            graph=graph,
            rigid_fragments=rigid_fragments,
        )


def get_one_seed():
    return int.from_bytes(os.urandom(3), byteorder="big")


def create_seed_list(size):
    unique_set = set()
    result = []
    while len(result) < size:
        list_element = get_one_seed()
        if list_element not in unique_set:
            unique_set.add(list_element)
            result.append(list_element)
    return result


MCR_FLAGS_DESCRIPTIONS = {
    'total': {
        'ntries': "Number of sampling attempts in total"
    },
    'good': {
        'nsucc':
        "Successfull iterations of MCR with postoptimization (if it's enabled)",
    },
    'bad': {
        'nfail':
        "Cases of TLC unable to provide correct solutions (only incorrect ones)",
        'nzero': "Cases of zero IK solutions",
        'ngeom': "MCR sampling attempts didn't pass geometry validation",
        'nolap': "MCR sampling attempts didn't pass overlap checks",
        'npostopt_fail':
        "Crashed postoptimizations (BFGS unable to make a step, etc.)",
        'npostopt_more_steps':
        "Postoptimization unable to pass the overlap and validity requirements",
        'ndihedral_filtering':
        "Discarded due to violated configuration rules for dihedrals",
        'nrmsd_duplicate': "Discarded by RMSD filter",
    }
}


def mcr_result_to_list(result_data: dict) -> dict:
    result_descriptions = {}
    for section_name, section_cases in MCR_FLAGS_DESCRIPTIONS.items():
        result_descriptions[section_name] = {}
        for key, description in section_cases.items():
            if key in result_data:
                result_descriptions[section_name][description] = result_data[
                    key]
    return result_descriptions


class TerminationConditions(BaseModel):
    timelimit: Optional[int] = Field(
        None,
        gt=0,
        description="Time limit in seconds, must be positive if provided")
    max_conformers: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum number of successfully generated conformations")
    max_tries: Optional[int] = Field(
        None,
        ge=0,
        description=
        "Number of sampling attempts (expect success rate of around 1%)")

    @model_validator(mode='before')
    def check_at_least_one(cls, values):
        if not any(
                values.get(field) is not None
                for field in ('timelimit', 'max_conformers', 'max_tries')):
            raise ValueError(
                'At least one of timelimit, max_conformers, or max_tries must be provided.'
            )
        return values


class RmsdFilteringSettings(BaseModel):
    ignore_elements: list[str] = Field(['HCarbon'],
                                       description="Elements to ignore")
    rmsd_cutoff: float = Field(0.2, gt=0.0, description="RMSD threshold")
    mirror_match: bool = Field(
        True, description="Whether mirror reflections are considered the same")


class ConfsearchInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    molecule: Molecule
    termination_conditions: TerminationConditions
    pool: Optional[Confpool] = Field(None, validate_default=True)
    rmsd_settings: Optional[RmsdFilteringSettings
                            | Literal['default']] = Field(
                                None, validate_default=True)
    postopt_settings: Optional[Any] = Field([], validate_default=True)
    geometry_validation: Optional[Any] = {}
    nthreads: int = Field(1, gt=0, description="Number of threads to use")
    filter: None = None
    clear_feed: bool = Field(
        True, description="Whether to clear the feed of warning messages")
    seeds: Optional[list[int]] = Field(
        None,
        description=
        "Random seeds for sampling. Length must be precisely the number of threads."
    )

    @field_validator("molecule")
    @classmethod
    def check_molecule(cls, mol: Molecule) -> Molecule:
        assert mol.is_ready(), (
            "The Molecule object does not seem to be well-initialized.")
        return mol

    @field_validator("pool")
    @classmethod
    def check_pyxyz(
        cls,
        p: Optional[Confpool],
    ) -> Optional[Confpool]:
        if base.use_pyxyz:
            assert p is not None, "Confpool object must be passed to store generated conformations"
            assert len(
                p
            ) == 0, "The Confpool object must be empty, but it already contains some geometries"  # TODO: Full check that Confpool is default
        else:
            assert p is None, "PyXYZ is not included in the current build"

        return p

    @field_validator("nthreads")
    @classmethod
    def check_threading(cls, nthreads: int) -> int:
        if nthreads == 1:
            assert base.use_mcr_singlethreaded, "The default single-threaded Monte-Carlo is not supported by the current build of Ringo"
        elif nthreads > 1:
            assert base.use_mcr_parallel, "Parallel Monte-Carlo is not supported by the current build of Ringo"

        return nthreads

    @field_validator("postopt_settings")
    @classmethod
    def check_postopt(cls, postopt_settings: Any) -> Any:
        DEFAULT_DISABLED = [{'enabled': False}, {'enabled': False}]
        if not base.use_postoptimization:
            assert len(postopt_settings) == 0 or (
                postopt_settings == DEFAULT_DISABLED
            ), "Postoptimization is not supported by this build"

        if len(postopt_settings) == 0:
            result = DEFAULT_DISABLED
        else:
            result = postopt_settings

        assert len(result) == 2, "Two-stage optimization is supported"
        return result

    @field_validator("rmsd_settings")
    @classmethod
    def check_rmsd_settings(
        cls,
        rmsd_settings: Optional[RmsdFilteringSettings | Literal['default']]
    ) -> RmsdFilteringSettings | None:
        if rmsd_settings is not None:
            assert base.use_pyxyz, "PyXYZ is not included in the current build, so rmsd_settings must be None"

        if base.use_pyxyz:
            assert rmsd_settings is not None, "RMSD filtering settings must be provided"

        if rmsd_settings == 'default':
            result = RmsdFilteringSettings(
                ignore_elements=['HCarbon'],
                rmsd_cutoff=0.2,
                mirror_match=True,
            )
        else:
            result = rmsd_settings

        return result

    @model_validator(mode='after')
    def check_seeds(self):
        if self.seeds is None:
            self.seeds = create_seed_list(self.nthreads)
        else:
            assert len(
                self.seeds
            ) == self.nthreads, f"Provided {len(self.seeds)} seed(s) is not equal to the number of threads {self.nthreads}"
        return self

    def _to_cxx_format(self):  # -> base.ConfsearchInputCxx:
        return base.ConfsearchInputCxx(self)


def run_confsearch(input: ConfsearchInput):
    res = base.run_confsearch(input._to_cxx_format())
    return res


class SysConfsearchInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    molecule: Molecule
    custom_preferences: dict[int, list[float]]
    default_dihedrals: list[float] = Field(
        default_factory=lambda: [-60.0, 60.0, 180.0])
    pool: Optional[Confpool] = Field(None, validate_default=True)
    rmsd_settings: Optional[RmsdFilteringSettings
                            | Literal['default']] = Field(
                                None, validate_default=True)
    clear_feed: bool = Field(
        True, description="Whether to clear the feed of warning messages")
    show_status: bool = Field(
        True, description="Whether to use interactive status monitoring")
    nthreads: int = Field(1,
                          description="Number of threads to use for sampling")

    @field_validator("pool")
    @classmethod
    def check_pyxyz(
        cls,
        p: Optional[Confpool],
    ) -> Optional[Confpool]:
        if base.use_pyxyz:
            assert p is not None, "Confpool object must be passed to store generated conformations"
            assert len(
                p
            ) == 0, "The Confpool object must be empty, but it already contains some geometries"  # TODO: Full check that Confpool is default
        else:
            assert p is None, "PyXYZ is not included in the current build"

        return p

    @field_validator("rmsd_settings")
    @classmethod
    def check_rmsd_settings(
        cls,
        rmsd_settings: Optional[RmsdFilteringSettings | Literal['default']]
    ) -> RmsdFilteringSettings | None:
        if rmsd_settings is not None:
            assert base.use_pyxyz, "PyXYZ is not included in the current build, so rmsd_settings must be None"

        if base.use_pyxyz:
            assert rmsd_settings is not None, "RMSD filtering settings must be provided"

        if rmsd_settings == 'default':
            result = RmsdFilteringSettings(
                ignore_elements=['HCarbon'],
                # ignore_elements=[],
                rmsd_cutoff=0.2,
                mirror_match=True,
            )
        else:
            result = rmsd_settings

        return result

    @field_validator("nthreads")
    @classmethod
    def check_threading(cls, nthreads: int) -> int:
        assert nthreads >= 1, "Number of threads must be positive"
        num_procs = multiprocessing.cpu_count()
        assert nthreads <= num_procs, f"Number of threads must be less or equal than {num_procs} for this machine"
        return nthreads

    def _to_cxx_format(self) -> base.SysConfsearchInputCxx:
        return base.SysConfsearchInputCxx(self)


def systematic_sampling(input: SysConfsearchInput):
    res = base.systematic_sampling(input._to_cxx_format())
    return res


# Work with vdw radii controls
build_flags = base.build_flags
if base.use_overlap_detection:
    get_vdw_radii = base.get_vdw_radii
    set_vdw_radii = base.set_vdw_radii
    set_radius_multiplier = base.set_radius_multiplier

# Work with Ringo status feed
WARNING_CODES = base.warning_codes
for warning_code, warning_line in base.warning_codes.items():
    globals(
    )[warning_code] = warning_line  # Declares str variables IK_NOT_APPLIED, SUBOPTIMAL_SOLN_SEQ, UNMET_DOF_REQUEST, etc.
add_message_to_feed = base.add_message_to_feed
clear_status_feed = base.clear_status_feed


def get_status_feed(important_only=True):
    json_data = base.get_status_feed()
    parsed_data = [json.loads(item) for item in json_data]
    for item in parsed_data:
        item['important'] = '[important]' in item['subject']
        item['subject'] = item['subject'].replace('[important]', '')
        if len(item['atoms']) > 0:
            item['atoms'] = sorted([idx + 1 for idx in item['atoms']])
        else:
            del item['atoms']

    if important_only:
        return [item for item in parsed_data if item['important']]
    else:
        return parsed_data


# Summarising statistics for the molecule
def get_molecule_statistics(m):
    graph = m.molgraph_access()
    symbols = m.get_symbols()

    composition = set(symbols[atom] for atom in graph.nodes)
    composition = {element: 0 for element in composition}
    for atom in graph.nodes:
        composition[symbols[atom]] += 1

    temp_graph = nx.Graph()
    temp_graph.add_edges_from(graph.edges)
    molgraph_bridges = list(nx.bridges(temp_graph))
    temp_graph.remove_edges_from(molgraph_bridges)
    lone_nodes = []
    for node in temp_graph.nodes:
        if len(list(temp_graph.neighbors(node))) == 0:
            lone_nodes.append(node)
    temp_graph.remove_nodes_from(lone_nodes)
    num_cyclic_parts = len([x for x in nx.connected_components(temp_graph)])
    all_ring_atoms = list(temp_graph.nodes)

    mcb = [set(c) for c in nx.minimum_cycle_basis(graph)]
    num_cyclic_rotatable_bonds = 0
    num_rotatable_bonds = 0
    for vxA, vxB in graph.edges:
        if len(list(graph.neighbors(vxA))) > 1 and len(
                list(graph.neighbors(vxB))) > 1:
            num_rotatable_bonds += 1
            for ring_atoms in mcb:
                if vxA in ring_atoms and vxB in ring_atoms:
                    num_cyclic_rotatable_bonds += 1
                    break

    num_cyclic_dofs = 0
    dof_list, _ = m.get_ps()
    for sideA, atA, atB, sideB in dof_list:
        if atA in all_ring_atoms and atB in all_ring_atoms and \
                (atA, atB) not in molgraph_bridges and (atB, atA) not in molgraph_bridges:
            num_cyclic_dofs += 1

    result = {
        'composition':
        composition,
        'num_atoms':
        graph.number_of_nodes(),
        'num_heavy_atoms':
        len([atom for atom in graph.nodes if symbols[atom] != 'H']),
        'num_bonds':
        graph.number_of_edges(),
        'num_rotatable_bonds':
        num_rotatable_bonds,
        'num_cyclic_rotatable_bonds':
        num_cyclic_rotatable_bonds,
        'largest_macrocycle_size':
        max([len(item) for item in mcb]) if len(mcb) > 0 else 0,
        'n_flexible_rings':
        m.get_num_flexible_rings(),
        'n_rigid_rings':
        m.get_num_rigid_rings(),
        'num_dofs':
        len(dof_list),
        'num_cyclic_dofs':
        num_cyclic_dofs,
        'cyclomatic_number':
        graph.number_of_edges() - graph.number_of_nodes() + 1,
        'num_cyclic_parts':
        num_cyclic_parts,
    }
    return result
