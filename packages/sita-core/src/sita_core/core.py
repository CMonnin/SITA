import logging
import re
from collections import Counter

import numpy as np

from sita_core.isotope_data import ISOTOPE_ABUNDANCE_DICT_UNIT_MASS

logger = logging.getLogger("sita_core")

# The correction matrix is (backbone_c + 1) square and gets inverted, so this
# bounds memory and CPU. Atom counts themselves are cheap (see
# shift_distribution) and are not limited.
MAX_BACKBONE_C = 200
# Sanity ceiling only: far above any real GC-MS fragment, but stops absurd
# counts (thousands of digits) from costing CPU.
MAX_ATOMS_PER_ELEMENT = 100_000

# Correction of natural abundance:
# MDV_star = Corr^-1 dot MDVa
#
# MDV_star: Corrected Isotopic Mass Distribution Vector
# Corr^-1:  Inverse of correction matrix
# MDVa:     Experimentally measured mass distribution vector normalised to 1
#
# TODO: adducts Ca, Na, NH4, FA, AA, Li
# TODO: correct for contribution by unlabelled mass


class LabelledCompound:
    def __init__(
        self,
        formula: str,
        labelled_element: str,
        backbone_c: int,
        mdv_a=None,
    ):
        """
        Each compound will have a molecular formula and
        one labelled element
        Parameters
        ----------
        formula = the chemical formula of the compound or fragment
        labelled_element = which element is labelled (currently only supports one labelled_element)
        backbone_c = number of atoms of the labelled element that are subject to
            the tracer experiment (e.g. 3 for alanine's backbone, even though the
            TBDMS fragment C8H23NO2Si2 contains 8 C total). These positions carry
            the measurement signal and are excluded from the natural-abundance
            correction per Fischer & Zamboni (2007).
        mdv_a = a list of numbers corresponding to the observed ratio of isotopes, the sum
            of these ratios needs to equal 1. Length must equal backbone_c + 1.
        """
        self.formula = formula
        self.labelled_element = labelled_element if labelled_element else "C"
        self.formula_dict = self.formula_parser()

        if not self.formula_dict:
            raise ValueError(
                f"formula={formula!r} parsed to no elements; element symbols must "
                "start with an uppercase letter (e.g. 'H2O', not 'h2o')"
            )
        for element, count in self.formula_dict.items():
            if count > MAX_ATOMS_PER_ELEMENT:
                raise ValueError(
                    f"{element}{count}: at most {MAX_ATOMS_PER_ELEMENT} atoms per element"
                )
        if self.labelled_element not in ISOTOPE_ABUNDANCE_DICT_UNIT_MASS:
            raise ValueError(
                f"labelled_element={self.labelled_element!r} is not a supported element "
                f"(known: {sorted(ISOTOPE_ABUNDANCE_DICT_UNIT_MASS)})"
            )
        if self.labelled_element not in self.formula_dict:
            raise ValueError(
                f"labelled_element={self.labelled_element!r} not present in formula {formula!r}"
            )

        if backbone_c is None:
            raise ValueError("backbone_c is required")
        total_labelled = self.formula_dict[self.labelled_element]
        if backbone_c > MAX_BACKBONE_C:
            raise ValueError(
                f"backbone_c={backbone_c} exceeds the supported maximum of {MAX_BACKBONE_C}"
            )
        if backbone_c < 0 or backbone_c > total_labelled:
            raise ValueError(
                f"backbone_c={backbone_c} must be between 0 and the "
                f"{self.labelled_element} count in the formula ({total_labelled})"
            )
        self.backbone_c = backbone_c
        self.vector_size = backbone_c + 1

        if mdv_a is not None:
            if not isinstance(mdv_a, list):
                numbers = re.split(r",\s*", mdv_a)
                float_numbers = [float(num) for num in numbers]
                self.mdv_a = np.array(float_numbers)
            else:
                self.mdv_a = np.array(mdv_a)
            self.mdv_a = self.mdv_a.reshape(-1, 1)
            if self.mdv_a.size != self.vector_size:
                raise ValueError(
                    f"mdv_a length {self.mdv_a.size} != backbone_c+1 {self.vector_size}"
                )
        logger.debug(f" vector_size: {self.vector_size}")

    def formula_parser(self):
        """
        This function parses the molecular formula
        """
        # Make two capture groups:
        # 1st one upper case letter lower case letter,
        # 2nd group the digits following the 1st group
        pattern = r"([A-Z][a-z]*)(\d*)"
        formula = self.formula
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

    def shift_distribution(self, element_ID: str, number_of_atoms: int) -> np.ndarray:
        # Probability of each mass shift 0..vector_size-1 for `number_of_atoms`
        # atoms of an element: the coefficients of
        #   (a_0 + a_1 x + a_2 x^2 + ...)^n
        # where a_k is the abundance of the isotope k mass units above the
        # lightest. Expanding this is the multinomial sum from Nanchen et al.
        # 2007 (all isotope combinations sharing a mass shift are summed), but
        # truncated at the matrix size so cost doesn't grow with atom count.
        # Squaring-and-multiplying keeps it O(log n) polynomial products.
        size = self.vector_size
        abundances = ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[element_ID]["abundance"][:size]
        base = np.zeros(size)
        base[: len(abundances)] = abundances
        result = np.zeros(size)
        result[0] = 1.0
        n = number_of_atoms
        while n:
            if n & 1:
                result = np.convolve(result, base)[:size]
            base = np.convolve(base, base)[:size]
            n >>= 1
        return result

    def matrix_populator(self, element_ID: str, atom_count_override=None):
        """Build the per-element natural-abundance contribution matrix.
        atom_count_override reduces the atom count for the labelled element so
        the tracer-subject backbone carbons don't appear in the correction.
        """
        if atom_count_override is not None:
            number_of_atoms = atom_count_override
        else:
            number_of_atoms = self.formula_dict[element_ID]

        shifts = self.shift_distribution(element_ID, number_of_atoms)
        # lower-triangular Toeplitz: cell [j, i] is the mass shift j - i
        element_matrix = np.zeros((self.vector_size, self.vector_size))
        for i in range(self.vector_size):
            element_matrix[i:, i] = shifts[: self.vector_size - i]

        logger.debug(element_matrix)
        return element_matrix

    def correction_matrix(self):
        correction_matrix = np.identity(self.vector_size)
        for element, count in self.formula_dict.items():
            if element == self.labelled_element:
                effective_count = count - self.backbone_c
                if effective_count == 0:
                    continue
                current_matrix = self.matrix_populator(
                    element, atom_count_override=effective_count
                )
            else:
                current_matrix = self.matrix_populator(element)
            logger.debug(f"matrix for {element}: \n{current_matrix}")
            correction_matrix = np.dot(correction_matrix, current_matrix)
        try:
            correction_matrix = np.linalg.inv(correction_matrix)
        except np.linalg.LinAlgError:
            correction_matrix = None
        if correction_matrix is None or not np.all(np.isfinite(correction_matrix)):
            # abundances underflowed to zero, e.g. tens of thousands of Si atoms
            raise ValueError(
                f"correction matrix for {self.formula!r} is not invertible"
            )
        logger.info(f"corr matrix: \n{correction_matrix}")
        return correction_matrix

    def mdv_star(self):
        correction_matrix = self.correction_matrix()
        # mdv_star = np.round(np.dot(correction_matrix, self.mdv_a), 4)
        mdv_star = np.dot(correction_matrix, self.mdv_a)
        # normalise the vector to 1
        vector_sum = np.sum(mdv_star)
        mdv_star_normalised = mdv_star / vector_sum
        logger.info(f"mdv_star_normalised \n{mdv_star_normalised}")

        return mdv_star_normalised

    def mdv_unlabelled(self):
        # Natural-abundance MDV for the backbone_c labelled atoms only,
        # per Nanchen 2007 Eq. 4 (the reference distribution for Eq. 5).
        return self.shift_distribution(
            self.labelled_element, self.backbone_c
        ).reshape(-1, 1)

    def mdv_AA(self, f_unlabelled=0.01):
        # Correct for pre-existing unlabelled biomass per Nanchen 2007 Eq. 5:
        # mdv_AA = (mdv_star - f * mdv_unlabelled) / (1 - f)
        # where mdv_unlabelled is the natural-abundance distribution of the
        # n backbone atoms (Eq. 4), computed internally from backbone_c.
        # TODO: f_unlabelled may be estimated as exp(-dilution_rate * feeding_time)
        return (self.mdv_star() - f_unlabelled * self.mdv_unlabelled()) / (
            1 - f_unlabelled
        )
