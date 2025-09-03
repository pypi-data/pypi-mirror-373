import random
import time
import math
import os
import multiprocessing

from functools import wraps
from typing import Callable

import numpy as np

from .utils import (
    match_lists,
    to_abs,
    DOUBLE_THR,
    SkipTestWarning,
)

from .. import (
    Molecule,
    Confpool,
    base,
    run_confsearch,
    get_molecule_statistics,
    ConfsearchInput,
    TerminationConditions,
    SysConfsearchInput,
    systematic_sampling,
)

if base.use_pyxyz:
    from .. import Confpool

RINGO_TESTS = {}


def test(raw_f: Callable, name=None) -> Callable:

    @wraps(raw_f)
    def f():
        try:
            raw_f()
            success = True
            message = ''
        except SkipTestWarning as e:
            success = True
            message = "Skipped"
        except Exception as e:
            success = False
            message = repr(e)
        return (success, message)

    RINGO_TESTS[f.__name__ if name is None else name] = f
    return f


@test
def manual_dofs():
    mol = Molecule.from_sdf(to_abs('pdb1GHG.sdf'))
    dofs_list, dofs_values = mol.get_ps()
    ddofs_list, ddofs_values = mol.get_discrete_ps()
    while True:
        for i in range(len(dofs_list)):
            newvalue = random.uniform(-math.pi, math.pi)
            dofs_values[i] = newvalue

        for i in range(len(ddofs_list)):
            ddofs_values[i] = -1  # -1 requests for random solution of IK

        result = mol.apply_ps()

        if result == 0:
            symbols = mol.get_symbols()
            coords = mol.get_xyz()
            assert len(symbols) == coords.shape[0]
            break


@test
def mol_stats():
    mol = Molecule.from_sdf(to_abs('pdb1GHG.sdf'))
    res = get_molecule_statistics(mol)
    assert all(key in res
               for key in ('composition', 'num_atoms', 'num_heavy_atoms',
                           'num_bonds', 'num_rotatable_bonds',
                           'num_cyclic_rotatable_bonds',
                           'largest_macrocycle_size', 'n_flexible_rings',
                           'n_rigid_rings', 'num_dofs', 'num_cyclic_dofs',
                           'cyclomatic_number', 'num_cyclic_parts'))


@test
def all_solutions():
    mol = Molecule.from_sdf(to_abs('pdb1GHG.sdf'))
    dofs_list, dofs_values = mol.get_ps()
    ddofs_list, ddofs_values = mol.get_discrete_ps()
    while True:
        for i in range(len(dofs_list)):
            newvalue = random.uniform(-math.pi, math.pi)
            dofs_values[i] = newvalue

        result = mol.prepare_solution_iterator()
        if result != 0:
            continue

        sol_list = mol.get_solutions_list()
        if len(sol_list) > 2:
            break


def gen_sampling(parallel: bool):

    def f():
        if parallel and not (base.use_mcr_parallel and base.use_pyxyz):
            raise SkipTestWarning("PyXYZ or MCR are disabled in this build")
        elif not parallel and not (base.use_mcr_parallel and base.use_pyxyz):
            raise SkipTestWarning("PyXYZ or MCR are disabled in this build")

        mol = Molecule.from_sdf(to_abs('pdb1GHG.sdf'))
        p = Confpool()

        nthreads = 1 if not parallel else min(multiprocessing.cpu_count(), 8)

        cs_settings = ConfsearchInput(
            molecule=mol,
            pool=p,
            termination_conditions=TerminationConditions(timelimit=10),
            rmsd_settings='default',
            geometry_validation={
                "ringo": {
                    "bondlength": 0.05,
                    "valence": 3.0,
                    "dihedral": 3.0,
                }
            },
            nthreads=nthreads,
        )
        run_confsearch(cs_settings)
        assert p.size > 0, "No conformers, that's sus"

    return f


@test
def test_systematic_sampling():
    mol = Molecule.from_sdf(to_abs('pdb7UPJ.sdf'))
    p = Confpool()

    cs_settings = SysConfsearchInput(
        molecule=mol,
        pool=p,
        rmsd_settings='default',
        default_dihedrals=[-60.0, 60.0],
        custom_preferences={},
        clear_feed=False,
        show_status=True,
        nthreads=1,
    )

    systematic_sampling(cs_settings)
    assert len(p) == 700


test(gen_sampling(parallel=False), name='sampling_singlethread')
test(gen_sampling(parallel=True), name='sampling_parallel')
