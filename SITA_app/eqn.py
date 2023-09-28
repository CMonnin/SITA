import numpy as np


hydrogen_isotpes = (0.999885,0.000115)
carbon_isotopes = (0.9893,0.0107)
nitrogen_isotopes = (0.99632,0.00368)
oxygen_isotopes = (0.99757,0.00038,0.00205)
silicon_isotopes = (0.922297,0.046832,0.030872)
phosphorus_isotopes = (1)
sulphur_isotopes = (0.9493,0.0076,0.0429,0.0002)
hydrogen_most_abundant = 1
carbon_most_abundant = 12
nitrogen_most_abundant = 14
oxygen_most_abundant = 16
silicon_most_abundant = 28
phosphorus_most_abundant = 31 
sulphur_most_abundant = 32 



def correction_matrix():
    '''This creates a matrix
    This matrix will be square, i=j
    This matrix will be triangular, diagonal values are equal and 
    one side all values are = 0

    '''
    v_factorial = math.factorial(v)
    product_term = 1
    for i in range(n):
        product_term *= (A*b[k]**vk[k])/ math.factorial(vk[k])
        return 

def test_prod(n):
    k=1
    n=int(n)
    for i in range(k,n):
        print(i)

def correction_matrix_test(size_of_matrix=4,C_num=0,H_num=0,
                           O_num=0,N_num=0,Si_num=0,S_num=0,):

    ''' that matrix needs to take into accont the number of 
    units the user wants to calculate out to. Use itertools
    to calculate the the different combinations that are required.
    eg O has 16O, 17O, and 18O that can contribute. 
    where there are 2 O, M+2 can come from 17O2, or 16O + 18O
    '''
    corr_matrix = np.zeros((size_of_matrix,size_of_matrix))
    carbon_matrix = np.zeros((size_of_matrix,size_of_matrix))
    carbon_list = []

    for count, item in enumerate(carbon_isotopes ):
        carbon_list.append()
    for i in range (size_of_matrix):
        for j in range (size_of_matrix):
            matrix[i,j] = XXXXXX



    pass

