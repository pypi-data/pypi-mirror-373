import sys
import numpy as np
import networkx as nx
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

from typing import Optional, Dict, Tuple, List


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Polyhedron:
    """Stores information about coordination polyhedron of a single atom in a molecule"""
    coords: Dict[int, np.ndarray]

    def inverted(self) -> 'Polyhedron':
        return Polyhedron({k: -xyz for k, xyz in self.coords.items()})

    def _raw_data(self):
        return {
            'idxs': [i for i in self.coords.keys()],
            'coords': [xyz.tolist() for xyz in self.coords.values()],
        }

    @classmethod
    def from_neighbors(cls,
                       neighbors: List[int],
                       num_lone_pairs: Optional[int] = None):
        """Guess atomic polyhedron based on VSEPR principle"""
        if num_lone_pairs is None:
            num_lone_pairs = 0

        return cls({
            key: dir
            for key, dir in zip(
                neighbors,
                Polyhedron._generate_unit_vectors(
                    len(neighbors) + num_lone_pairs),
            )
        })

    @staticmethod
    def _generate_unit_vectors(N: int) -> np.ndarray:
        """Generate N three-dimensional unit vectors directed towards vertices of coordination polyhedron"""
        if N == 1:
            # Just return one vector pointing along the x-axis
            return np.array([[1.0, 0.0, 0.0]])
        elif N == 2:
            # Return two vectors pointing along the x-axis and its opposite direction
            return np.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
        elif N == 3:
            # Return three vectors forming a 120-degree angle with each other
            angle = 2 * np.pi / 3
            vectors = np.zeros((3, 3))
            vectors[0] = [1.0, 0.0, 0.0]
            vectors[1] = [np.cos(angle), np.sin(angle), 0.0]
            vectors[2] = [np.cos(angle), -np.sin(angle), 0.0]
            return vectors
        elif N == 4:
            # Return four vectors forming a regular tetrahedron
            vectors: np.ndarray = np.zeros((4, 3))
            vectors[0] = [1.0, 1.0, 1.0]
            vectors[1] = [-1.0, 1.0, -1.0]
            vectors[2] = [-1.0, -1.0, 1.0]
            vectors[3] = [1.0, -1.0, -1.0]
            vectors /= np.sqrt(3)
            return vectors
        elif N == 5:
            # Generate unit vectors for a regular trigonal bipyramid
            angle = 2 * np.pi / 3
            vectors = np.zeros((5, 3))
            vectors[0] = [1.0, 0.0, 0.0]
            vectors[1] = [np.cos(angle), np.sin(angle), 0.0]
            vectors[2] = [np.cos(angle), -np.sin(angle), 0.0]
            vectors[3] = [0.0, 0.0, 1.0]
            vectors[4] = [0.0, 0.0, -1.0]
            return vectors
        elif N == 6:
            # Return six vectors forming a regular octahedron
            vectors = np.zeros((6, 3))
            vectors[0] = [1.0, 0.0, 0.0]
            vectors[1] = [-1.0, 0.0, 0.0]
            vectors[2] = [0.0, 1.0, 0.0]
            vectors[3] = [0.0, -1.0, 0.0]
            vectors[4] = [0.0, 0.0, 1.0]
            vectors[5] = [0.0, 0.0, -1.0]
            return vectors
        else:
            raise ValueError("Invalid value of N")


@dataclass
class AtomAttr:
    """These objects must be put into 'data' attr of molecular graph edges"""
    symbol: str
    poly: Polyhedron


@dataclass
class DihedralValue:
    """Must be used to specify desired values of fixed dihedrals"""
    atoms: tuple[int, int, int, int]
    value: float  # in degrees


@dataclass
class BondAttr:
    """These objects must be put into 'data' attr of molecular graph nodes"""
    length: float
    bond_type: int
    fixed_value: Optional[DihedralValue] = None


def smiles_to_graph(smiles: str):
    """Build molecule as NetworkX graph from SMILES. Requires RDKit"""
    try:
        from rdkit import Chem
    except ImportError as e:
        print("[ERROR] Make sure you have RDKit installed!!!", sys.stderr)
        raise e

    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)

    graph = nx.Graph()
    for atom in mol.GetAtoms():
        symbol = atom.GetSymbol()
        nnlp = 0
        if symbol in N_NLP:
            nnlp = N_NLP[symbol]
        graph.add_node(atom.GetIdx(), symbol=symbol, num_lone_pairs=nnlp)

    for bond in mol.GetBonds():
        start_idx = bond.GetBeginAtomIdx()
        end_idx = bond.GetEndAtomIdx()
        bond_type = int(bond.GetBondType())
        graph.add_edge(start_idx, end_idx, bond_type=bond_type)
    return graph


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class GraphInput:
    """Main object that stores information required for initializing Molecule
    without 3D geometry (xyzless way)"""

    graph: nx.Graph
    rigid_fragments: Dict[Tuple[int, ...], Dict[int, List[float]]]

    @classmethod
    def build(
        cls,
        graph: nx.Graph,
        rigid_fragments: List[Dict[int, List[float]]],
    ) -> 'GraphInput':
        """GraphInput constructor from a graph and a list of rigid fragments geometries
        represented by maps {atom_index => coordinates}."""
        return cls(
            graph=graph,
            rigid_fragments={
                tuple(sorted(fragment.keys())): fragment
                for fragment in rigid_fragments
            },
        )

    def _raw_rigid_fragments(
            self) -> List[Tuple[List[int], Dict[int, List[float]]]]:
        return [(list(k), v) for k, v in self.rigid_fragments.items()]


def graph_to_xyzless_input(
    molgraph: nx.Graph,
    fixed_dihedrals: Dict[Tuple[int, int, int, int], float],
    rigid_fragments: List[Dict[int, List[float]]] = [],
) -> GraphInput:
    """Converts a molecular graph and specified fixed dihedrals into a GraphInput object
    that is used for xyzless Molecule initialization.
    """
    fixed_dihedrals_fixed = expand_dihedrals(fixed_dihedrals)
    for nA, nB in molgraph.edges:
        length = (COVALENT_RADII[molgraph.nodes[nA]['symbol']] +
                  COVALENT_RADII[molgraph.nodes[nB]['symbol']])
        bond_data = BondAttr(
            length=length,
            bond_type=molgraph[nA][nB]['bond_type'],
        )
        if _seq(nA, nB) in fixed_dihedrals_fixed:
            bond_data.fixed_value = fixed_dihedrals_fixed[_seq(nA, nB)]
        molgraph[nA][nB]['data'] = bond_data

    for node, attrs in molgraph.nodes(data=True):
        neighbor_atoms = list(molgraph.neighbors(node))
        attrs['data'] = AtomAttr(
            symbol=attrs['symbol'],
            poly=Polyhedron.from_neighbors(
                neighbor_atoms,
                num_lone_pairs=attrs['num_lone_pairs'],
            ),
        )
    return GraphInput.build(
        graph=molgraph,
        rigid_fragments=rigid_fragments,
    )


def _seq(a: int, b: int):
    assert a != b
    if a < b:
        return (a, b)
    else:
        return (b, a)


def expand_dihedrals(inp: Dict[Tuple[int, int, int, int], float]):
    """Transforms dihedral angle representation into a mapping from central bonds to dihedral values.
    Ensures each bond is associated with at most one dihedral and adjusts atom indices to zero-based.
    """
    res: Dict[Tuple[int, int], DihedralValue] = {}
    for (a, b, c, d), value in inp.items():
        a, b, c, d = a - 1, b - 1, c - 1, d - 1
        key = _seq(b, c)
        assert key not in res, f"Dihedral on bond {key} provided multiple times"
        new_item = DihedralValue(atoms=(a, b, c, d), value=value)
        res[key] = new_item
    return res


COVALENT_RADII = {
    'H': 0.31,
    'He': 0.28,
    'Li': 1.28,
    'Be': 0.96,
    'B': 0.84,
    'C': 0.69,
    'N': 0.71,
    'O': 0.66,
    'F': 0.57,
    'Ne': 0.58,
    'Na': 1.66,
    'Mg': 1.41,
    'Al': 1.21,
    'Si': 1.11,
    'P': 1.07,
    'S': 1.05,
    'Cl': 1.02,
    'Ar': 1.06,
    'K': 2.03,
    'Ca': 1.76,
    'Sc': 1.7,
    'Ti': 1.6,
    'V': 1.53,
    'Cr': 1.39,
    'Mn': 1.61,
    'Fe': 1.52,
    'Co': 1.5,
    'Ni': 1.24,
    'Cu': 1.32,
    'Zn': 1.22,
    'Ga': 1.22,
    'Ge': 1.2,
    'As': 1.19,
    'Se': 1.2,
    'Br': 1.2,
    'Kr': 1.16,
    'Rb': 2.2,
    'Sr': 1.95,
    'Y': 1.9,
    'Zr': 1.75,
    'Nb': 1.64,
    'Mo': 1.54,
    'Tc': 1.47,
    'Ru': 1.46,
    'Rh': 1.42,
    'Pd': 1.39,
    'Ag': 1.45,
    'Cd': 1.44,
    'In': 1.42,
    'Sn': 1.39,
    'Sb': 1.39,
    'Te': 1.38,
    'I': 1.39,
    'Xe': 1.4,
    'Cs': 2.44,
    'Ba': 2.15,
    'La': 2.07,
    'Ce': 2.04,
    'Pr': 2.03,
    'Nd': 2.01,
    'Pm': 1.99,
    'Sm': 1.98,
    'Eu': 1.98,
    'Gd': 1.96,
    'Tb': 1.94,
    'Dy': 1.92,
    'Ho': 1.92,
    'Er': 1.89,
    'Tm': 1.9,
    'Yb': 1.87,
    'Lu': 1.87,
    'Hf': 1.75,
    'Ta': 1.7,
    'W': 1.62,
    'Re': 1.51,
    'Os': 1.44,
    'Ir': 1.41,
    'Pt': 1.36,
    'Au': 1.36,
    'Hg': 1.32,
    'Tl': 1.45,
    'Pb': 1.46,
    'Bi': 1.48,
    'Po': 1.4,
    'At': 1.5,
    'Rn': 1.5,
    'Fr': 2.6,
    'Ra': 2.21,
    'Ac': 2.15,
    'Th': 2.06,
    'Pa': 2.0,
    'U': 1.96,
    'Np': 1.9,
    'Pu': 1.87,
    'Am': 1.8,
    'Cm': 1.69
}
N_NLP = {'O': 2, 'N': 1, 'S': 2, 'P': 1}
