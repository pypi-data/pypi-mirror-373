import pytest
import numpy as np

from pysisyphus.calculators import ORCA, XTB
from pysisyphus.constants import AU2KJPERMOL, ANG2BOHR
from pysisyphus.elem_data import COVALENT_RADII as CR
from pysisyphus.drivers.afir import (
    coordinates_similar,
    decrease_distance,
    determine_target_pairs_for_geom,
    generate_random_union_ref,
    lstsqs_with_reference,
    weight_function,
    find_candidates,
    prepare_sc_afir,
)
from pysisyphus.helpers import geom_loader
from pysisyphus.init_logging import init_logging
from pysisyphus.intcoords import Stretch
from pysisyphus.intcoords.setup_fast import find_bonds
from pysisyphus.optimizers.RFOptimizer import RFOptimizer
from pysisyphus.testing import using


init_logging()


@pytest.fixture
def geom():
    geom = geom_loader("lib:claisen_scfafir_paper_ref_opt.xyz")
    return geom


def test_weight_func():
    atoms = ("H", "H")
    cr_h = CR["h"]
    r_hh = 2 * cr_h
    coords3d = np.zeros((2, 3))
    coords3d[1, 2] = r_hh

    omega = weight_function(atoms, coords3d, 0, 1)
    assert omega == pytest.approx(1.0)


@pytest.mark.parametrize(
    "center, ref_candidates",
    (
        (5, (8, 7, 0)),
        (4, (12, 13, 3)),
        (0, (6, 1, 5)),
    ),
)
def test_find_candidates(center, ref_candidates, geom):
    bond_sets = [set(bond) for bond in find_bonds(geom.atoms, geom.coords3d).tolist()]
    candidates = find_candidates(center, bond_sets)
    assert set(candidates) == set(ref_candidates)


def test_least_squares_opt(geom):
    m, n = 4, 5
    bond = Stretch((m, n))
    ref_dist = bond.calculate(geom.coords3d)
    # 5.12 Å as in the SC-AFIR paper
    assert ref_dist == pytest.approx(5.118688 * ANG2BOHR)

    frac = 0.9  # decrease by 10%
    tmp_coords3d = decrease_distance(geom.coords3d, m, n, frac=frac)
    # geom.jmol(cart_coords=tmp_coords3d.flatten())
    tmp_dist = bond.calculate(tmp_coords3d)
    assert tmp_dist == pytest.approx(frac * ref_dist)
    # CC-bond will be compressed
    comp_bond = Stretch((5, 0))  # this bond will be compressed
    comp_dist = comp_bond.calculate(tmp_coords3d)
    assert comp_dist == pytest.approx(1.0928863 * ANG2BOHR)

    # Formerly compressed CC-bond-length will be partially "restored" again,
    # by the least-squares optimization.
    _, opt_coords3d = lstsqs_with_reference(tmp_coords3d, geom.coords3d, (m, n))
    opt_dist = bond.calculate(opt_coords3d)
    assert opt_dist == pytest.approx(tmp_dist)
    # geom.jmol(cart_coords=opt_coords3d.flatten())
    comp_dist = comp_bond.calculate(opt_coords3d)
    assert comp_dist == pytest.approx(1.30461 * ANG2BOHR)


@pytest.mark.parametrize(
    "calc_cls, calc_kwargs, ref_cc_dist, ref_oc_dist",
    (
        # Skip ORCA in the CI, as it takes quite some time
        pytest.param(
            ORCA,
            {"keywords": "b3lyp/G 6-31G tightscf", "pal": 6},
            1.46768 * ANG2BOHR,
            4.67404 * ANG2BOHR,
            marks=(using("orca"), pytest.mark.skip_ci),
        ),
        pytest.param(
            XTB,
            {"pal": 1},
            2.76345,
            8.532,
            marks=(using("xtb"), pytest.mark.skip_ci),
        ),
    ),
)
def test_sc_afir_claisen(calc_cls, calc_kwargs, ref_cc_dist, ref_oc_dist, geom):
    geom = geom.copy(coord_type="redund")
    m, n = 4, 5
    afir_kwargs = {"gamma": 200 / AU2KJPERMOL}

    def calc_getter():
        calc = calc_cls(**calc_kwargs)
        return calc

    geom, _afir_kwargs, broken_bonds, _ = prepare_sc_afir(geom, m, n)
    afir_kwargs.update(_afir_kwargs)

    calc = calc_getter()
    from pysisyphus.calculators import AFIR
    afir_calc = AFIR(calc, **afir_kwargs)
    geom.set_calculator(afir_calc)

    opt_kwargs = {
        "dump": True,
        "thresh": "gau",
        "hessian_init": "calc",
        "hessian_recalc": 50,
        "trust_max": 0.2,
        "fragments": afir_calc.fragment_indices,
        "monitor_frag_dists": 5,
    }
    opt = RFOptimizer(geom, **opt_kwargs)
    opt.run()

    def assert_dist(i, j, ref_dist):
        dist = Stretch([i, j]).calculate(geom.coords3d)
        print(dist, dist / ANG2BOHR)
        assert dist == pytest.approx(ref_dist, abs=2e-2)

    assert_dist(m, n, ref_cc_dist)
    assert_dist(1, 2, ref_oc_dist)


@pytest.mark.parametrize(
    "ref_coords3d, ref_return",
    (
        (
            [
                geom_loader("lib:claisen_scfafir_paper_ref_opt.xyz").coords3d,
            ],
            (True, 0),
        ),
        ([], (False, -1)),
    ),
)
def test_coordinates_similar(ref_coords3d, ref_return):
    test_coords3d = geom_loader("lib:claisen_scfafir_paper_ref_opt.xyz").coords3d
    return_ = coordinates_similar(test_coords3d, ref_coords3d)
    assert return_ == ref_return


def test_determine_target_pairs(geom):
    target_pairs = determine_target_pairs_for_geom(geom, min_=1.25, max_=5.0)
    assert len(target_pairs) == 64


def test_random_union():
    geom = geom_loader("lib:h2o.xyz")
    n = 5
    geoms = [geom] * n
    union = generate_random_union_ref(geoms)
    assert len(union.atoms) == n * len(geom.atoms)
