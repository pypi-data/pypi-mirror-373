import os
import unittest

from steam_sdk.utils.parse_str_to_list import parse_str_to_list


class Test_parse_str_to_list(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    @staticmethod
    def _compare_lists(list1, list2):
        if type(list1) != type(list2):
            return False, f"Type mismatch: {type(list1)} vs {type(list2)}"

        if isinstance(list1, list):
            if len(list1) != len(list2):
                return False, f"Length mismatch: {len(list1)} vs {len(list2)}"
            for idx, (item1, item2) in enumerate(zip(list1, list2)):
                are_equal, detail = Test_parse_str_to_list._compare_lists(item1, item2)
                if not are_equal:
                    return False, f"Difference found at index {idx}: {detail}"
            return True, "No differences"
        else:
            if list1 != list2:
                return False, f"Value mismatch: {list1} vs {list2}"
            return True, "No differences"

    def test_parse_str_to_list(self):

        input_strings = [
            '[[Kapton, Kapton, Kapton], [G10, G10, G10]]',
            '[test, test2, test3]',
            '[test, 1, test3, 2.0]',
            '[[Kapton, Kapton, Kapton], [G10, 1, 2.0]]',
            '[[0.1, 0.1, 0.1], [0.5, 0.5, 0.5]]',
            '[[1, 2, 3], [5, 6, 7]]',
            '[1.3, 23.5, 12.4]',
            #'[CWS, 500.0, [500.0, 500.0, 0.0], 500.0, 1, solve_with_post_process_python, true, false, true, true, false, true, false]'
        ]

        expected_results = [
            [['Kapton', 'Kapton', 'Kapton'], ['G10', 'G10', 'G10']],
            ['test', 'test2', 'test3'],
            ['test', 1, 'test3', 2.0],
            [['Kapton', 'Kapton', 'Kapton'], ['G10', 1, 2.0]],
            [[0.1, 0.1, 0.1], [0.5, 0.5, 0.5]],
            [[1, 2, 3], [5, 6, 7]],
            [1.3, 23.5, 12.4],
            # ['CWS', 500.0, [500.0, 500.0, 0.0], 500.0, 1, 'solve_with_post_process_python', 'true', 'false', 'true', 'true', 'false', 'true', 'false']
        ]

        only_float_list = False

        for in_string, exp_list in zip(input_strings, expected_results):
            out_list = parse_str_to_list(s=in_string, only_float_list=only_float_list)
            print(f'Checking input str: {in_string}')
            print(f'Expecting: {exp_list}')
            print(f'Got: {out_list}')
            state, comment = Test_parse_str_to_list._compare_lists(exp_list, out_list)
            self.assertTrue(state)
            print(f'Comment: {comment}')

        float_input_strings = [
            '[[0.1, 0.1, 0.1], [0.5, 0.5, 0.5]]',
            '[[1, 2, 3], [5, 6, 7]]',
            '[1.3, 23.5, 12.4]',
        ]

        float_expected_results = [
            [[0.1, 0.1, 0.1], [0.5, 0.5, 0.5]],
            [[1.0, 2.0, 3.0], [5.0, 6.0, 7.0]],
            [1.3, 23.5, 12.4]
        ]

        only_float_list = True
        for in_string, exp_list in zip(float_input_strings, float_expected_results):
            out_list = parse_str_to_list(s=in_string, only_float_list=only_float_list)
            print(f'Checking input str: {in_string}')
            print(f'Expecting: {exp_list}')
            print(f'Got: {out_list}')
            state, comment = Test_parse_str_to_list._compare_lists(exp_list, out_list)
            self.assertTrue(state)
            print(f'Comment: {comment}')

        non_float_input_strings = [
            '[[Kapton, Kapton, Kapton], [G10, G10, G10]]',
            '[test, test2, test3]',
            '[test, 1, test3, 2.0]',
            '[[Kapton, Kapton, Kapton], [G10, 1, 2.0]]',
        ]
        for non_float_input_string in non_float_input_strings:
            with self.assertRaises(ValueError):
                parse_str_to_list(s=non_float_input_string, only_float_list=only_float_list)