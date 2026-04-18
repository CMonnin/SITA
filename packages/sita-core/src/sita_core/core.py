import itertools
import logging
import math
import re
from collections import Counter

import numpy as np

from sita_core.isotope_data import ISOTOPE_ABUNDANCE_DICT_UNIT_MASS

logger = logging.getLogger("sita_core")

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
        vector_size=None,
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
            of these ratios needs to equal 1.
        vector_size = optional override for the MDV length. Defaults to backbone_c + 1
            (covers M+0 ... M+backbone_c). Provide explicitly only if a truncated
            MDV is measured.
        """
        self.formula = formula
        self.labelled_element = labelled_element if labelled_element else "C"
        self.formula_dict = self.formula_parser()

        if backbone_c is None:
            raise ValueError("backbone_c is required")
        total_labelled = self.formula_dict.get(self.labelled_element, 0)
        if backbone_c < 0 or backbone_c > total_labelled:
            raise ValueError(
                f"backbone_c={backbone_c} must be between 0 and the "
                f"{self.labelled_element} count in the formula ({total_labelled})"
            )
        self.backbone_c = backbone_c

        if mdv_a is not None:
            if not isinstance(mdv_a, list):
                numbers = re.split(r",\s*", mdv_a)
                float_numbers = [float(num) for num in numbers]
                self.mdv_a = np.array(float_numbers)
            else:
                self.mdv_a = np.array(mdv_a)
            self.mdv_a = self.mdv_a.reshape(-1, 1)
            self.vector_size = self.mdv_a.size
        elif vector_size:
            self.vector_size = vector_size
        else:
            self.vector_size = backbone_c + 1

        if self.vector_size > backbone_c + 1:
            raise ValueError(
                f"vector_size={self.vector_size} exceeds backbone_c+1={backbone_c + 1}"
            )
        logger.debug(f" vector_size: {self.vector_size}")

    def matrix_generator(self):
        # generate an empty matrix of appropriate size
        return np.zeros((self.vector_size, self.vector_size))

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

    def combo_solver(self, element_ID: str, atom_count_override=None) -> list:
        # figures out all the combinations depending on the
        # number of atoms and isotopes of an element.
        # atom_count_override lets callers reduce the atom count for the
        # labelled element (backbone carbons don't contribute to natural
        # abundance correction).

        if atom_count_override is not None:
            number_of_atoms = atom_count_override
        else:
            number_of_atoms = self.formula_dict[element_ID]
        number_of_isotopes = len(
            ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[element_ID]["abundance"]
        )
        combinations = itertools.combinations_with_replacement(
            range(number_of_isotopes), number_of_atoms
        )
        return list(combinations)

    def valid_combos(self, target: int, combinations: list) -> list:
        # All combinations summing to `target` mass-shift. For elements with
        # >=3 isotopes (O, Si, S, Cl, Br), multiple distinct combinations can
        # share the same mass shift (e.g. Si28+Si30 and Si29+Si29 both give
        # mass shift 2). Every such combo contributes to the matrix cell and
        # they must all be summed (see Nanchen et al. 2007 Fig. equations).
        return [list(combo) for combo in combinations if sum(combo) == target]

    def abundance_solver(
        self, combinations: Counter, element_ID: str, atom_count_override=None
    ):
        # will take the combination and convert it to the abundance to then populate
        # the matrix

        if atom_count_override is not None:
            number_of_atoms = atom_count_override
        else:
            number_of_atoms = self.formula_dict[element_ID]
        # the isotope counter will determine the values for the
        # equations eg #isotope_1 ...
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

    def matrix_populator(self, element_ID: str, atom_count_override=None):
        """Build the per-element natural-abundance contribution matrix.
        atom_count_override reduces the atom count for the labelled element so
        the tracer-subject backbone carbons don't appear in the correction.
        """

        combos = self.combo_solver(element_ID, atom_count_override=atom_count_override)
        element_matrix = self.matrix_generator()

        for i in range(self.vector_size):
            for j in range(self.vector_size):
                if j - i < 0:
                    element_matrix[i, j] = 0
                    continue
                valid = self.valid_combos(target=j - i, combinations=combos)
                cell = 0.0
                for combo in valid:
                    cell += self.abundance_solver(
                        combo, element_ID, atom_count_override=atom_count_override
                    )
                element_matrix[i, j] = cell

        element_matrix = element_matrix.transpose()
        logger.debug(element_matrix)
        return element_matrix

    def correction_matrix(self, save_to_text=False):
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
        correction_matrix = np.linalg.inv(correction_matrix)
        correction_matrix = np.round(correction_matrix, 4)
        logger.info(f"corr matrix: \n{correction_matrix}")
        if save_to_text is True:
            file_name = self.formula + ".csv"
            np.savetxt(file_name, correction_matrix, delimiter=",")
        return correction_matrix

    def mdv_star(self):
        correction_matrix = self.correction_matrix()
        mdv_star = np.round(np.dot(correction_matrix, self.mdv_a), 4)

        # normalise the vector to 1
        vector_sum = np.sum(mdv_star)
        mdv_star_normalised = np.round(mdv_star / vector_sum, 4)

        logger.info(f"mdv_star_normalised \n{mdv_star_normalised}")

        return mdv_star_normalised

    def mdv_unlabelled(self):
        # Natural-abundance MDV for the backbone_c labelled atoms only,
        # per Nanchen 2007 Eq. 4 (the reference distribution for Eq. 5).
        abundances = ISOTOPE_ABUNDANCE_DICT_UNIT_MASS[self.labelled_element]["abundance"]
        n = self.backbone_c
        vec = np.zeros((self.vector_size, 1))
        for shift in range(self.vector_size):
            combos = itertools.combinations_with_replacement(range(len(abundances)), n)
            total = 0.0
            for combo in combos:
                if sum(combo) != shift:
                    continue
                counter = Counter(combo)
                term = math.factorial(n)
                for k, v in counter.items():
                    term *= abundances[k] ** v / math.factorial(v)
                total += term
            vec[shift, 0] = total
        return vec

    def mdv_AA(self, f_unlabelled=0.01):
        # Correct for pre-existing unlabelled biomass per Nanchen 2007 Eq. 5:
        # mdv_AA = (mdv_star - f * mdv_unlabelled) / (1 - f)
        # where mdv_unlabelled is the natural-abundance distribution of the
        # n backbone atoms (Eq. 4), computed internally from backbone_c.
        # TODO: f_unlabelled may be estimated as exp(-dilution_rate * feeding_time)
        return (self.mdv_star() - f_unlabelled * self.mdv_unlabelled()) / (
            1 - f_unlabelled
        )
