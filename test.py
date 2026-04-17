import logging
import sys

import numpy as np

import SITA_module

logger = logging.getLogger("logger")
logger.propagate = False
logger.setLevel(logging.WARNING)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


# Expected correction matrices and corrected MDVs are snapshotted from the
# implementation after the Fischer/Zamboni backbone-C fix. The C channel uses
# (total_C - backbone_c) atoms; all H/N/O/Si contribute at natural abundance.
# Tolerance 1e-3 accounts for the 4-decimal rounding in correction_matrix().

ALANINE_CORR = np.array(
    [
        [1.2547, 0.0, 0.0, 0.0],
        [-0.2041, 1.2547, 0.0, 0.0],
        [-0.0658, -0.2041, 1.2547, 0.0],
        [0.0163, -0.0658, -0.2041, 1.2547],
    ]
)
ALANINE_MDV_STAR = np.array([[0.7695], [0.0510], [0.0180], [0.1616]])

PYRUVATE_CORR = np.array(
    [
        [1.1339, 0.0, 0.0, 0.0],
        [-0.1014, 1.1339, 0.0, 0.0],
        [-0.0387, -0.1014, 1.1339, 0.0],
        [0.0056, -0.0387, -0.1014, 1.1339],
    ]
)

CITRATE_CORR_DIAG = 1.5107
CITRATE_CORR_SUBDIAG = -0.4691


def test_alanine_backbone_correction():
    ala = SITA_module.LabelledCompound(
        formula="C8H23NO2Si2",
        labelled_element="C",
        backbone_c=3,
        mdv_a=[0.6628, 0.1517, 0.0749, 0.1507],
    )
    np.testing.assert_allclose(ala.correction_matrix(), ALANINE_CORR, atol=1e-3)
    np.testing.assert_allclose(ala.mdv_star(), ALANINE_MDV_STAR, atol=1e-3)


def test_pyruvate_backbone_correction():
    pyr = SITA_module.LabelledCompound(
        formula="H12C6N1O3Si1", labelled_element="C", backbone_c=3
    )
    np.testing.assert_allclose(pyr.correction_matrix(), PYRUVATE_CORR, atol=1e-3)


def test_citrate_shape_and_structure():
    cit = SITA_module.LabelledCompound(
        formula="H39C20O6Si3", labelled_element="C", backbone_c=6
    )
    corr = cit.correction_matrix()
    assert corr.shape == (7, 7)
    # Lower-triangular: upper triangle must be zero.
    assert np.all(np.triu(corr, k=1) == 0)
    # Pin the top-left structure — diagonal and subdiagonal are sensitive to
    # whether the backbone C exclusion is applied correctly.
    assert abs(corr[0, 0] - CITRATE_CORR_DIAG) < 1e-3
    assert abs(corr[1, 0] - CITRATE_CORR_SUBDIAG) < 1e-3


def test_backbone_equals_total_collapses_c_channel():
    # When every C is a backbone C, the C contribution is identity. The
    # correction then depends only on H/N/O natural abundance.
    with_c = SITA_module.LabelledCompound(
        formula="C3H7NO2", labelled_element="C", backbone_c=3
    ).correction_matrix()
    # Construct the non-C equivalent by making backbone_c absorb all C.
    # (C3 with backbone_c=3 → effective C count = 0 → C skipped.)
    # Sanity: result must still be lower-triangular and diagonal > 1 (H/N/O correct).
    assert with_c.shape == (4, 4)
    assert np.all(np.triu(with_c, k=1) == 0)
    assert with_c[0, 0] > 1.0


def test_mdv_star_normalised_to_one():
    ala = SITA_module.LabelledCompound(
        formula="C8H23NO2Si2",
        labelled_element="C",
        backbone_c=3,
        mdv_a=[0.6628, 0.1517, 0.0749, 0.1507],
    )
    assert abs(ala.mdv_star().sum() - 1.0) < 1e-3


def test_mdv_AA_returns_vector():
    # Previously crashed: np.dot(scalar - vector, vector) gave a scalar.
    ala = SITA_module.LabelledCompound(
        formula="C8H23NO2Si2",
        labelled_element="C",
        backbone_c=3,
        mdv_a=[0.6628, 0.1517, 0.0749, 0.1507],
    )
    aa = ala.mdv_AA(
        base_aa_formula="C8H23NO2Si2",
        base_aa_mdv=[0.6628, 0.1517, 0.0749, 0.1507],
        base_aa_backbone_c=3,
    )
    assert aa.shape == (4, 1)


def test_backbone_c_required():
    try:
        SITA_module.LabelledCompound(formula="C3H7NO2", labelled_element="C", backbone_c=None)
    except ValueError:
        return
    raise AssertionError("expected ValueError when backbone_c is None")


def test_backbone_c_exceeds_formula():
    try:
        SITA_module.LabelledCompound(formula="C3H7NO2", labelled_element="C", backbone_c=4)
    except ValueError:
        return
    raise AssertionError("expected ValueError when backbone_c > total C in formula")


def test_vector_size_exceeds_backbone():
    try:
        SITA_module.LabelledCompound(
            formula="C3H7NO2", labelled_element="C", backbone_c=3, vector_size=5
        )
    except ValueError:
        return
    raise AssertionError("expected ValueError when vector_size > backbone_c + 1")


TESTS = [
    test_alanine_backbone_correction,
    test_pyruvate_backbone_correction,
    test_citrate_shape_and_structure,
    test_backbone_equals_total_collapses_c_channel,
    test_mdv_star_normalised_to_one,
    test_mdv_AA_returns_vector,
    test_backbone_c_required,
    test_backbone_c_exceeds_formula,
    test_vector_size_exceeds_backbone,
]


def main():
    failures = 0
    for fn in TESTS:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as e:
            failures += 1
            print(f"FAIL  {fn.__name__}: {e}")
    if failures:
        sys.exit(1)
    print(f"\n{len(TESTS)} passed")


if __name__ == "__main__":
    main()
