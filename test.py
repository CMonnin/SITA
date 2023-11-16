import logging
import sys
import numpy as np
import SITA_module

logger = logging.getLogger("logger")
logger.propagate = False
logger.setLevel(logging.DEBUG)
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


#
def main():
    alanine_M_57 = SITA_module.Labelled_compound(
        formula="C8H23NO2Si2",
        labelled_element="C",
        mdv_a=[0.6628, 0.1517, 0.0749, 0.1507],
    )
    pyruvate_M_57 = SITA_module.Labelled_compound(
        formula="H12C6N1O3Si1", labelled_element="C", vector_size=4
    )
    citrate_M_57 = SITA_module.Labelled_compound(
        formula="H39C20O6Si3", labelled_element="C", vector_size=7
    )
    pyruvate_M_57.correction_matrix(save_to_text=True)
    # pyruvate_M_57.mdv_star()
    # np.savetxt(citrate_M_57.correction_matrix(), ",")
    # logger.debug(f"class vars:{vars(citrate_M_57)}")
    # print(dir(test_instamdv_starnce))pass


if __name__ == "__main__":
    logger.debug("running test")
    main()
