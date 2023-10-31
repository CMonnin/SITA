import logging
import re
import sys
from collections import Counter

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


class Labelled_compound:
    # dict of the natural abundance of common elements
    # source: XXXXX
    ISOTOPE_ABUNDANCE_DICT_UNIT_MASS = {
        "H": {"abundance": (0.999885, 0.000115), "mass": (1, 2)},
        "C": {"abundance": (0.9893, 0.0107), "mass": (12, 13)},
        "N": {"abundance": (0.99632, 0.00368), "mass": (14, 15)},
        "O": {"abundance": (0.99757, 0.00038, 0.00205), "mass": (16, 17, 18)},
        "Si": {"abundance": (0.922297, 0.046832, 0.030872), "mass": (28, 29, 30)},
        "P": {"abundance": (1), "mass": (31)},
        "S": {"abundance": (0.9493, 0.0076, 0.0429, 0.0002), "mass": (32, 33, 34, 36)},
    }

    def __init__(self, formula, labelled_element):
        """
        Each compound will have a molecular formula and
        one labelled element
        """
        self.formula = formula
        self.labelled_element = labelled_element

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

    def correction_matrix(atom_ID, number_of_atoms):
        """
        calculates a matrix for one element

        parameters
        atom_ID: what the atom is
        number_of_atoms: the number of the selected atom present in the molecular formula

        eg for a 4x4 matrix for C, it's calculated out to M+3


        +-----+-----------+-----------+-----------+------+
        | M+0 |    12C8   |     0     |     0     |   0  |
        +-----+-----------+-----------+-----------+------+
        | M+1 | 12C7 13C1 |    12C8   |     0     |   0  |
        +-----+-----------+-----------+-----------+------+
        | M+2 | 12C6 13C2 | 12C7 13C1 |    12C8   |   0  |
        +-----+-----------+-----------+-----------+------+
        | M+3 | 12C5 13C3 | 12C6 13C2 | 12C7 13C1 | 12C8 |
        +-----+-----------+-----------+-----------+------+

        """
        # right now calculated out to n+1, which is the maximum number of peaks that would be seen
        # in practice this probably only needs to go out to M+5 or M+6

        corr_matrix = np.zeros(number_of_atoms + 1, number_of_atoms + 1)
        xxxx = 1
        for i in range(number_of_atoms + 1):
            for j in range(i + 1):
                if i < j:
                    corr_matrix[i, j] = 0
                else:
                    corr_matrix[i, j] = xxxx

    def correction_matrix_original(self):
        """This creates a matrix
        This matrix will be square, i=j
        This matrix will be triangular, diagonal values are equal and
        one side all values are = 0

        """

    v_factorial = math.factorial(v)
    product_term = 1
    for i in range(n):
        product_term *= (A * b[k] ** vk[k]) / math.factorial(vk[k])
    pass


def test_prod(n):
    k = 1
    n = int(n)
    for i in range(k, n):
        print(i)


def correction_matrix_test(
    size_of_matrix=4,
    C_num=0,
    H_num=0,
    O_num=0,
    N_num=0,
    Si_num=0,
    S_num=0,
):
    """that matrix needs to take into accont the number of
    units the user wants to calculate out to. Use itertools
    to calculate the the different combinations that are required.
    eg O has 16O, 17O, and 18O that can contribute.
    where there are 2 O, M+2 can come from 17O2, or 16O + 18O
    Genereally this can be restricted to the number of carbons

    """
    corr_matrix = np.zeros((size_of_matrix, size_of_matrix))
    carbon_matrix = np.zeros((size_of_matrix, size_of_matrix))
    carbon_list = []

    for count, item in enumerate(carbon_isotopes):
        carbon_list.append()
    for i in range(size_of_matrix):
        for j in range(size_of_matrix):
            matrix[i, j] = XXXXXX

    pass


def matrix_creator(element, size_of_matrix):
    pass
