import re
import ast

def parse_str_to_list(s: str, only_float_list: bool = False):
    """
        this function turns:
            - strings in the format '[[Kapton, Kapton, Kapton], [G10, G10, G10]]' to a list of lists of strings [['Kapton', 'Kapton', 'Kapton'], ['G10', 'G10', 'G10']]
            - floats in the format '[[0.1, 0.1, 0.1], [0.5, 0.5, 0.5]]' to a list of lists of floats [[[0.1, 0.1, 0.1], [0.5, 0.5, 0.5]]
            - integers in the format '[[1, 2, 3], [5, 6, 7]]' to a list of lists of ints [[1, 2, 3], [5, 6, 7]]
            - strings in the format '[1.3, 23.5, 12.4]' to a list of floats [1.3, 23.5, 12.4]
            - strings in the format '[test, test2, test3]' to a list of strings ['test', 'test2', 'test3']
            - strings in the format '[test, 1, test3, 2.0]' to a list of mixed values [test, 1, test3, 2.0] i.e.: [str, int, str, float]
            - strings in the format '[[Kapton, Kapton, Kapton], [G10, 1, 2.0]]' to a list of mixed values [[Kapton, Kapton, Kapton], [G10, 1, 2.0]] i.e.: [[str, str, str], [str, int, float]]
            - strings in another format stay the same string
        :param s: input string from csv
        :param only_float_list: if this flag is true an Exception will be raised when not parsable into a float list
        :return: parsed python datatype needed in model_data
    """

    if s.startswith('[[') and s.endswith(']]'):
        # Remove the enclosing brackets and split the string into sublists
        allowed_inner_list_separations = ['], [', '],[', '],  [']
        split_str_found = False
        for spl_str in allowed_inner_list_separations: # this is to deal with space or no space case between the brackets as in this list. Extend the list if you manage to find not covered way.
            if spl_str in s:
                split_str_found = True
                spl_str_to_use = spl_str
        if split_str_found:
            sublists = s.strip('[]').split(spl_str_to_use)
        else:
            try:    # this case deals with a list of lists with lenght of the outer list equal to 1, e.g.: '[[49,50]]'
                obj = ast.literal_eval(s)
                if (isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], list)):
                    return obj
            except (ValueError, SyntaxError):
                ValueError(f"List of lists in the parametric sweep .csv file has wrong spacing between the inner list. Try to use of of the following: {allowed_inner_list_separations}.")
        # Split each sublist into individual strings
        l_l_of_str = [re.split(r',\s*', sublist.strip('[]')) for sublist in sublists]
        out_l = []
        if only_float_list:
            for sub_l in l_l_of_str:
                out_sub_l = []
                for elem in sub_l:
                    val = float(elem)       # then check if it is a float
                    out_sub_l.append(val)
                out_l.append(out_sub_l)
        else:
            for sub_l in l_l_of_str:
                out_sub_l = []
                for elem in sub_l:
                    try:
                        val = int(elem)     # if it is int this would not error
                    except ValueError:
                        try:
                            val = float(elem)       # then check if it is a float
                        except ValueError:
                            val = elem          # well, it must be as string, so return 'as is'
                    out_sub_l.append(val)
                out_l.append(out_sub_l)
        return out_l
    elif s.startswith('[') and s.endswith(']'):
        if only_float_list:
            return [float(x) for x in s[1:-1].split(',')]
        else:
            returned_list = []  # this could be a mixed list of strings, floats or integrates, treat each entry individually
            for x in s[1:-1].split(','):
                try:
                    x = int(x)      # int conversion will take care of stripping
                except ValueError:
                    try:
                        x = float(x)    # float conversion will take care of stripping
                    except ValueError:
                        x = x.strip()   # strip spaces before the string if present
                returned_list.append(x)
            # Try to split the string and convert each element to a float
            return returned_list
    else:
        # if no list: use normal string
        if only_float_list:
            raise Exception(f'The entry ({s}) in the csv file cant be parsed into a float list.')
        return s