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


# Expected values verified against Nanchen, Fuhrer & Sauer (2007),
# "Determination of metabolic flux ratios from 13C-experiments and GC-MS data",
# Methods in Molecular Biology 358:177-197, Subheading 3.7 "Example 1".
#
# The worked example is the alanine (M-57)+ fragment: molecular formula
# C11H26NO2Si2, 3 backbone carbons, measured MDV = (0.6228, 0.1517, 0.0749,
# 0.1507) from ion counts (737537, 179694, 88657, 178433).

# Paper's published Ccorr,C (diagonal 0.9175) and overall Ccorr,CONHSiS
# (diagonal 0.7715). Our code returns the INVERSE; re-invert to compare.
PAPER_C_ONLY = np.array(
    [
        [0.9175, 0.0000, 0.0000, 0.0000],
        [0.0794, 0.9175, 0.0000, 0.0000],
        [0.0030, 0.0794, 0.9175, 0.0000],
        [0.0000, 0.0030, 0.0794, 0.9175],
    ]
)
PAPER_OVERALL = np.array(
    [
        [0.7715, 0.0000, 0.0000, 0.0000],
        [0.1509, 0.7715, 0.0000, 0.0000],
        [0.0672, 0.1509, 0.7715, 0.0000],
        [0.0087, 0.0672, 0.1509, 0.7715],
    ]
)
PAPER_MDV_STAR = np.array([[0.7730], [0.0372], [0.0183], [0.1715]])

# Pyruvate / citrate values are implementation snapshots (no published example
# in the paper) — they pin behaviour but not published truth.
PYRUVATE_CORR_INV = np.array(
    [
        [1.1338, 0.0000, 0.0000, 0.0000],
        [-0.1014, 1.1338, 0.0000, 0.0000],
        [-0.0388, -0.1014, 1.1338, 0.0000],
        [0.0056, -0.0388, -0.1014, 1.1338],
    ]
)


def test_alanine_c_only_matrix_matches_paper():
    # Ccorr,C only — isolate by feeding a C-only formula with backbone_c=3.
    c_only = SITA_module.LabelledCompound(
        formula="C11", labelled_element="C", backbone_c=3
    )
    pre_inverse = np.linalg.inv(c_only.correction_matrix())
    np.testing.assert_allclose(pre_inverse, PAPER_C_ONLY, atol=1e-3)


def test_alanine_overall_matrix_matches_paper():
    ala = SITA_module.LabelledCompound(
        formula="C11H26NO2Si2", labelled_element="C", backbone_c=3
    )
    pre_inverse = np.linalg.inv(ala.correction_matrix())
    np.testing.assert_allclose(pre_inverse, PAPER_OVERALL, atol=1e-3)


def test_alanine_corrected_mdv_matches_paper():
    ala = SITA_module.LabelledCompound(
        formula="C11H26NO2Si2",
        labelled_element="C",
        backbone_c=3,
        mdv_a=[0.6228, 0.1517, 0.0749, 0.1507],
    )
    np.testing.assert_allclose(ala.mdv_star(), PAPER_MDV_STAR, atol=1e-3)


def test_pyruvate_correction_matrix():
    pyr = SITA_module.LabelledCompound(
        formula="H12C6N1O3Si1", labelled_element="C", backbone_c=3
    )
    np.testing.assert_allclose(pyr.correction_matrix(), PYRUVATE_CORR_INV, atol=1e-3)


def test_citrate_shape_and_structure():
    cit = SITA_module.LabelledCompound(
        formula="H39C20O6Si3", labelled_element="C", backbone_c=6
    )
    corr = cit.correction_matrix()
    assert corr.shape == (7, 7)
    assert np.all(np.triu(corr, k=1) == 0)


def test_multi_isotope_summation():
    # Silicon has 3 isotopes (28, 29, 30). For Si2, mass shift 2 has two valid
    # combos: (28,30) and (29,29). The prior bug used only the first; with the
    # fix, both contribute. Verify a Si-only fragment produces non-zero at the
    # sub-subdiagonal (mass shift +2).
    si = SITA_module.LabelledCompound(formula="C3Si2", labelled_element="C", backbone_c=2)
    corr_inv = si.correction_matrix()
    pre = np.linalg.inv(corr_inv)
    # Expected Si contribution at mass-shift 2 = 2*c28*c30 + c29^2
    # = 2*0.92223*0.03092 + 0.04685^2 = 0.05703 + 0.00220 = 0.05923
    # (plus small C contribution for the 1 non-backbone C).
    assert pre[2, 0] > 0.05, f"sub-subdiagonal was {pre[2, 0]}; Si multi-combo not summed"


def test_mdv_star_normalised_to_one():
    ala = SITA_module.LabelledCompound(
        formula="C11H26NO2Si2",
        labelled_element="C",
        backbone_c=3,
        mdv_a=[0.6228, 0.1517, 0.0749, 0.1507],
    )
    assert abs(ala.mdv_star().sum() - 1.0) < 1e-3


def test_mdv_AA_returns_vector():
    ala = SITA_module.LabelledCompound(
        formula="C11H26NO2Si2",
        labelled_element="C",
        backbone_c=3,
        mdv_a=[0.6228, 0.1517, 0.0749, 0.1507],
    )
    aa = ala.mdv_AA(
        base_aa_formula="C11H26NO2Si2",
        base_aa_mdv=[0.6228, 0.1517, 0.0749, 0.1507],
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
    test_alanine_c_only_matrix_matches_paper,
    test_alanine_overall_matrix_matches_paper,
    test_alanine_corrected_mdv_matches_paper,
    test_pyruvate_correction_matrix,
    test_citrate_shape_and_structure,
    test_multi_isotope_summation,
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
