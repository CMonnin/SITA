import logging
import sys
import numpy as np
import SITA_module

logger = logging.getLogger("logger")
logger.propagate = False
logger.setLevel(logging.INFO)
test_console_handler = logging.StreamHandler(sys.stdout)

# setting up formating for the handlers
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
quiet_formatter = logging.Formatter("%(message)s")
test_console_handler.setFormatter(quiet_formatter)
if logger.handlers:
    print(logger.handlers)
# adding the handlers to the logger
if not logger.handlers:
    logger.addHandler(test_console_handler)


def main():
    alanine_M_57 = SITA_module.LabelledCompound(
        formula="C8H23NO2Si2",
        labelled_element="C",
        backbone_c=3,
        mdv_a=[0.6628, 0.1517, 0.0749, 0.1507],
    )
    pyruvate_M_57 = SITA_module.LabelledCompound(
        formula="H12C6N1O3Si1", labelled_element="C", backbone_c=3
    )
    citrate_M_57 = SITA_module.LabelledCompound(
        formula="H39C20O6Si3", labelled_element="C", backbone_c=6
    )
    alanine_M_57_2 = SITA_module.LabelledCompound(
        formula="C8H23NO1Si2",
        labelled_element="C",
        backbone_c=4,
        mdv_a=[0.3711, 0.3211, 0.2348, 0.0561, 0.0169],
    )

    pyruvate_M_57.correction_matrix()

    # Regression: backbone_c = total C should collapse the C-channel to identity,
    # so the correction only reflects H/N/O/Si natural abundance.
    all_backbone = SITA_module.LabelledCompound(
        formula="C3H7NO2", labelled_element="C", backbone_c=3
    )
    corr = all_backbone.correction_matrix()
    assert corr.shape == (4, 4), corr.shape

    # Alanine M-57 (C8H23NO2Si2) corrected MDV with backbone_c=3.
    corrected = alanine_M_57.mdv_star().flatten()
    assert corrected.size == 4
    # Mass balance: corrected MDV must sum to 1 (normalised in mdv_star).
    assert abs(corrected.sum() - 1.0) < 1e-3, corrected.sum()

    # Unlabeled-biomass correction should return a vector (was previously a scalar crash).
    aa = alanine_M_57.mdv_AA(
        base_aa_formula="C8H23NO2Si2",
        base_aa_mdv=[0.6628, 0.1517, 0.0749, 0.1507],
        base_aa_backbone_c=3,
    )
    assert aa.shape == (4, 1), aa.shape


if __name__ == "__main__":
    logger.debug("running test")
    main()
