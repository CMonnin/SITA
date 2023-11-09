
    def correction_matrix(
        atom_ID: str, experimental_peak_number: int, number_of_atoms: int | None
    ):
        """
        calculates a matrix for one element

        parameters
        ----------

        atom_ID: str
            what the atom is
        experimental_peak_number: int
            takes the number of peaks seen in the experimental data and creates a matrix to match the size
        number_of_atoms: int
            the number of the selected atom present in the molecular formula
        returns
        -------
        the correction matrix


        notes
        -----
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

        corr_matrix = np.zeros(experimental_peak_number, experimental_peak_number)
        xxxx = 1
        for i in range(experimental_peak_number):
            for j in range(i + 1):
                if i < j:
                    corr_matrix[i, j] = 0
                else:
                    corr_matrix[i, j] = xxxx

    def correction_matrix_original(self, k, v, b, A, n):
        """This creates a matrix
        This matrix will be square, i=j
        This matrix will be triangular, diagonal values are equal and
        one side all values are = 0

        """
        vk = v * k
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
    """that matrix needs to take into account the number of
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
