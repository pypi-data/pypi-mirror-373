import numpy as np

def unique(input_list: list):
    '''
    function to get unique values from a list
    '''
    return list(np.unique(np.array(input_list)))
