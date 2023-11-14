import itertools
import logging
import math
import re
import sys
from collections import Counter

import numpy as np

# ------------------------------------------------------
# setting up a logger to print to std out and to a file
# creating logger and handlers
logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("log.log")

# setting up formating for the handlers
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
quiet_formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(quiet_formatter)

# adding the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
# -------------------------------------------------------
# correction of natural abundance
# MDV_star = Corr^-1 dot MDVa
# MDV_star: Corrected Istopic Mass Distribution Vector
# Corr^-1: Inverse of correction matrix
# MDVa = Experimentally measured Mass distrubtion vector normalised to 1
# ----------------------------------------------------------------------
# TODO adducts Ca, Na, NH4, FA, AA, Li,
# TODO: correct for contribtuion by unalblled mass
# -----------------------------------------------------------------------
# dict of the natural abundance of common elements
# Source:
# Coursey, J. S., et al. "Atomic weights and isotopic compositions with
# relative atomic masses." NIST Physical Measurement Laboratory (2015).
# https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl Added some additional isotopes at 0% abundnace for ease of logic later on
ISOTOPE_ABUNDANCE_DICT_UNIT_MASS = {
    "H": {"abundance": (0.999885, 0.000115), "mass": (1, 2)},
    "C": {"abundance": (0.9893, 0.0107), "mass": (12, 13)},
    "N": {"abundance": (0.99636, 0.00364), "mass": (14, 15)},
    "O": {"abundance": (0.99757, 0.00038, 0.00205), "mass": (16, 17, 18)},
    "Si": {"abundance": (0.92223, 0.04685, 0.03092), "mass": (28, 29, 30)},
    "P": {"abundance": (1), "mass": (31)},
    "S": {
        "abundance": (0.9499, 0.0075, 0.0425, 0, 0.0001),
        "mass": (32, 33, 34, 35, 36),
    },
    "Cl": {"abundance": (0.7576, 0, 0.2424), "mass": (35, 36, 37)},
    "Br": {"abundance": (0.5069, 0, 0.4931), "mass": (79, 80, 81)},
}


class Labelled_compound:
    def __init__(self, formula: str, labelled_element: str, mdv_a: list):
        """
        Each compound will have a molecular formula and
        one labelled element
        The vector_size will be required as an argument.
        This will define how big the matrix will be.
        Eg if you see M+0, M+1, M+2, the vector_size will be 3
        Parameters
        ----------
        formula = the chemical formula of the compound or fragment
        labelled_element = which element is lablled (currently only supports one labelled_element)
        mdv_a = a list of numbers corresponding to the observed ratio of isotopes, the sum
        of these ratios needs to equal 1.
        """
        if not isinstance(mdv_a, list):
            numbers = re.split(r",\s*", mdv_a)
            float_numbers = [float(num) for num in numbers]
            self.mdv_a = np.array(float_numbers)
        else:
            self.mdv_a = np.array(mdv_a)

        self.formula = formula
        self.labelled_element = labelled_element
        # convert to a vector and reshape it into a horizontal vector
        self.mdv_a = self.mdv_a.reshape(-1, 1)
        self.vector_size = self.mdv_a.size
        self.formula_dict = self.formula_parser()
        # adding error handling here if vector_size is greater than
        # the number of lablled elements eg vecto_size of 4 when
        # alanine only has 3 carbons

    def matrix_generator(self):
        # generate an empty matrix of appropriate size
        return np.zeros((self.vector_size, self.vector_size))

    def formula_parser(self):
        """
        This function parses the molecular formula
        """
        formula = self.formula
        # Make two capture groups:
        # 1st one upper case letter lower case letter,
        # 2nd group the digits following the 1st group
        pattern = r"([A-Z][a-z]*)(\d*)"
        groups = re.findall(pattern, formula)
        # creating a dict of hashable objects, the elements and their counts
        elements = Counter()

        for element, count in groups:
            # if count is empty e.g. mol formula: CO, assume 1
            if count == "":
                count = 1
            else:
                count = int(count)

            elements[element] += count

        logger.debug(f" parsed formula: {elements}")
        return elements

    def combo_solver(self, element_ID: str) -> list:
        # figures out all the combinations depening on the
        # number of atoms and isotpes of an element
        # eg for the carbon in alanine C3H7NO2 there will be two isotopes
        # and three carbons

        number_of_atoms = self.formula_dict[element_ID]
        number_of_isotopes = len(
            ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[element_ID]["abundance"]
        )
        combinations = itertools.combinations_with_replacement(
            range(number_of_isotopes), number_of_atoms
        )
        return list(combinations)

    def valid_combos(self, target: int, combinations: list) -> list | None:
        # a valid combo being one that sums up to the target eg M+0 has a sum
        # of 0, M+1 a sum of 1 etc ...
        # TODO needs to somehow deal with multiple tuples (i think)
        valid_combos = [combo for combo in combinations if sum(combo) == target]
        if valid_combos:
            combo_list = list(valid_combos[0])
            logger.debug(f"combo_list: {combo_list}")
            isotope_counter = Counter(combo_list)
            logger.debug(f"valid_combo: {isotope_counter}")
            return combo_list
        else:
            logger.debug(f"No combinations")
            return None

    def abundnace_solver(self, combinations: Counter, element_ID: str):
        # will take the combination and convert it to the abundance to then populate
        # the matrix

        # determine the number of atoms from the chem formula
        # for a specific element
        # eg in C3H7NO2 for 'C' this will be 3
        number_of_atoms = self.formula_dict[element_ID]
        # the isotope counter will determine the values for the
        # equations eg #istope_1 ...
        # eg for M+1 in alanine considering carbon
        # (0,0,1) will be passed as the combination
        # and will result in a counter (0:2,1:1)
        isotope_counter = Counter(combinations)
        logger.debug(isotope_counter)
        # the full eqn is Cij = (# element)! * [(abundance_1)^#isotope_1/(#isotope_1)!]*
        # [(abundance_2)^#isotope_2/(#isotope_2)!]*...
        abundance = math.factorial(number_of_atoms)
        # the key will be the isotope ID eg 0 -> 016, 1 -> 017, 2-> 018
        # value will be the abundance
        for key, value in isotope_counter.items():
            abundance = (
                abundance
                * ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[element_ID]["abundance"][key]
                ** value
                / math.factorial(value)
            )

        return abundance

    def matrix_populator(self, element_ID: str):
        """this will take an istope and generate all the possible combinations
        that can occur depending on the number of atoms present in the compound
        practically only a subset will be used to populate the matrix which is
        dependant on the size of the matrix
        this might have to be changed. I don't know how much of performance hit
        it will cause.
        """

        # get the combos for the element
        combos = self.combo_solver(element_ID)
        # create an empty matrix
        element_matrix = self.matrix_generator()

        for i in range(self.vector_size):
            for j in range(self.vector_size):
                if j - i == 0:
                    # get a list of valid combos for this location
                    combinations = self.valid_combos(target=0, combinations=combos)
                    if combinations:
                        element_matrix[i, j] = self.abundnace_solver(
                            combinations, element_ID
                        )
                if j - i < 0:
                    # here this is supposed to remain 0
                    element_matrix[i, j] = 0

                else:
                    # get a list of valid combinations for this location
                    combinations = self.valid_combos(target=j - i, combinations=combos)
                    if combinations:
                        element_matrix[i, j] = self.abundnace_solver(
                            combinations, element_ID
                        )

        element_matrix = element_matrix.transpose()
        logger.debug(element_matrix)
        return element_matrix

    def correction_matrix(self):
        correction_matrix = np.identity(self.vector_size)
        for element in self.formula_dict:
            current_matrix = self.matrix_populator(element)
            logger.info(f"matrix for {element}: \n{current_matrix}")
            correction_matrix = np.dot(correction_matrix, current_matrix)
        logger.info(f"corr matrix: \n{correction_matrix}")
        return correction_matrix

    def mdv_star(self):
        correction_matrix = self.correction_matrix()
        correction_matrix_inverse = np.linalg.inv(correction_matrix)
        mdv_star = np.dot(correction_matrix_inverse, self.mdv_a)

        # normalise the vector to 1
        vector_sum = np.sum(mdv_star)
        mdv_star_normalised = mdv_star / vector_sum
        logger.info(f"mdv_star_normalised \n{mdv_star_normalised}")
        return mdv_star_normalised

    def mdv_AA(self, base_aa_formula, base_aa_mdv):
        # TODO possibly implement this eqution for f_unlabelled
        # f_unlabelled = e**-(dil rate)(time of substrate feeding)
        f_unlabelled = 0.01

        mdv_unlabelled = Labelled_compound(
            formula=base_aa_formula,
            labelled_element="C",
            mdv_a=base_aa_mdv,
        )
        mdv_aa = np.dot(self.mdv_star() - f_unlabelled, mdv_unlabelled.mdv_star()) / (
            1 - f_unlabelled
        )
        return mdv_aa


def main():
    formula = input(
        f"please enter a molecular formuala for a compound or fragment \n eg C8H23NO2Si2"
    )
    labelled_element = input(f"Which element is labelled?")
    mdv_a = input(list(f"list of observed ratios: "))
    pass


if __name__ == "__main__":
    my_instance = Labelled_compound(
        formula="C8H23NO2Si2",
        labelled_element="C",
        mdv_a=[0.6628, 0.1517, 0.0749, 0.1507],
    )
    my_instance.mdv_star()

    logger.debug(f"class vars:{vars(my_instance)}")
    # print(dir(my_instance))
