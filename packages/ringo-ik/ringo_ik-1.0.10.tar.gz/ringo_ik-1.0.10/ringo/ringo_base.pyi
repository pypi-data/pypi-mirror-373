from __future__ import annotations
import numpy
import typing
__all__ = ['Confpool', 'ConfpoolIterator', 'ConfpoolSlice', 'ConfsearchInputCxx', 'MolProxy', 'Molecule', 'Problem', 'SysConfsearchInputCxx', 'TLCExtSolver', 'TLCMain', 'add_message_to_feed', 'address_leaks_enabled', 'build_flags', 'clear_status_feed', 'get_radius_multiplier', 'get_status_feed', 'get_vdw_radii', 'mcr_allow_zero_steps', 'run_confsearch', 'set_radius_multiplier', 'set_vdw_radii', 'systematic_sampling', 'use_geometry_validation', 'use_mcr_parallel', 'use_mcr_singlethreaded', 'use_overlap_detection', 'use_postoptimization', 'use_pyxyz', 'vf3py_enabled', 'warning_codes']
class Confpool:
    """
    
    The core class of PyXYZ library responsible for storing and manipulating conformer ensembles.
    
    .. code-block:: python
    
        >>> from pyxyz import Confpool
        >>> p = Confpool() # You're good to go
    """
    def __copy__(self) -> Confpool:
        ...
    def __deepcopy__(self, arg0: dict) -> Confpool:
        ...
    def __delitem__(self, arg0: typing.Any) -> None:
        ...
    def __getitem__(self, arg0: typing.Any) -> typing.Any:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> ...:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.Any, arg1: typing.Any) -> None:
        ...
    def align_all_with(self, ref: ..., mirror_match: bool = True, allow_reorder: bool = True, inplace: bool = True) -> typing.Any:
        """
        Align all conformations to minimize RMSD with a given reference conformation ``ref``. There are 3 optional arguments:
        
        * ``mirror_match`` determines whether to constrain the Kabsch algorithm on matrices with a positive determinant. If ``True``, the algorithm is not constrained, resulting in a zero RMSD for mirror images. If ``False``, the algorithm is constrained, resulting in non-zero RMSD for mirror images.
        * ``allow_reorder``: If ``True``, applies coordinate permutation after aligning geometries so that the closest topologically equivalent atoms have the same indices. If ``False``, topological equivalence is still accounted for during alignment, but no permutation is applied.
        * ``inplace``: Determines whether to modify the current object (``True``) or create a new one (``False``).
        
        This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``.
        
        **NOTE:** If ``allow_reorder=True``, only those atoms will be reordered that were not ignored when topology had been constructed.
        
        .. code-block:: python
        
            >>> p[0].xyz # Simple case of a single atom
            array([[0., 0., 0.]])
            >>> p[1].xyz
            array([[1., 2., 3.]])
            >>> p.align_all_with(p[1]) # Align all conformers with the first one
            >>> p[0].xyz # First atom is aligned with the second one
            array([[1., 2., 3.]])
        """
    def as_table(self) -> dict:
        """
        Generates a dictionary where the keys are the same as the keys in the ``Confpool`` object. Each key in the dictionary is associated with a list of floating-point numbers - the values of the key for each structure in the ``Confpool``.
        
        .. code-block:: python
        
            >>> p.float_from_descr("Energy", 1)
            >>> p['length'] = lambda m: m.l(4, 15)
            >>> pd.DataFrame(p.as_table())
                length     Energy
            0    2.298683 -46.567503
            1    2.298580 -46.567316
            2    2.297140 -46.561874
            ...
        """
    def clone_subset(self, indices: list[int]) -> Confpool:
        """
        Construct a (shallow) copy of Confpool that contains only conformations with given indices in required order.
        
        .. code-block:: python
        
            >>> pnew = p.clone_subset([0, 1]) # pnew contains only two leading conformers, p is unaffected
        """
    def count(self, accept_function: typing.Callable) -> int:
        """
        Counts the number of structures in the ``Confpool`` for which the function ``f`` returns ``True``. Example usage:
        
        .. code-block:: python
        
            >>> def filter_func(m):
            ...     energy = m["Energy"]
            ...     return energy <= -46.55
            >>> len(p) # Initial num of conformations
            701
            >>> p.filter(filter_func, inplace=False)
            {'DelCount': 85, 'Object': Confpool with 616 structures and 27 atoms}
            >>> p.count(filter_func)
            616
            >>> 85+616
            701
        """
    def drop_connectivity(self) -> None:
        """
        Remove the connectivity graph from current Confpool object.
        """
    def drop_isomorphisms(self) -> None:
        """
        Delete isomorphisms from current Confpool object.
        """
    def extract_atoms(self, new_indices: list[int], inplace: bool = True) -> typing.Any:
        """
        Allows to remove some atoms from all conformations stored in ``Confpool`` and place remaining atoms in required order. A list of indices of atoms that have to stay in the Confpool has to be passed as an argument. Indexing of atoms starts from 0. If ``inplace=True``, the method modifies the current ``Confpool`` object, otherwise it returns a new ``Confpool`` object with some atoms removed. To ensure the state consistency, the following changes also happen:
        
        #. Correction of connectivity graph (removal of nodes and reindexing of the remaining ones). Previous references obtained with ``p.get_connectivity()`` method stay valid and keep older nodes and their indexing.
        #. Previously generated isomorphisms are restricted onto the new subset of atoms. Duplicate isomorphism restrictions are filtered out.
        
        .. code-block:: python
        
            p.generate_connectivity(0, mult=1.3, ignore_elements=['HCarbon'])
            interesting_atoms = [n for n in p.get_connectivity()]
            print(f"Num atoms before extraction {p.natoms}")
            p.extract_atoms(interesting_atoms)
            print(f"Num atoms after extraction {p.natoms}")
        """
    def filter(self, filter_function: typing.Callable, inplace: bool = True) -> typing.Any:
        """
        This method removes the structures from the ensemble for which the ``filter_function`` returns ``False``. If ``inplace=True``, the method modifies the ``Confpool`` object, otherwise it returns a new ``Confpool`` object with the filtered structures. The method returns the number of deleted structures if ``inplace=True``, otherwise it returns a dictionary with keys ``'Object'`` and ``'DelCount'``. The value associated with ``'Object'`` is the new Confpool object with the filtered structures, and the value associated with ``'DelCount'`` is the number of deleted structures. Example usage:
        
        .. code-block:: python
        
            >>> def filter_func(m):
            ...     energy = m["Energy"]
            ...     return energy <= -46.55
            >>> p
            Confpool with 701 structures and 27 atoms
            >>> # Remove structures with energies above -46.55 from the ensemble and return a new Confpool object
            >>> p.filter(filter_func, inplace=False)
            {'DelCount': 85, 'Object': Confpool with 616 structures and 27 atoms}
            >>> p
            Confpool with 701 structures and 27 atoms
            >>> # Remove structures with energies above -46.55 from the main ensemble inplace
            >>> p.filter(filter_func)
            85
            >>> p
            Confpool with 616 structures and 27 atoms
        """
    def float_from_descr(self, keyname: str, float_index: int) -> None:
        """
        This method creates a new key with the name `keyname` in the ``Confpool`` object, where the value of the key is set to the `i`-th floating-point number of the description of each structure. The floating-point numbers are enumerated from 1. Example usage:
        
        .. code-block:: python
        
            >>> p[0].descr
            'Energy=-1.23'
            >>> p.float_from_descr("Energy", 1)
            >>> # The number -1.23 is extracted from the description "Energy=-1.23"
            >>> p["Energy"]
            [-1.23]
        """
    def generate_connectivity(self, index: int, **kwargs) -> None:
        """
        This method generates the molecular graph based on the ``i``-th geometry of the ``Confpool`` object (geometry indexing starts from 0). Atoms are assumed to be bonded if the distance between them is less than the sum of their covalent radii multiplied by the ``mult`` factor. All atoms of elements listed in the ``ignore_elements`` parameter are excluded from the RMSD calculations. The ``ignore_elements`` parameter can take a list of element symbols such as ``'H'`` or ``'F'``. Additionally, the ``'HCarbon'`` option can be specified in the ``ignore_elements`` parameter to exclude only hydrogen atoms bonded only to carbon atoms.
        
        If the ``sdf_name`` parameter is provided, the coordinates and bonds will be written to an SDF file with that name. The ``add_bonds`` and ``remove_bonds`` parameters can be used to add or remove specific bonds, respectively, after the initial connectivity has been generated.
        
        .. code-block:: python
        
            p.generate_connectivity(0, mult=1.3, ignore_elements=['H'], sdf_name='connectivity_check.sdf')
            # or
            p.generate_connectivity(1, ignore_elements=['HCarbon'], add_bonds=[[1, 2], [3, 4]], sdf_name='connectivity_check.sdf')
        """
    def generate_isomorphisms(self, trivial: bool = False) -> int:
        """
        This method generates the automorphisms of the molecular graph obtained in the previous call of ``generate_connectivity``. It returns the number of generated automorphisms (at least 1). If the call takes too long, then your molecule is probably too symmetric and you should try re-running ``generate_connectivity`` with ``ignore_elements=['HCarbon']`` or do something else to reduce the number of symmetries.
        
        If you want to avoid the use isomorphisms to compute RMSD, just call ``generate_isomorphisms(trivial=True)`` - this creates a placeholder isomorphism ``(i -> i for i = 0, ..., p.natoms-1)`` and allows to compute RMSD for fixed atom pairing without accounting for any topological symmetry.
        
        .. code-block:: python
        
            niso = p.generate_isomorphisms()
            print(f"Number of isomorphisms generated = {niso}")
        """
    def get_connectivity(self) -> typing.Any:
        """
        Provides read-write access to a molecular graph in the ``Confpool`` object. The graph a ``networkx.Graph`` object with node attributes ``symbol`` on each atom. The returned graph is modifiable. This graph is used by ``generate_isomorphisms`` and becomes accessible only after calling ``generate_connectivity``. Also, connectivity is used when saving to SDF.
        
        .. code-block:: python
        
            # Generate molecular graph based on interatomic distances in the first conformer
            p.generate_connectivity(0, mult=1.3, ignore_elements=[])
        
            # Access the molecular graph
            molgr = p.get_connectivity()
            if not molgr.has_edge(1, 2):
                molgr.add_edge(1, 2)
        
            # Get automorphisms based on the modified molecular graph
            p.generate_isomorphisms()
        """
    def get_isomorphisms_list(self, raw: bool = False) -> list:
        """
        Get a complete list of isomorphisms in the format ``List[List[int]]``. If ``raw=False``, then each isomorphism can be directly used to map atomic indices. If ``raw=True``, then each list maps from internal indexing used for RMSD calculation (which is not the same as indexing used in XYZ file, if some elements are ignored during isomorphism calculation) to usual atomic indices. This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``.
        """
    def get_num_isomorphisms(self) -> int:
        """
        Get the number of isomorphisms of molecular graph. Can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``.
        """
    def get_rmsd_matrix(self, mirror_match: bool = True, print_status: bool = False, print_stats: bool = False) -> numpy.ndarray[numpy.float64]:
        """
        This method calculates the RMSD matrix for all pairs of structures in ``Confpool`` object. The resulting matrix is a numpy array with shape ``(p.size, p.size)``. The optional arguments are as follows:
        
        * ``mirror_match``: Whether to constrain the Kabsch algorithm to matrices with positive determinants. If ``True``, the algorithm will not constrain, resulting in a zero RMSD for mirror reflections. If ``False``, the algorithm will constrain, resulting in non-zero RMSD for mirror reflections.
        * ``print_status``: Whether to print progress updates to the console.
        * ``print_stats``: Whether to print benchmark stats at the end of calculation.
        
        Note that methods ``generate_connectivity`` and ``generate_isomorphisms`` must be called prior to RMSD calculation.
        
        .. code-block:: python
        
            my_rmsd_matrix = p.get_rmsd_matrix(mirror_match=True, print_status=False)
        """
    def include_from_file(self, filename: str) -> int:
        """
        This method loads conformers from an XYZ file into the ``Confpool`` object. The XYZ file should contain a set of conformers represented as a sequence of atoms, each with its own coordinates and optional descriptors. The number of conformers in the file is returned. Example usage:
        
        .. code-block:: python
        
            >>> p = Confpool()
            >>> p.include_from_file("structures.xyz") # Load structures from an XYZ file
            701
        """
    def include_from_xyz(self, xyz_nparray: numpy.ndarray[numpy.float64], description: str) -> None:
        """
        This method adds a new conformer to the ``Confpool`` object, with the specified coordinates and description. Example usage:
        
        .. code-block:: python
        
            >>> import numpy as np
            >>> p = Confpool()
            >>> xyz = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]) # Just some coordinates
            >>> descr = "Example structure"
            >>> p.include_from_xyz(xyz, descr)
            The object is initialized with 2 atoms and empty element symbols.
            >>> p.atom_symbols = ['H', 'C'] # Now we're good
        """
    def include_subset(self, other: Confpool, indices: list[int]) -> None:
        """
        This method adds structures from another ``Confpool`` object into the current object given a list of indices of the structures to include (starting from 0). Example:
        
        .. code-block:: python
        
            p1 = Confpool()
            p1.include_from_file("structures1.xyz")
        
            p2 = Confpool()
            p2.include_from_file("structures2.xyz")
        
            p1.include_subset(p2, [0, 1]) # Add the first two structures from p2 into p1
        """
    def lower_cutoff(self, keyname: str, cutoff: float, inplace: bool = True) -> typing.Any:
        """
        This method removes from the pool the structures for which the value of the key attribute is lower than the max value of the key attribute in the pool by more than ``cutoff``. If ``inplace`` is ``True``, the pool is modified directly and the method returns the number of structures that were removed. If ``inplace`` is ``False``, a new ``Confpool`` object is returned with the remaining structures, along with the number of structures that were removed as a dictionary.
        
        .. code-block:: python
        
            >>> print(f"min={min(p['Energy'])}, max={max(p['Energy'])}, diff={max(p['Energy'])-min(p['Energy'])}")
            min=-46.56750419, max=-46.54309456, diff=0.02440963000000096
            >>> p.lower_cutoff("Energy", 0.02)
            26
            >>> # If you wanted to extract high energy conformers for some reason ...
            >>> print(f"min={min(p['Energy'])}, max={max(p['Energy'])}, diff={max(p['Energy'])-min(p['Energy'])}")
            min=-46.56187395, max=-46.54309456, diff=0.01877938999999884
        """
    def make_centered(self, inplace: bool = True) -> typing.Any:
        """
        This method centers coordinates of all conformations in the ensemble by subtracting centroids (the mean of each coordinate). If ``inplace=True``, the ensemble is centered in-place, otherwise a new ``Confpool`` object is created and returned.
        
        .. code-block:: python
        
            >>> p[0].xyz
            array([[0., 0., 0.],
                   [1., 0., 0.]])
            >>> p.make_centered()
            >>> p[0].xyz
            array([[-0.5,  0. ,  0. ],
                   [ 0.5,  0. ,  0. ]])
        """
    def reorder_atoms(self, new_order: dict[int, int], inplace: bool = True) -> typing.Any:
        """
        Allows to reorder atoms of all conformations stored in ``Confpool``. ``new_order`` dict must contain old atom indices as keys and new atom indices as values. Atoms that do not change their index may be omitted from ``new_order``. Indexing of atoms starts from 0. If ``inplace=True``, the method modifies the current ``Confpool`` object, otherwise it returns a new ``Confpool`` object with reordered atoms. To ensure the state consistency, the following changes also happen:
        
        #. Correction of connectivity graph. Previous references obtained with ``p.get_connectivity()`` method stay valid and keep older indexing.
        #. Previously generated isomorphisms are modified to be valid with new indexing.
        
        .. code-block:: python
        
            old_order = [i for i in range(p.natoms)]
            old_atom_symbols = p.atom_symbols
            new_order = sorted(old_order,
                               key=lambda old_i: (old_atom_symbols[old_i], old_i))
            # Order atoms alphabetically and use old_i as a secondary index
            # for better agreement with earlier ordering
            p.reorder_atoms({old_i: new_i for old_i, new_i in zip(old_order, new_order)})
        """
    def rmsd_filter(self, rmsd_cutoff: float, inplace: bool = True, energy_threshold: float = 0.0, energy_key: str = '', mirror_match: bool = True, print_status: bool = False, num_threads: int = 1, **kwargs) -> dict:
        """
        This method removes duplicates from the ``Confpool`` object based on RMSD with symmetry consideration through isomorphisms. The ``rmsd_cutoff`` parameter is the threshold value of RMSD below which one of the structures will be removed. This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``.
        
        The following keyword arguments are used:
        
        #. ``mirror_match``: Determines whether to constrain the Kabsch algorithm on matrices with a positive determinant. If ``True``, the algorithm is not constrained, resulting in a zero RMSD for mirror images. If ``False``, the algorithm is constrained, resulting in non-zero RMSD for mirror images.
        #. ``energy_threshold``: The threshold value for energy difference above which two structures are considered different, regardless of RMSD. The use of ``energy_threshold`` is one of the ways to accelerate RMSD filtering.
        #. ``energy_key``: The key under which the energy is stored.
        #. ``print_status``: Determines whether to print progress to the console.
        #. ``num_threads``: Number of threads to use for parallel RMSD computation.
        #. ``inplace``: Determines whether to modify the current object (``True``) or create a new one (``False``).
        #. ``rmsd_matrix``: Avoid RMSD computations by passing precomputed RMSD matrix as ``np.ndarray``.
        
         Note that the use of energy threshold (``energy_threshold`` and ``energy_key`` kwargs) prompts ensemble sorting by this key.
        
        The returned dictionary contains the following keys:
        
        #. ``DelCount``: The number of filtered out structures.
        #. ``MinRMSD``: The smallest RMSD among all the remaining structure pairs. May be omitted if no pairs were accepted by RMSD (e.g. when energy_threshold is too small).
        #. ``MinRMSD_pairA``: The index of the first structure of the pair. May be omitted if no pairs were accepted by RMSD (e.g. when energy_threshold is too small).
        #. ``MinRMSD_pairB``: The index of the second structure of the pair. May be omitted if no pairs were accepted by RMSD (e.g. when energy_threshold is too small).
        #. ``TimeElapsed``: The time in milliseconds spent on filtering.
        #. ``NRMSDCalcs``: The number of RMSD calculations made.
        #. ``NEnergySkipped``: The number of RMSD calculations skipped due to the energy threshold.
        #. ``Object``: The ``Confpool`` object if ``inplace=False``, otherwise the key is absent.
        
        .. code-block:: python
        
            >>> p.rmsd_filter(0.2, energy_threshold=1.0 * KC2H, energy_key='Energy', print_status=True)
        """
    def save_sdf(self, filename: str, molname: str = '') -> None:
        """
        Save conformational ensemble to SDF. There are a few prerequisites:
        
        #. Topology is required for saving, so ``generate_connectivity`` must be called prior.
        #. (optional) Bond orderes must be set as a ``type`` attrs of graph edges. Use ``p.get_connectivity()`` to access the graph. The default bond type is 1 (single bonds).
        #. (optional) Atomic charges must be set using ``p.set_charges([list of charges])``.
        #. (optional) SDF format supports setting molecule name in the header, which can optionally be provided with ``molname`` keyword.
        
        .. code-block:: python
        
            p.generate_connectivity(0, mult=1.3)
            
            # This stuff is optional
            for atomA, atomB, edge_attrs in p.get_connectivity().edges(data=True):
                edge_attrs['type'] = 1 # Stands for single bond
            p.set_charges([0 for i in range(p.natoms)]) # No charged atoms
        
            p.save_sdf("my_ensemble.sdf", "my_molecule")
        """
    def save_xyz(self, filename: str) -> None:
        """
        Saves the structures and their descriptions to the file specified by ``filename``. The order of structures in the file corresponds to their sequence in the ``Confpool`` object.
        
        .. code-block:: python
        
            p.save_xyz("my_conformers.xyz")
        """
    def set_charges(self, charges_list: list[int]) -> None:
        """
        Set atomic charges based on provided list of integers. The charges are needed for the ``save_sdf`` method. 
        
        .. code-block:: python
        
            # If there are no charged atoms
            p.set_charges([0 for i in range(p.natoms)])
        """
    def sort(self, keyname: str, ascending: bool = True, inplace: bool = True) -> typing.Any:
        """
        This method sorts the ensemble based on the values of the key `keyname`. If ``ascending=True``, the ensemble is sorted in ascending order, otherwise it is sorted in descending order. If ``inplace=True``, the ensemble is sorted in-place, otherwise a new ``Confpool`` object is created and returned.
        
        .. code-block:: python
        
            # Sort the ensemble in ascending order based on the energy key
            p.sort("Energy")
        
            # Sort the ensemble in descending order based on the bond length key
            p.sort("BondLength", ascending=False)
        
            # Sort the ensemble in descending order based on the energy key and return a new Confpool object
            p_new = p.sort("Energy", ascending=False, inplace=False)
        """
    def upper_cutoff(self, keyname: str, cutoff: float, inplace: bool = True) -> typing.Any:
        """
        This method removes from the pool the structures for which the value of the ``key`` attribute is greater than the min value of the ``key`` attribute in the pool by more than ``cutoff``. If ``inplace`` is ``True``, the pool is modified directly and the method returns the number of structures that were removed. If ``inplace`` is ``False``, a new ``Confpool`` object is returned with the remaining structures, along with the number of structures that were removed as a dictionary.
        
        .. code-block:: python
        
            >>> print(f"min={min(p['Energy'])}, max={max(p['Energy'])}, diff={max(p['Energy'])-min(p['Energy'])}")
            min=-46.56750419, max=-46.54309456, diff=0.02440963000000096
            >>> p.upper_cutoff("Energy", 0.02)
            31
            >>> print(f"min={min(p['Energy'])}, max={max(p['Energy'])}, diff={max(p['Energy'])-min(p['Energy'])}")
            min=-46.56750419, max=-46.54783981, diff=0.019664380000001813
        """
    @property
    def atom_symbols(self) -> list:
        """
        Read/write element symbols of atoms. Note the convention - first letter should be uppercase and the others lowercase (this is important for retrieval of covalent radii).
        
        **Getter**: Returns the list of element symbols
        
        **Setter**: Set the list of element symbols
        
        .. code-block:: python
        
            >>> p.atom_symbols = ['H', 'C'] # Use setter
            >>> p.atom_symbols # Use getter
            ['H', 'C']
        """
    @atom_symbols.setter
    def atom_symbols(self, arg1: list) -> None:
        ...
    @property
    def descr(self) -> list:
        """
        Read/write conformer descriptions all at once.
        
        **Getter**: Returns the list of descriptions for all conformers.
        
        **Setter**: Takes a ``Callable[[MolProxy], str]`` and modifies all descriptions accordingly.
        
        .. code-block:: python
        
            >>> p.descr[:5]
            ['        -46.56750309', '        -46.56731579', '        -46.56187373', '        -46.56137046', '        -46.56126721']
            >>> p.descr = lambda m: f"New: {m.descr.lstrip()}"
            >>> p.descr[:5]
            ['New: -46.56750309', 'New: -46.56731579', 'New: -46.56187373', 'New: -46.56137046', 'New: -46.56126721']
        """
    @descr.setter
    def descr(self, arg1: typing.Callable) -> None:
        ...
    @property
    def natoms(self) -> int:
        """
        Read-only. Get the number of atoms in a single stored conformer (all conformers have the same number of atoms).
        """
    @property
    def simple_reorder(self) -> list:
        """
        Read-only. Access the mapping of atomic indices from internal indexing used in RMSD calculation and. The mapping is going to be nontrivial when some atoms are ignored from RMSD calculation (``ignore_elements`` flag of ``generate_connectivity`` method). This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``.
        """
    @property
    def size(self) -> int:
        """
        Read-only. Get the number of stored conformers as integer. Equivalent to ``len(p)``
        """
class ConfpoolIterator:
    """
    
    The class responsible for iteration over Confpool objects and their slices.
    
    .. code-block:: python
    
        >>> for mA, mB in zip(p, p[1:]) # Iterate over pairs of i-th and i+1-th conformers
        ...
    """
    def __iter__(self) -> ConfpoolIterator:
        ...
    def __next__(self) -> MolProxy:
        ...
class ConfpoolSlice:
    """
    
    The class responsible for slicing Confpool objects
    
    .. code-block:: python
    
        >>> for m in p[-1::-1]: # Iterate over all conformers in reverse order
        ...
    """
    def __iter__(self) -> ConfpoolIterator:
        ...
    def __repr__(self) -> str:
        ...
    def _expose_parent(self) -> typing.Any:
        ...
    def _get_index_list(self) -> list:
        ...
class ConfsearchInputCxx:
    def __init__(self, arg0: typing.Any) -> None:
        ...
class MolProxy:
    def __getitem__(self, arg0: typing.Any) -> float:
        ...
    def __setitem__(self, arg0: typing.Any, arg1: typing.Any) -> None:
        ...
    def align_with(self, other: MolProxy, mirror_match: bool = True, allow_reorder: bool = True) -> None:
        """
        Align the current conformation aligned with a given reference conformation ``other`` to minimize RMSD. There are 2 optional arguments:
        
        * ``mirror_match`` determines whether to constrain the Kabsch algorithm on matrices with a positive determinant. If ``True``, the algorithm is not constrained, resulting in a zero RMSD for mirror images. If ``False``, the algorithm is constrained, resulting in non-zero RMSD for mirror images.
        * ``allow_reorder``: If ``True``, applies coordinate permutation after aligning geometries so that the closest topologically equivalent atoms have the same indices. If ``False``, topological equivalence is still accounted for during alignment, but no permutation is applied.
        
        This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``.
        
        **NOTE:** If ``allow_reorder=True``, only those atoms will be reordered that were not ignored when topology had been constructed.
        
        .. code-block:: python
        
            >>> p[0].xyz # Simple case of a single atom
            array([[0., 0., 0.]])
            >>> p[1].xyz
            array([[1., 2., 3.]])
            >>> p[0].align_with(p[1])
            >>> p[0].xyz # Conformation coordinates are not affected
            array([[1., 2., 3.]])
        """
    def aligned_with(self, other: MolProxy, mirror_match: bool = True, allow_reorder: bool = True) -> numpy.ndarray[numpy.float64]:
        """
        Get the XYZ matrix of the current conformation aligned with a given reference conformation ``other`` to minimize RMSD. There are 2 optional arguments:
        
        * ``mirror_match`` determines whether to constrain the Kabsch algorithm on matrices with a positive determinant. If ``True``, the algorithm is not constrained, resulting in a zero RMSD for mirror images. If ``False``, the algorithm is constrained, resulting in non-zero RMSD for mirror images.
        * ``allow_reorder``: If ``True``, applies coordinate permutation after aligning geometries so that the closest topologically equivalent atoms have the same indices. If ``False``, topological equivalence is still accounted for during alignment, but no permutation is applied.
        
        This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``.
        
        **NOTE:** If ``allow_reorder=True``, only those atoms will be reordered that were not ignored when topology had been constructed.
        
        .. code-block:: python
        
            >>> p[0].xyz # Simple case of a single atom
            array([[0., 0., 0.]])
            >>> p[1].xyz
            array([[1., 2., 3.]])
            >>> p[0].aligned_with(p[1])
            array([[1., 2., 3.]]) # First atom is aligned with the second one
            >>> p[0].xyz # Conformation coordinates are not affected
            array([[0., 0., 0.]])
        """
    def centered(self) -> numpy.ndarray[numpy.float64]:
        """
        Computes centered coordinates of the conformation by subtracting centroid (the mean of each coordinate). The matrix of centered coordinates is returned. This method does not modify coordinates of the conformation inside the Confpool object.
        
        .. code-block:: python
        
            >>> p[0].xyz
            array([[0., 0., 0.],
                   [1., 0., 0.]])
            >>> p[0].centered()
            array([[-0.5,  0. ,  0. ],
                   [ 0.5,  0. ,  0. ]])
            >>> p[0].xyz # Actual coordinates are unaffected
            array([[0., 0., 0.],
                   [1., 0., 0.]])
        """
    def l(self, indexA: int, indexB: int) -> float:
        """
        Calculates the bond length between atoms with indices ``indexA`` and ``indexB``. The indexing of atoms starts with 1. The method returns the bond length as a float.
        
        .. code-block:: python
        
            length = p[0].l(1, 2)
            print(f"The 1-2 bond length in the first conformer is {length:.3f}")
        """
    def make_centered(self) -> None:
        """
        Centers coordinates of a single conformation by subtracting centroid (the mean of each coordinate). Modifies coordinates of the conformation inside the Confpool object.
        
        .. code-block:: python
        
            >>> p[0].xyz
            array([[0., 0., 0.],
                   [1., 0., 0.]])
            >>> p[0].make_centered()
            >>> p[0].xyz
            array([[-0.5,  0. ,  0. ],
                   [ 0.5,  0. ,  0. ]])
        """
    def rmsd(self, other: MolProxy, mirror_match: bool = True) -> tuple[float, numpy.ndarray[numpy.float64], numpy.ndarray[numpy.float64], list]:
        """
        Calculates the RMSD between the structure in the current ``MolProxy`` and the stucture in the ``other`` MolProxy object. This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``. The method returns a tuple with the following elements:
        
        * ``rmsd``: the RMSD value between the two structures as a float.
        * ``rotation_matrix``: as a 3x3 numpy array of floats, the rotation matrix for transforming the current structure for the optimal overlap with the ``other`` structure. Rotation must be done *before* translation.
        * ``translation``: translation vector (3-element numpy array of floats) that must be added to the current structure *after* rotation to align it with ``other`` structure.
        * ``reorder``: mapping of atomic indices ``{old_index: new_index}`` that must be applied to ``self`` to achieve minimal RMSD.
        
        Also, accepts one optional argument:
        
        - ``mirror_match``: a boolean flag determining whether to constrain the Kabsch algorithm on matrices with a positive determinant. If ``True``, the algorithm is not constrained, resulting in a zero RMSD for mirror refletions. If ``False``, the algorithm is constrained, resulting in a large RMSD for mirror refletions. By default, this argument is set to ``True``.
        
        .. code-block:: python
        
            # Calculate the RMSD between the two structures
            manual_rmsd, rotation, translation, reorder = p[i].rmsd(p[j])
            print(f"The RMSD between i and j is {manual_rmsd:.3f}")
        
            # Calculate the RMSD between the two structures without mirrored match constraint
            manual_rmsd, rotation, translation, reorder = p[i].rmsd(p[j], mirror_match=False)
            print(f"The RMSD between i and j is (without mirrored match constraint) is {manual_rmsd:.3f}")
        
            # Cross check by computing RMSD from optimal alignment
            i_xyz: np.ndarray = p[i].xyz[reorder][p.simple_reorder]
            j_xyz: np.ndarray = p[j].xyz[p.simple_reorder]
            i_xyz = i_xyz @ rotation
            i_xyz += translation
            differences = i_xyz - j_xyz
            reproduced_rmsd = np.sqrt(
                sum(x**2 for x in differences.flatten()) / len(p.simple_reorder))
            assert abs(manual_rmsd - reproduced_rmsd) < 1e-10
        """
    def v(self, indexA: int, indexB: int, indexC: int) -> float:
        """
        Calculates the bond angle between three atoms with indices ``indexA``, ``indexB``, and ``indexC``. The indexing of atoms starts with 1. The method returns the bond angle in degrees as a float.
        
        .. code-block:: python
        
            angle = p[0].v(1, 2, 3)
            print(f"The first conformer has bond angle between atoms 1, 2, and 3 equal to {angle:.2f} degrees")
        """
    def z(self, indexA: int, indexB: int, indexC: int, indexD: int) -> float:
        """
        Calculates the dihedral angle between four atoms with indices ``indexA``, ``indexB``, ``indexC``, and ``indexD``. The indexing of atoms starts with 1. The method returns the dihedral angle in degrees as a float.
        
        .. code-block:: python
        
            dihedral = p[0].z(1, 2, 3, 4)
            print(f"The first conformer has dihedral angle between atoms 1, 2, 3, and 4 equal to {dihedral:.2f} degrees")
        """
    @property
    def descr(self) -> str:
        """
        Read/write description of one specific conformer.
        
        **Getter**: Return the description as str.
        
        **Setter**: Takes str object and sets it as a new description.
        
        .. code-block:: python
        
            >>> p[0].descr
            '        -46.56750309'
            >>> p[0].descr = "Hi, mom!"
            >>> p[0].descr
            'Hi, mom!'
            >>> p.descr[:3]
            ['Hi, mom!', '        -46.56731579', '        -46.56187373']
        """
    @descr.setter
    def descr(self, arg1: str) -> None:
        ...
    @property
    def idx(self) -> int:
        """
        Provides read access to index of the conformers that ``MolProxy`` object refers to.
        
        .. code-block:: python
        
            >>> p[0].index
            0
        """
    @property
    def molgraph(self) -> typing.Any:
        """
        Provides read-write access to a molecular graph in the ``Confpool`` object. The graph a ``networkx.Graph`` object with node attributes ``symbol`` on each atom. The returned graph is modifiable. This graph is used by ``generate_isomorphisms`` and becomes accessible only after calling ``generate_connectivity``. Also, connectivity is used when saving to SDF.
        
        This is equivalent to calling ``p.get_connectivity()``.
        """
    @property
    def natoms(self) -> int:
        """
        Read-only. Get the number of atoms in a single stored conformer. Equivalent to ``p.natoms``.
        """
    @property
    def xyz(self) -> numpy.ndarray[numpy.float64]:
        """
        Read/write XYZ of one specific conformer.
        
        **Getter**: Return the coordinates as numpy matrix.
        
        **Setter**: Takes a np.ndarray object and sets it as new coordinates.
        
        .. code-block:: python
        
            >>> p[0].xyz
            array([[0., 0., 0.],
                   [1., 1., 1.]])
            >>> p[0].xyz = np.array([[1.0, 2.0, 3.0], [1.0, 1.0, 1.0]])
            >>> p[0].xyz
            array([[1., 2., 3.],
                   [1., 1., 1.]])
        """
    @xyz.setter
    def xyz(self, arg1: numpy.ndarray[numpy.float64]) -> None:
        ...
class Molecule:
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: Molecule) -> None:
        ...
    def _build_xyzless_input(self) -> dict:
        ...
    def _graph_constructor(self, arg0: typing.Any) -> None:
        ...
    def _require_best_sequence(self) -> None:
        ...
    def _sdf_constructor(self, arg0: str) -> None:
        ...
    def _set_fixed_dofs(self, arg0: list[tuple[int, int]]) -> None:
        ...
    def _set_requested_dofs(self, arg0: list[tuple[int, int]]) -> None:
        ...
    def apply_ps(self, check_overlaps: bool = True) -> int:
        ...
    def assign(self, arg0: Molecule) -> Molecule:
        ...
    def get_biggest_ringfrag_atoms(self) -> list:
        ...
    def get_discrete_ps(self) -> tuple:
        ...
    def get_dof_type(self, arg0: int, arg1: int) -> str:
        ...
    def get_num_flexible_rings(self) -> int:
        ...
    def get_num_rigid_rings(self) -> int:
        ...
    def get_ps(self) -> tuple:
        ...
    def get_solutions_list(self) -> list:
        ...
    def get_symbols(self) -> list:
        ...
    def get_xyz(self) -> numpy.ndarray[numpy.float64]:
        ...
    def is_ready(self) -> bool:
        ...
    def molgraph_access(self) -> typing.Any:
        ...
    def prepare_solution_iterator(self, check_overlaps: bool = True) -> int:
        ...
    def reconfigure(self, arg0: dict) -> None:
        ...
    def translate_dihedral(self, source_atoms: tuple[int, int, int, int], source_value: float, target_atoms: tuple[int, int, int, int], normalize_result: bool = True) -> float:
        ...
class Problem:
    @staticmethod
    def add_message_to_feed(arg0: str) -> None:
        ...
    @staticmethod
    def get_warning_codes() -> dict:
        ...
    def __init__(self, arg0: typing.Any, arg1: list, arg2: list, arg3: bool) -> None:
        ...
    def get_unfulfilled_requests(self) -> list:
        ...
    def recheck_method(self) -> bool:
        ...
    def record_warning(self) -> None:
        ...
    @property
    def method(self) -> int:
        ...
class SysConfsearchInputCxx:
    def __init__(self, arg0: typing.Any) -> None:
        ...
class TLCExtSolver:
    @staticmethod
    def initialize(arg0: int, arg1: dict, arg2: list, **kwargs) -> typing.Any:
        ...
    def __init__(self) -> None:
        ...
    def set_solution(self, arg0: numpy.ndarray[numpy.float64], arg1: int) -> None:
        ...
    def solve(self, arg0: list) -> int:
        ...
class TLCMain:
    def __init__(self) -> None:
        ...
    def set_solution(self, arg0: numpy.ndarray[numpy.float64], arg1: int) -> None:
        ...
    def solve(self, arg0: list, arg1: list, arg2: list) -> int:
        ...
def add_message_to_feed(arg0: str) -> None:
    ...
def clear_status_feed() -> None:
    ...
def get_radius_multiplier(arg0: str) -> float:
    ...
def get_status_feed() -> list:
    ...
def get_vdw_radii(arg0: str) -> dict:
    ...
def run_confsearch(arg0: ConfsearchInputCxx) -> typing.Any:
    ...
def set_radius_multiplier(arg0: float, arg1: str) -> None:
    ...
def set_vdw_radii(arg0: dict) -> None:
    ...
def systematic_sampling(arg0: SysConfsearchInputCxx) -> None:
    ...
address_leaks_enabled: bool = False
build_flags: str = 'ensure_performance_build=True,link_rdkit=False,enable_gperftools=False,time_profile=False,heap_profile=False,pyversion=linux-py311,use_openblas=True,use_gslcblas=False,print_checkpoints=False,mc:build_mcr=True,mc:build_mcrsmart=False,mc:build_systematic_basic=False,mc:mcr_singlethread_mode=True,mc:mcr_parallel_mode=True,mc:mcr_all_solutions=False,mc:use_rmsd_filter=True,mc:use_bfgs_postopt=False,mc:use_rdkit_postopt=False,mc:use_postopt_after_mcr=False,mc:add_mcr_library=True,mc:allow_zero_steps=True,r:unittest=False,r:use_overlap_detection_final=True,r:static_assembly=True,tlc:unittest=False,z:rmsd_using_eigen=True,z:build_shared_confpool=True,z:build_pyxyz=True,vf:use_vf3py=True,vf:basic_mode=True,mc:mcrsmart_coeffA_provided=False,mc:mcrsmart_coeffB_provided=False,r:log_flag=False,debug_flag=False,r:debug_flag=False,r:dynamic_assembly=False,tlc:log_flag=False,tlc:tlc_unittest=False,tlc:ext_unittest=False,r:weak_geom_validation=True,r:full_geom_validation=False,mc:build_any_mcr=True,r:use_overlap_detection_full=False,use_any_overlap_detection=True,z:build_classes=True,r:store_all_bondtypes=True,z:validate_rmsd_svd=False,z:rmsd_cross_validate=False,z:main_project=False,include_bfgs=False,use_eigen=True,z:build_placeholders=False,z:debug=False,z:disable_fullcheck=True,z:addess_leak_method=False,z:rmsd_using_lapack=False,z:cheat_rmsd=False,cmake_release_mode=True,cmake_debug_mode=False,enable_asan=False,o3_flag=True,ublas_nodebug=True,ndebug_flag=True'
mcr_allow_zero_steps: bool = True
use_geometry_validation: bool = True
use_mcr_parallel: bool = True
use_mcr_singlethreaded: bool = True
use_overlap_detection: bool = True
use_postoptimization: bool = False
use_pyxyz: bool = True
vf3py_enabled: bool = True
warning_codes: dict = {'COMPUTING_THREAD_EXCEPTION': 'Exception encountered in computing thread(s) during MCR', 'UNKNOWN_ELEMENT': 'Unknown element', 'FREQUENT_GEOM_FAILS': 'Frequent geometry failures', 'FREQUENT_TLC_FAILS': 'Frequent TLC failures', 'UNMET_DOF_REQUEST': 'Unfulfilled DOF request', 'NO_CONFORMERS': 'No conformers found', 'SUBOPTIMAL_SOLN_SEQ': 'Suboptimal solution sequence', 'RIGIDITY_ANALYSIS_UNRELIABLE': 'Error during regidity analysis', 'IK_NOT_APPLIED': 'IK Not Applied'}
