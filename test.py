import logging
import sys

import SITA_module

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)

# setting up formating for the handlers
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
quiet_formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(quiet_formatter)

# adding the handlers to the logger
logger.addHandler(console_handler)


#
def main():
    test_instance = SITA_module.Labelled_compound(
        formula="C8H23NO2Si2",
        labelled_element="C",
        mdv_a=[0.6628, 0.1517, 0.0749, 0.1507],
    )
    test_instance.correction_matrix()
    test_instance.mdv_star()

    logger.debug(f"class vars:{vars(test_instance)}")
    # print(dir(test_instamdv_starnce))pass


if __name__ == "__main__":
    logger.debug("running test")
    main()
