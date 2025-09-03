import os
import sys
import numpy as np
from typing import Generator, Tuple

from ..cpppart import cpppart as base
from ..cpppart.cpppart import Confpool, MolProxy

try:
    from sage.all import *
    sage_available = True
except ImportError:

    class PermutationGroup:
        """Placeholder class for SageMath's ``PermutationGroup``.
        It's generated if SageMath failed to import.
        """

    sage_available = False


def _rmsd_interval(
    self, start_rmsd: float, end_rmsd: float, matr: np.ndarray
) -> Generator[Tuple[base.MolProxy, base.MolProxy, float], None, None]:
    """Iterate over all pairs of conformers whose RMSD fits a given range [start_rmsd, end_rmsd].
    If start_rmsd < end_rmsd, then conformers are yielded in the order of increasing RMSD. Otherwise, in the order of decreasing RMSD.

    Args:
        start_rmsd (float): start of RMSD range for iteration
        end_rmsd (float): end of RMSD range for iteration
        matr (np.ndarray): RMSD matrix

    Yields:
        Generator[Tuple[base.MolProxy, base.MolProxy, float], None, None]: Generator of conformer pairs with respective RMSD values
    """
    min_rmsd = min(start_rmsd, end_rmsd)
    max_rmsd = max(start_rmsd, end_rmsd)
    ascending = 1 if start_rmsd < end_rmsd else -1
    assert matr.ndim == 2
    assert matr.shape[0] == len(self) and matr.shape[1] == len(self)

    df = {'molA': [], 'molB': [], 'rmsd': []}
    for i in range(matr.shape[0]):
        for j in range(i):
            if matr[i, j] > min_rmsd and matr[i, j] < max_rmsd:
                df['molA'].append(i)
                df['molB'].append(j)
                df['rmsd'].append(matr[i, j])

    df['molA'], df['molB'], df['rmsd'] = zip(
        *sorted(zip(df['molA'], df['molB'], df['rmsd']),
                key=lambda x: ascending * x[2]))

    for indexA, indexB, rmsd in zip(df['molA'], df['molB'], df['rmsd']):
        yield self[indexA], self[indexB], float(rmsd)


base.Confpool.rmsd_fromto = _rmsd_interval


def _clone_slice(self: base.ConfpoolSlice) -> base.Confpool:
    """Generate a copy of the original Confpool object that contains only conformations of the slice.

    .. code-block:: python

        >>> p[::2].clone().save_xyz("even_conformations.xyz") # Save conformations with even indices

    Returns:
        Confpool: the resulting Confpool (shallow copy, i.e. references the same topology graph)
    """
    p = self._expose_parent()
    indices = self._get_index_list()
    res_p = p.clone_subset(indices)
    return res_p


base.ConfpoolSlice.clone = _clone_slice


def _get_isomsgroup(self: base.Confpool) -> PermutationGroup:
    """Builds a PermutationGroup of molecular graph isomorphisms. This method can be used only after calling ``generate_connectivity`` and ``generate_isomorphisms``. Indexing of atoms starts in the resulting PermutationGroup starts from 1 as per agreement used in SageMath.
    
    Requires SageMath to be installed.
    """
    assert sage_available, "Cannot import SageMath. Is it installed?"
    return PermutationGroup(self.get_isomorphisms_list(),
                            domain=[i for i in range(self.natoms)])


base.Confpool.get_isomorphisms_group = _get_isomsgroup


def _repr_isomsgroup(self, group: PermutationGroup) -> str:
    """Build a concise human-readable analysis of PermutationGroup used to represent isomorphism group of the molecule.
    Indexing of atoms starts in the resulting PermutationGroup starts from 1 as per agreement used in SageMath.
    
    Requires SageMath to be installed.

    Args:
        group (PermutationGroup): SageMath object for isomorphisms group built with ``get_isomorphisms_group`` method
    
    .. code-block:: python

        G = p.get_isomorphisms_group()
        print(p.repr_isomorphisms_group(G))
    """
    assert sage_available, "Cannot import SageMath. Is it installed?"
    G = group
    generators = G.gens_small()
    generators_str = (
        f"The group has {len(G)} elements and {len(generators)} generators:\n"
        + "\n".join(f"{i}. {g.cycle_string()}"
                    for i, g in enumerate(generators, start=1)))

    sage_perms = self.get_isomorphisms_list()

    dirprod_decomposition_lines = []
    num_fixed = 0
    num_nontrivial = 0
    for subg_indices in G.disjoint_direct_product_decomposition():
        if len(subg_indices) == 1:
            num_fixed += 1
            continue
        else:
            num_nontrivial += 1

        isom_restrictions = [[isom[i] for i in subg_indices]
                             for isom in sage_perms]

        subg_indices_list = list(subg_indices)
        H = PermutationGroup(isom_restrictions, domain=subg_indices_list)
        gens = H.gens_small()
        dirprod_decomposition_lines.append(
            f"{num_nontrivial}. {len(H)} elements acting on atoms {subg_indices_list}. {len(gens)} generators: {gens}"
        )

    dirprod_decomposition = [
        f"The group has {num_fixed} fixed atoms and it is a direct product of the following:",
        *dirprod_decomposition_lines
    ]
    dirprod_decomposition_str = '\n'.join(dirprod_decomposition)

    return '\n'.join([generators_str, dirprod_decomposition_str])


base.Confpool.repr_isomorphisms_group = _repr_isomsgroup
