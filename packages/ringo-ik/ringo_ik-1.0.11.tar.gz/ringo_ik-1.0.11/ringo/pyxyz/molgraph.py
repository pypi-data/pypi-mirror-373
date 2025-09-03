import networkx as nx
import numpy as np
from copy import deepcopy
from typing import Tuple, List

from .base_load import base


class Molecule:
    """Helper class to align pairs of conformers based on translation vector and rotation matrix from :py:meth:`pyxyz.pyxyz_base.MolProxy.rmsd`
    """

    def __init__(self, start_obj: base.MolProxy) -> None:
        """Initialization from specific conformer

        Args:
            start_obj (base.MolProxy): Proxy of a conformer (``p[i]``)

        Raises:
            RuntimeError: If incorrect object is supplied
        """
        if not isinstance(start_obj, base.MolProxy):
            raise RuntimeError("Molecule should be initialized from MolProxy")

        self.G = nx.Graph(start_obj.molgraph)
        xyz = start_obj.xyz
        for i in self.G.nodes:
            self.G.nodes[i]['xyz'] = xyz[i, :]
        self.G = nx.convert_node_labels_to_integers(self.G)

    def set_orientation(self, rotation: np.ndarray, translation: np.ndarray) -> None:
        """Apply translation and rotation to a conformer. This method is expected to be used to achieve optimal alignment of two conformers.
        
        .. code-block:: python

            # Choose some pair of conformers
            structA = p[i]
            structB = p[j]

            rmsd, rotation, translation, reorder = structA.rmsd(structB) # Info needed to align structA with structB
            print(f"The pair {structA.idx}-{structB.idx} has RMSD={rmsd}")

            molA = Molecule(structA)
            molA.set_orientation(rotation, translation) # Align molA with molB to minimize RMSD
                                            # (this change does not affect structA in the main confpool object)
            molB = Molecule(structB) # molA and molB objects inherit bonding info from Confpool (p.generate_connectivity, remember?)
            total = molA + molB # Unite two molecules and their bonds in one frame

        Args:
            rotation (np.ndarray): Rotation matrix
            translation (np.ndarray): Translation vector
        """
        for node in self.G.nodes:
            self.G.nodes[node]['xyz'] = self.G.nodes[node]['xyz'] @ rotation
            self.G.nodes[node]['xyz'] += translation

    def __add__(self, other: 'Molecule') -> 'Molecule':
        """Join two conformers in the same coordinate frame.
        E.g. ``joined_geom = molA + molB``

        Args:
            other (Molecule): right-hand side ``Molecule`` object

        Returns:
            Molecule: the resuling joined geometry
        """
        res = deepcopy(other)
        n_reserve = self.G.number_of_nodes()
        mapping = {node: n_reserve + node for node in res.G.nodes}
        res.G = nx.relabel_nodes(res.G, mapping)
        res.G = nx.compose(res.G, self.G)
        return res

    def save_sdf(self, fname: str) -> None:
        """Save to SDF (including topology)

        Args:
            fname (str): file name
        """
        lines = ["", "", ""]
        lines.append("%3d%3d  0  0  0  0  0  0  0  0999 V2000" %
                     (self.G.number_of_nodes(), self.G.number_of_edges()))
        for i in range(self.G.number_of_nodes()):
            lines.append(
                "%10.4f%10.4f%10.4f%3s  0  0  0  0  0  0  0  0  0  0  0  0" %
                (self.G.nodes[i]['xyz'][0], self.G.nodes[i]['xyz'][1],
                 self.G.nodes[i]['xyz'][2], self.G.nodes[i]['symbol']))

        for edge in self.G.edges:
            lines.append("%3s%3s%3s  0" % (edge[0] + 1, edge[1] + 1, 1))
        lines.append("M  END\n")

        with open(fname, "w") as f:
            f.write("\n".join(lines))

    def as_xyz(self) -> Tuple[List[np.ndarray], List[str]]:
        """Obtain lists of coordinates and element symbols

        Returns:
            Tuple[List[np.ndarray], List[str]]: coordinates and element symbols
        """
        xyzs = []
        syms = []
        for atom in range(self.G.number_of_nodes()):
            xyzs.append(self.G.nodes[atom]['xyz'])
            syms.append(self.G.nodes[atom]['symbol'])
        return xyzs, syms

    def set_xyz(self, new_xyz: np.ndarray) -> None:
        """Update atomics coordinates. Ordering atom atoms must be the same as p[i].xyz[p.simple_reorder].

        Args:
            new_xyz (np.ndarray): Matrix Nx3 of new atomic coordinates
        """
        assert len(new_xyz.shape) == 2
        assert new_xyz.shape[0] == self.G.number_of_nodes()
        assert new_xyz.shape[1] == 3

        for i in self.G.nodes:
            self.G.nodes[i]['xyz'] = new_xyz[i, :]
