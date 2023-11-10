import logging
import re
import sys
from collections import Counter
import itertools
import math
import numpy as np

# setting up a logger to print to std out and to a file
# creating logger and handlers
logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
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


# correction of natural abundance
# MDV = Corr^-1 dot MDVa
# MDV: Corrected Istopic Mass Distribution Vector
# Corr^-1: Inverse of correction matrix
# MDVa = Experimentally measured Mass distrubtion vector normalised to 1


# dict of the natural abundance of common elements
# Source:
# Coursey, J. S., et al. "Atomic weights and isotopic compositions with
# relative atomic masses." NIST Physical Measurement Laboratory (2015).
# https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl

# TODO adducts Ca, Na, NH4, FA, AA, Li,

# Added some additional isotopes at 0% abundnace for ease of logic later on
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
    def __init__(self, formula: str, labelled_element: str, vector_size: int):
        """
        Each compound will have a molecular formula and
        one labelled element
        The vector_size will be required as an argument.
        This will define how big the matrix will be.
        Eg if you see M+0, M+1, M+2, the vector_size will be 3
        """
        self.formula = formula
        self.labelled_element = labelled_element
        self.vector_size = vector_size
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

        logger.debug(elements)
        return elements

    def combo_solver(self, number_of_isotopes: int, number_of_atoms: int):
        # figures out all the combinations depening on the
        # number of atoms and isotpes of an element
        # eg for the carbon in alanine C3H7NO2 there will be two isotopes
        # and three carbons
        combinations = itertools.combinations_with_replacement(
            range(number_of_isotopes), number_of_atoms
        )
        return list(combinations)

    def valid_combos(self, target: int, combinations: list):
        # a valid combo being one that sums up to the target eg M+0 has a sum
        # of 0, M+1 a sum of 1 etc ...
        valid_combos = [combo for combo in combinations if sum(combo) == target]
        return valid_combos

    def abundnace_solver(self, combinations, element_ID):
        # will take the combination and convert it to the abundance to then populate
        # the matrix
        number_of_atoms = xxx
        isotope_counter = Counter(combinations)
        abundance = math.factorial(number_of_atoms)
        for key, value in isotope_counter.items():
            abundance = (
                abundance
                * ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[element_ID][key] ** value
                / math.factorial(value)
            )

        return abundance

    def matrix_populator(self, element_ID: str, number_of_atoms: int):
        """this will take an istope and generate all the possible combinations
        that can occur depending on the number of atoms present in the compound
        practically only a subset will be used to populate the matrix which is
        dependant on the size of the matrix
        this might have to be changed. I don't know how much of performance hit
        it will cause.
        """

        # getting the mass of the 1st element of "mass" which is the most
        # abundant
        base_mass = (
            ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[element_ID].get("mass")[0]
            * number_of_atoms
        )
        number_of_isotopes = len(
            ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[element_ID]["abundance"]
        )
        mass_list = []
        current_mass = base_mass
        for i in range(0, number_of_atoms + 1):
            mass_list.append(current_mass)
            current_mass += 1
        combos = self.combo_solver(number_of_isotopes, number_of_atoms)
        element_matrix = self.matrix_generator()

        for i in range(self.vector_size):
            for j in range(self.vector_size):
                if j - i == 0:
                    element_matrix[i, j] = self.valid_combos(
                        target=0, combinations=combos
                    )
                if j - i < 0:
                    element_matrix[i, j] = 0

                else:
                    element_matrix[i, j] = self.valid_combos(
                        target=j - i, combinations=combos
                    )

        for element in mass_list:
            self.valid_combos(target=element, combinations=combos)


if __name__ == "__main__":
    my_instance = Labelled_compound(
        formula="C3H7NO2",
        labelled_element="C",
        vector_size=3,
    )
    my_instance.matrix_populator(element_ID="C", number_of_atoms=3)
