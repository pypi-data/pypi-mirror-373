import random
import copy
from functools import wraps
from typing import Callable, Optional

import numpy as np
# from icecream import ic

from .utils import (
    match_lists,
    to_abs,
    DOUBLE_THR,
)

from .. import (
    Confpool,
    base,
    H2KC,
    KC2H,
    Molecule,
)

MolProxy = base.MolProxy

PYXYZ_TESTS = {}


def test(raw_f: Callable) -> Callable:

    @wraps(raw_f)
    def f():
        # print(f"Running test {f.__name__}", flush=True)
        try:
            raw_f()
            success = True
            message = ''
        except Exception as e:
            success = False
            message = repr(e)
        return (success, message)

    # if f.__name__ == 'iterators':
    PYXYZ_TESTS[f.__name__] = f

    return f


@test
def load_hydrogen():
    p = Confpool()
    p.include_from_file(to_abs("hydrogen_atom.xyz"))
    assert p.size == len(p) == 1, "Incorrect number of conformers"
    assert p.natoms == 1, "Incorrect number of conformers"
    assert p.atom_symbols == ['H'], "Incorrect number of conformers"
    m = p[0]
    assert match_lists(
        m.xyz.tolist(),
        [[0.0, 0.0, 0.0]]), (f"{m.xyz.tolist()} vs. {[0.0,0.0,0.0]}")
    assert m.idx == 0
    assert m.natoms == 1
    assert m.descr == "Energy = -1488.228"

    p.generate_connectivity(0, mult=1.3)
    p.generate_isomorphisms()
    p.rmsd_filter(0.2)


@test
def empty_filter():
    p = Confpool()
    p.include_from_file(to_abs("aminoacid_single.xyz"))
    p.filter(lambda m: m.l(1, 19) < 2.0)
    assert p.size == 0, "Incorrect number of conformers"


def _load_ensemble():
    p = Confpool()
    p.include_from_file(to_abs("aminoacid_ensemble.xyz"))
    p["Energy"] = lambda m: float(m.descr.strip())
    p.descr = lambda m: "Conf #{}; Energy = {:9f} a.u.".format(
        m.idx + 1, m["Energy"])
    return p


@test
def description_edit():
    p = _load_ensemble()
    p.float_from_descr("Energy_check", 1)
    assert match_lists(
        p["Energy"],
        p["Energy_check"]), f'{p["Energy"]} vs.\n {p["Energy_check"]}'


@test
def filtering():
    p = _load_ensemble()
    p.upper_cutoff("Energy", 5.0 * KC2H)
    assert all(m["Energy"] < 5.0 * KC2H for m in p)
    p.filter(lambda m: m.l(1, 19) < 2.0)
    assert all(m.l(1, 19) < 2.0 for m in p)


@test
def sorting():
    p = _load_ensemble()
    p.sort("Energy")
    energies = p['Energy']
    assert all(i < j
               for i, j in zip(energies, energies[1:])), "Basic sort failed"
    p.sort("Energy", ascending=False)
    energies = p['Energy']
    assert all(
        i > j
        for i, j in zip(energies, energies[1:])), "Descending sort failed"


@test
def attrs():
    p = _load_ensemble()
    xyz = p[0].xyz
    assert all(m.idx == i for i, m in enumerate(p)), "'idx' attr failed"
    assert xyz.shape[1] == 3
    natoms_ref = xyz.shape[0]
    assert p.natoms == natoms_ref, (
        f"Confpool natoms fail: {p.natoms} (ref={natoms_ref})")
    assert p[0].natoms == natoms_ref, (
        f"MolProxy natoms fail: {p[0].natoms} (ref={natoms_ref})")
    assert all(m.descr.startswith(f"Conf #{i+1}")
               for i, m in enumerate(p)), ("'descr' attr failed")


@test
def iterators():
    p = Confpool()
    for i in range(100):
        p.include_from_xyz(np.array([[float(i), float(i), float(i)]]), '')
    # ic(p)
    # ic(p[::2].clone())
    # ic(p[-1::-1].clone())
    # raise Exception("WE GOOD")
    indices = [i for i in range(len(p))]

    check_slices = [
        None,
        slice(None, None, None),
        slice(None, None, 1),
        slice(-1, None, -1),
        slice(None, 10, None)
    ]

    def check_slice(s: Optional[slice]):
        # pnew = p[s].clone()
        # ic(pnew)
        # ic(len(pnew))
        # ic(pnew[0].xyz)
        # for m in pnew:
        #     print(int(m.xyz[0, 0]))
        # for m in p[s].clone():
        #     print(int(m.xyz[0, 0]))
        if s is None:
            ref_indices, iter = indices, p
        else:
            ref_indices, iter = indices[s], p[s]

        results = [
            [m.idx for m in iter],
            [int(m.xyz[0, 0]) for m in iter],
        ]
        # ic(results)

        if s is not None:
            results.append([int(m.xyz[0, 0]) for m in iter.clone()])

        assert all(r == ref_indices for r in results)

    for s in check_slices:
        # ic(s)
        check_slice(s)


@test
def rmsd():
    p = Confpool()
    p.include_from_file(to_abs("crest_conformersA.xyz"))
    p.include_from_file(to_abs("crest_conformersB.xyz"))
    assert len(p) == 365
    p.generate_connectivity(0,
                            mult=1.3,
                            sdf_name=to_abs('test_topology.sdf'),
                            ignore_elements=['HCarbon'],
                            add_bonds=[[13, 23]])
    p.generate_isomorphisms()

    rmsd_matrix: np.ndarray = p.get_rmsd_matrix()
    assert rmsd_matrix.shape[0] == rmsd_matrix.shape[
        1], "RMSD matrix shape fail"
    assert all((rmsd_matrix[i, i] <= DOUBLE_THR and rmsd_matrix[i, i] >= 0.0)
               for i in range(rmsd_matrix.shape[0])), (
                   "RMSD matrix nonzero diagonal fail")
    assert all(
        abs(rmsd_matrix[i, j] - rmsd_matrix[j, i]) <= DOUBLE_THR
        for i in range(rmsd_matrix.shape[0])
        for j in range(i)), ("RMSD matrix symmetry fail")

    i, j = random.randint(0, len(p) - 1), random.randint(0, len(p) - 1)
    manual_rmsd, rotation, translation, reorder = p[i].rmsd(p[j])
    # p[i].aligned_with(p[j], allow_reorder=True)
    assert abs(manual_rmsd - rmsd_matrix[i, j]) < DOUBLE_THR, (
        f"Manual {manual_rmsd} vs. matrix {rmsd_matrix[i, j]} RMSD for i={i}, j={j}"
    )

    ordered_atoms = [n for n in p.get_connectivity().nodes]
    i_xyz: np.ndarray = p[i].xyz[reorder][ordered_atoms]
    j_xyz: np.ndarray = p[j].xyz[ordered_atoms]
    i_xyz = i_xyz @ rotation
    i_xyz += translation
    diffs = i_xyz - j_xyz
    outside_rmsd = np.sqrt(
        sum(x**2 for x in diffs.flatten()) / len(ordered_atoms))
    assert abs(manual_rmsd - outside_rmsd) < DOUBLE_THR
    p.rmsd_filter(0.3, rmsd_matrix=rmsd_matrix)

    pp = Confpool()
    pp.include_from_file(to_abs("crest_conformersA.xyz"))
    pp.include_from_file(to_abs("crest_conformersB.xyz"))
    pp.generate_connectivity(0,
                             mult=1.3,
                             ignore_elements=['HCarbon'],
                             add_bonds=[[13, 23]])
    pp.generate_isomorphisms()
    pp.rmsd_filter(0.3)
    assert len(p) == len(pp), (
        f"Filtering cross check failed: {len(p)} vs. {len(pp)}")


@test
def rmsd_pair_iter():
    p = _load_ensemble()
    p.generate_connectivity(0, mult=1.3, ignore_elements=['HCarbon'])
    p.generate_isomorphisms()
    rmsd_matrix = p.get_rmsd_matrix()

    min_rmsd = 0.2
    max_rmsd = 0.25
    check_entry_count = sum(
        1 for i in range(len(p)) for j in range(i)
        if rmsd_matrix[i, j] >= min_rmsd and rmsd_matrix[i, j] <= max_rmsd)

    entry_count = sum(1
                      for _ in p.rmsd_fromto(min_rmsd, max_rmsd, rmsd_matrix))

    ascending_rmsd = [
        rmsd for _, __, rmsd in p.rmsd_fromto(min_rmsd, max_rmsd, rmsd_matrix)
    ]
    descending_rmsd = [
        rmsd for _, __, rmsd in p.rmsd_fromto(max_rmsd, min_rmsd, rmsd_matrix)
    ]

    assert ascending_rmsd == sorted(ascending_rmsd)
    assert descending_rmsd == sorted(ascending_rmsd, key=lambda x: -x)

    assert entry_count == check_entry_count, f"actual {entry_count} vs. check {check_entry_count}"


@test
def molgraph():

    def check(p):
        confA = Molecule(p[0])
        confB = Molecule(p[1])
        assert (confA.G.number_of_edges()
                != 0) and (confA.G.number_of_nodes()
                           != 0), ("Num nodes or Num edges == 0")
        a_data = (confA.G.number_of_edges(), confA.G.number_of_nodes())
        b_data = (confB.G.number_of_edges(), confB.G.number_of_nodes())
        assert a_data == b_data, f"Compare fail: {a_data} vs. {b_data}"
        gsum = confA + confB
        sum_data = (gsum.G.number_of_edges(), gsum.G.number_of_nodes())
        assert sum_data == (a_data[0] * 2, a_data[1] *
                            2), (f"Sum fail. {sum_data} vs. {a_data}")
        gsum.save_sdf(to_abs('test_sum.sdf'))

    p = _load_ensemble()
    p.generate_connectivity(0, mult=1.3)
    check(p)
    p = _load_ensemble()
    p.generate_connectivity(0, mult=1.3, ignore_elements=['HCarbon'])
    check(p)


@test
def bondtypes():
    p = _load_ensemble()
    p.generate_connectivity(0, mult=1.3)
    graph = p.get_connectivity()
    random_edge = random.choice([e for e in graph.edges])
    result_sdf = to_abs('test_bondtypes.sdf')

    def find_by_parts(*parts):
        parts = [str(i) for i in parts]
        with open(result_sdf, 'r') as f:
            lines = f.readlines()
        return any(line.replace('\n', '').split() == parts for line in lines)

    random_edge_from_one = random_edge[0] + 1, random_edge[1] + 1
    p.set_charges([0 for i in range(p.natoms)])
    p.save_sdf(result_sdf)
    assert find_by_parts(*random_edge_from_one, 1, 0, 0,
                         0), f"Failed on default bond type: {result_sdf}"
    graph[random_edge[0]][random_edge[1]]['type'] = 3
    p.save_sdf(result_sdf)
    assert find_by_parts(*random_edge_from_one, 3, 0, 0,
                         0), f"Failed on custom bond type: {result_sdf}"


@test
def make_centered():

    rand = lambda: random.uniform(-5.0, 5.0)

    def gen_p() -> Confpool:
        p = Confpool()
        for i in range(1, 10):
            p.include_from_xyz(
                np.array([
                    [0.0 + i, rand(), rand()],
                    [1.0 + i, rand(), rand()],
                ]), '')
        p.atom_symbols = ['H', 'H']
        return p

    p = gen_p()
    for m in p:
        assert np.linalg.norm(m.xyz.mean(axis=0)) > DOUBLE_THR, "1"
        xyz_c = m.centered()
        assert np.linalg.norm(xyz_c - m.xyz) > DOUBLE_THR, "2"

        m.make_centered()
        assert np.linalg.norm(m.xyz.mean(axis=0)) < DOUBLE_THR, "3"
        assert np.linalg.norm(xyz_c - m.xyz) < DOUBLE_THR, "4"

    p = gen_p()
    pnew = p.make_centered(inplace=False)
    for m in pnew:
        assert np.linalg.norm(m.xyz.mean(axis=0)) < DOUBLE_THR, "5"
    for m1, m2 in zip(p, pnew):
        assert np.linalg.norm(m1.xyz - m2.xyz) > DOUBLE_THR, "6"

    p.make_centered()
    for m1, m2 in zip(p, pnew):
        assert np.linalg.norm(m1.xyz - m2.xyz) < DOUBLE_THR, "7"


if base.address_leaks_enabled:

    @test
    def addresses():

        p = Confpool()
        p.include_from_xyz(np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ]), '')

        p_copy = copy.copy(p)
        p_deepcopy = copy.deepcopy(p)

        def common_entries(*dcts):
            if not dcts:
                return
            for i in set(dcts[0]).intersection(*dcts[1:]):
                yield (i, ) + tuple(d[i] for d in dcts)

        def check_addresses(pA, pB):
            # print(f"Leaking first", flush=True)
            p1_addrs = pA.leak_addresses()
            # print(f"Leaking second", flush=True)
            p2_addrs = pB.leak_addresses()

            errors = []
            for key, p1_value, p2_value in common_entries(p1_addrs, p2_addrs):
                if p1_value == p2_value:
                    errors.append(f"{key}(addr={p1_value})")
            message = ', '.join(errors)
            assert len(errors) == 0, (
                f"Found corrupted pointers after copying: {message}")

        # print(f"{p}, {p_copy}", flush=True)
        check_addresses(p, p_copy)
        # print(f"{p}, {p_deepcopy}", flush=True)
        check_addresses(p, p_deepcopy)


@test
def geom_analysis():
    p = Confpool()
    p.include_from_file(to_abs("geom_analysis.xyz"))
    m = p[0]
    assert match_lists([m.l(1, 2), m.l(2, 3), m.l(3, 4)],
                       [0.96, 1.67, 2.0]), "Length check failed"
    assert match_lists([m.v(1, 2, 3), m.v(2, 3, 4)],
                       [120.0, 140.0]), "Vangle check failed"
    assert abs(m.z(1, 2, 3, 4) + 50.0) < DOUBLE_THR, (
        f"Dihedral check failed: {m.z(1, 2, 3, 4)} vs. -50.0")

    init_coords = [[0.0, 0.0, 0.0], [1.0, 2.0, 3.0], [10.0, 20.0, 10.0],
                   [-1.0, -1.0, -1.0]]
    p.include_from_xyz(np.matrix(init_coords), "Test descr")
    m = p[2]
    xyz = m.xyz
    assert match_lists(xyz.tolist(), init_coords)
    xyz[0] = [-5.0, -5.0, -5.0]
    p.include_from_xyz(xyz, "Test descr2")
    assert abs(p[3].l(1, 2) - 12.206555615733702) < DOUBLE_THR
    p.generate_connectivity(0,
                            mult=1.3,
                            sdf_name=to_abs('geom_topology.sdf'),
                            ignore_elements=['HCarbon'])
    p.generate_isomorphisms()
    p.rmsd_filter(0.3)
    assert p.size == 3
