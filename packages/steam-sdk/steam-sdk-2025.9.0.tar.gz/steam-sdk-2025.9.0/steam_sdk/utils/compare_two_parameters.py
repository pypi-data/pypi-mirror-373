import numpy as np

def compare_two_parameters(var_A, var_B, attribute, max_relative_error, flag_difference_messages: bool = True, verbose: bool = False):
    '''
        Helper-function for ParserLEDET() and ParserProteCCT() to compare to parameters
        max_relative_error is a relative value
    '''
    Diff = False  # Initialization to False (i.e. no differences found)

    # Check whether both parameters are None. If they are, do not detect a difference.
    if var_A is None and var_B is None:
        return Diff

    # Check whether there are parameters in one file and not in the other
    if var_A is not None and var_B is None:
        Diff = True
        if flag_difference_messages: print(f'Parameter {attribute} in file A is {var_A} while in file B is {var_B}')
        return Diff

    if var_B is not None and var_A is None:
        Diff = True
        if flag_difference_messages: print(f'Parameter {attribute} in file B is {var_B} while in file A is {var_A}')
        return Diff

    # Check whether the parameter has different types in the two files
    types_numeric = (int, float, np.int32, np.float32, np.float64)
    type_var_A = type(var_A)
    type_var_B = type(var_B)
    if type_var_A != type_var_B:
        if isinstance(var_A, types_numeric) and isinstance(var_B, types_numeric):
            # Allow for the parameters to be of different types, if they both are int or float
            if flag_difference_messages and verbose: print(f'Parameter {attribute} is of type {type_var_A} in file A and of type {type_var_B} in file B')
        else:
            Diff = True
            if flag_difference_messages: print(f'Parameter {attribute} is of type {type_var_A} in file A and of type {type_var_B} in file B')
            return Diff

    # Check parameter differences - scalar (int or float or..., as defined by the tuple types_numeric)
    if isinstance(var_A, types_numeric):
        if abs(var_A - var_B) > max_relative_error * abs(var_A):
            if flag_difference_messages: print(f'Found difference in scalar parameter {attribute}, A: {var_A}, B: {var_B}')
            Diff = True
        return Diff

    # Check parameter differences - string
    if isinstance(var_A, str):
        if var_A != var_B:
            Diff = True
            if flag_difference_messages: print(f'Found difference in string parameter {attribute}, A: {var_A}, B: {var_B}')
        return Diff

    # Check length of list or numpy array parameter
    if isinstance(var_A, (list, np.ndarray)):
        # Check list or array length
        if len(var_A) != len(var_B):
            Diff = True
            if flag_difference_messages: print(f'Parameter {attribute} has a length of {len(var_A)} in file A and {len(var_B)} in file B.')
            return Diff

    # Check parameter differences - list or numpy array
    if isinstance(var_A, (list, np.ndarray)):
        Diff_list = False
        Pos = []
        # Call this function recursively to check every element of the list
        for k in range(len(var_A)):
            Diff_list = compare_two_parameters(var_A[k], var_B[k], attribute, max_relative_error, flag_difference_messages=False, verbose=verbose)
            if Diff_list:
                Diff = True
                Pos.append(k)
        if Diff and flag_difference_messages:
            print(f'Found difference in list parameter {attribute}')
            if len(Pos) < 10:
                print(f'Different Positions: {Pos}')
            else:
                print('Many values are different (>10)')
                if verbose: print(Pos)
        return Diff

    # If the code arrives at this line, the differences were not checked with a known method
    raise Exception(f'Variable type {type_var_A} not supported.')