import numpy as np
import re
from collections import Counter

class Labelled_compound:
    ISOTOPE_ABUNDANCE_DICT_UNIT_MASS = {'H': {'abundance':(0.999885,0.000115),'mass':(1,2)},
                                        'C': {'abdunance':(0.9893,0.0107),'mass' :(12,13)},
                                        'N': {'abdunance':(0.99632,0.00368),'mass' :(14,15)},
                                        'O': {'abdunance':(0.99757,0.00038,0.00205),'mass' :(16,17,18)},
                                        'Si': {'abdunance':(0.922297,0.046832,0.030872), 'mass' :(28,29,30)},
                                        'P': {'abdunance':(1),'mass' :(31)},
                                        'S': {'abdunance':(0.9493,0.0076,0.0429,0.0002),'mass' :(32,33,34,36)}}



    def __init__(self, formula, labelled_element):
        self.formula = formula 
        self.labelled_element = labelled_element

    def formula_parser(self):
        formula = self.formula
        # Make two capture groups, 1st one upper case letter+ lower case letter
        # 2nd group the digits following the 1st group
        pattern = r'([A-Z][a-z]*)(\d*)'
        groups = re.findall(pattern, formula)
        # creating a dict of hashable objects, the elements and their counts
        elements = Counter()

        for element, count in groups:
            # if count is empty e.g. mol form: CO, assume 1
            if count == '':
                count = 1
            else:
                count = int(count)

            elements[element] += count

    return elements






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
    Genereally this can be restricted to the number of carbons

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

def matrix_creator(element, size_of_matrix):






