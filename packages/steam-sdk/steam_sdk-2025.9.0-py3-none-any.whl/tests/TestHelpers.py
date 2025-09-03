""" Some functions used in multiple test functions """
import unittest
import json
from typing import List

from steam_sdk.parsers.ParserYAML import yaml_to_data
import numpy as np
import yaml
import os


def assert_two_parameters(true_value, test_value):
    """
        **Assert two parameters - accepts multiple types**
    """
    # TODO: improve robustness and readability
    test_case = unittest.TestCase()

    if isinstance(true_value, np.ndarray) or isinstance(true_value, list):
        if len(true_value) == 1:
            true_value = float(true_value)

    if isinstance(test_value, np.ndarray) or isinstance(test_value, list):
        if len(test_value) == 1:
            test_value = float(test_value)

    # Comparison
    if isinstance(test_value, np.ndarray) or isinstance(test_value, list):
        if np.array(true_value).ndim == 2:
            for i, test_row in enumerate(test_value):
                if isinstance(test_row[0], np.floating):
                    test_row = np.array(test_row).round(10)
                    true_value[i] = np.array(true_value[i]).round(10)

                test_case.assertListEqual(list(test_row), list(true_value[i]))
        else:
            if isinstance(test_value[0], np.floating):
                test_value = np.array(test_value).round(10)
                true_value = np.array(true_value).round(10)

            test_case.assertListEqual(list(test_value), list(true_value))
    else:
        test_case.assertEqual(test_value, true_value)


def assert_equal_json(json_file1, json_file2):
    """
        **Assert that two json files are equal **
    """
    test_case = unittest.TestCase()

    # Load files to compare
    with open(json_file1, "r") as f1:
        file1 = json.loads(f1.read())
    with open(json_file2, "r") as f2:
        file2 = json.loads(f2.read())

    flag_equal = True

    # Compare files and print differences
    for item in file2:
        if item not in file1:
            print(f"Found item that appears in File2 but not in File1: {item}")
            flag_equal = False
        else:
            if not file1[item] == file2[item]:
                print(f"Found difference: {item}. File1: {file1[item]}. File2:{file2[item]}")
                flag_equal = False

    # Compare files and print differences (second check to be sure the two files have all and the same entries)
    for item in file1:
        if item not in file2:
            print(f"Found item that appears in File1 but not in File2: {item}")
            flag_equal = False

    # Display message and assert files have the same entries
    if flag_equal:
        print('Files {} and {} have the same entries.'.format(json_file1, json_file2))
    test_case.assertEqual(flag_equal, True)

    # test_case.assertEqual(file1 == file2, True)  # redundant


def assert_equal_readable_files(file1, file2, n_lines_to_skip_file1: int = 0, n_lines_to_skip_file2: int = 0):
    """
        **Assert that two csv files are equal **
    """
    test_case = unittest.TestCase()

    # Load files to compare
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        # Skip specified number of lines from each file
        for _ in range(n_lines_to_skip_file1):
            next(f1)
        for _ in range(n_lines_to_skip_file2):
            next(f2)

        file1_content = f1.readlines()
        file2_content = f2.readlines()

    flag_equal = True
    for line in file2_content:
        if line not in file1_content:
            print(f"Found line that appears in File2 but not in File1: {line}")
            flag_equal = False
    for line in file1_content:
        if line not in file2_content:
            print(f"Found line that appears in File1 but not in File2: {line}")
            flag_equal = False

    # Display message and assert files have the same entries
    if flag_equal:
        print('Files {} and {} have the same entries.'.format(file1, file2))
    test_case.assertEqual(flag_equal, True)


def assert_equal_yaml_OLD(yaml_file1, yaml_file2):
    """
    Compares content of two yaml files parsed to dictionaries with assertEqual
    :param yaml_file1: full path to yaml_file1
    :type yaml_file1: str
    :param yaml_file2: full path to yaml_file2
    :type yaml_file2: str
    :return: Nothing, asserts equal
    :rtype:
    """
    dict_file_1 = yaml_to_data(yaml_file1)
    dict_file_2 = yaml_to_data(yaml_file2)
    print(f'Comparing: {yaml_file1} with: {yaml_file2}.')
    test_case = unittest.TestCase()
    test_case.assertEqual(dict_file_1, dict_file_2)
    print(f'Files: {yaml_file1} and {yaml_file2} are the same.')


def assert_equal_yaml(yaml_file1, yaml_file2, check_for_same_order=False, max_relative_error=0.000001, keys_to_ignore=['M_m', 'M_InductanceBlock_m']):
    """
    Compares content of two yaml files
    :param yaml_file1: full path to yaml_file1
    :type yaml_file1: str
    :param yaml_file2: full path to yaml_file2
    :type yaml_file2: str
    :param check_for_same_order: flag that determines if also order of entries in yaml file should be the same
    :type check_for_same_order: bool
    :param max_relative_error: maximum relative difference of values
    :type max_relative_error: float
    :param keys_to_ignore: keys in yaml dict to ignore if they are different
    :type keys_to_ignore list of strings with key names
    :return: Nothing, asserts equal
    """
    print(f'Comparing: {yaml_file1} with: {yaml_file2}.')
    test_case = unittest.TestCase()
    with open(yaml_file1, 'r') as f1, open(yaml_file2, 'r') as f2:
        # load files
        data1 = yaml.safe_load(f1)
        data2 = yaml.safe_load(f2)
        name1 = os.path.basename(yaml_file1)
        name2 = os.path.basename(yaml_file2)
        # compare files
        if type(data1) == dict and type(data2) == dict:
            # generate custom error message and continue checking even if error is found to have detailed message
            msg_list = compare_dicts_print_differences(data1, data2, max_relative_error, name1, name2, check_for_same_order, keys_to_ignore=keys_to_ignore)
            error_msg = f'\nDifferences found when comparing {name1} and {name2} \n' + '\n'.join(msg_list)
            test_case.assertTrue(msg_list == [], error_msg)
        else:
            test_case.assertEqual(data1, data2)
        print(f'Files: {yaml_file1} and {yaml_file2} are identical.')


## HELPERS
def compare_dicts_print_differences(dict1, dict2, max_relative_error=1e-6, name1='', name2='', check_for_same_order=False, keys_to_ignore=[]):
    """
    Function that compares tow dicts and returns message list describing differences
    If there are no differences the list is empty
    :param dict1: reference dict to compare
    :param dict2: output dict to compare
    :param max_relative_error: maximum relative difference of values
    :param name1: name of first yaml file
    :param name2: name of second yaml file
    :param check_for_same_order: flag to also check for same order of keys
    """
    msg_list = []
    keys1 = list(dict1.keys())
    keys2 = list(dict2.keys())

    # check for same order
    if check_for_same_order:
        if keys1 != keys2:
            msg_list.append(" - Dicts have different order of keys:")
            msg_list.append(f"Order of keys in {name1} : {keys1}")
            msg_list.append(f"Order of keys in {name2} : {keys2}")

    # check for same variable names and values
    for key in dict1.keys():
        if key in keys_to_ignore:
            pass     # this key is to be ignored
        else:
            within_relative_error = True
            if dict1[key] != dict2[key]:
                within_relative_error = False
            if is_number(dict1[key]) and is_number(dict2[key]):
                if abs(dict1[key] - dict2[key]) < max_relative_error * dict2[key]:
                    within_relative_error = True
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                # Compare nested dictionaries
                msg_list += compare_dicts_print_differences(dict1[key], dict2[key], max_relative_error, name1, name2, check_for_same_order, keys_to_ignore=keys_to_ignore)
            elif isinstance(dict1[key], list) and isinstance(dict2[key], list):
                within_relative_error = lists_are_identical(dict1[key], dict2[key], max_relative_error)
            if key not in dict2:
                msg_list.append(f"Key '{key}' is only present in {name1}.")

            if not within_relative_error:
                # add string that displays differences
                msg_list.append(f"Value for key '{key}' is different:")
                if len(name1) < len(name2):
                    msg_list.append('     ' + name1.rjust(len(name2), " ") + f":   {dict1[key]} != ")
                    msg_list.append('     ' + name2 + f":   {dict2[key]}")
                elif len(name1) > len(name2):
                    msg_list.append('     ' + name1 + f":   {dict1[key]} != ")
                    msg_list.append('     ' + name2.rjust(len(name1), " ") + f":   {dict2[key]}")
    for key in dict2.keys():
        if key not in dict1:
            msg_list.append(f"Key '{key}' is only present in {name2}.")

    # return list of messages
    return msg_list

def lists_are_identical(list1: List, list2: List, max_rel_error=1e-6):
    """
    Checks if two lists are identical, considering elements of numeric types with a given relative error tolerance.
    This function is recursive and also checks for nested lists within the input lists.

    :param list1: The first list to be compared.
    :param list2: The second list to be compared.
    :param max_rel_error: The maximum relative error allowed for numeric elements (default is 1e-9).

    :return: True if the two lists are identical, considering the given relative error tolerance for numeric elements;
    """

    if len(list1) != len(list2):
        return False

    for item1, item2 in zip(list1, list2):
        if type(item1) != type(item2):
            return False

        if isinstance(item1, list):
            if not lists_are_identical(item1, item2, max_rel_error):
                return False
        elif is_number(item1):
            if abs(item1 - item2) > max_rel_error * max(abs(item1), abs(item2)):
                return False
        else:
            if item1 != item2:
                return False

    return True

def is_number(value):
    # returns if a variable is int or float
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def assert_string_in_file(file_path, target_string):
    """
    Simple function to check if a text file with file_path contains target_string
    :param file_path: full path to the file with extension
    :type file_path: str
    :param target_string: string to check
    :type target_string: str
    :return: test pass or fail via unittest
    :rtype: None
    """
    def check_string_in_file(file_path, target_string):

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if target_string in line:
                        return True
            return False
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return False
    test_case = unittest.TestCase()
    test_case.assertTrue(check_string_in_file(file_path, target_string))