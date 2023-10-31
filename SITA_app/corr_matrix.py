import math

import numpy as np


def calculate_correction_matrix(molecular_formula, isotopic_abundances, matrix_size):
    """
    Calculate the correction matrix based on the molecular formula and isotopic abundances.

    Parameters
    ----------
    molecular_formula : str
        The molecular formula.
    isotopic_abundances : dict
        Dictionary representing the abundances of isotopes.
        The keys are the isotopes, and the values are the corresponding abundances.
    matrix_size : int
        The size of the correction matrix.

    Returns
    -------
    list
        A 2D list representing the correction matrix.
    """
    # Parse the molecular formula into a dictionary of atom counts
    atom_counts = parse_molecular_formula(molecular_formula)

    # Initialize the correction matrix with zeros
    correction_matrix = np.zeros(matrix_size)

    # Calculate the correction matrix values
    for i in range(matrix_size):
        for j in range(matrix_size):
            value = (
                math.factorial(atom_counts["C"])
                * (isotopic_abundances["C12"] ** i)
                / math.factorial(i)
                * (isotopic_abundances["C13"] ** j)
                / math.factorial(j)
            )
            correction_matrix[i][j] = value

    return correction_matrix
