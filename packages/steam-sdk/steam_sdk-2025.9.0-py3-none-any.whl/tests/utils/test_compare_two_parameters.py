import unittest
import numpy as np

from steam_sdk.utils.compare_two_parameters import compare_two_parameters


class Test_compare_two_parameters(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        # Default test values
        self.attribute = 'dummy_attribute_name'
        self.max_relative_error = 1e-5
        self.flag_difference_messages = True
        print('')

    def _call_compare_two_parameters(self, var_A, var_B, verbose=False):
        '''
        Call the function compare_two_parameters() with default settings
        REMINDER: The function returns False if there are no differences, and True if there are differences.
        '''
        Diff = compare_two_parameters(var_A, var_B, self.attribute, self.max_relative_error, self.flag_difference_messages, verbose)
        return Diff



    def test_None_None_false(self):
        var_A = None
        var_B = None
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_int_None_true(self):
        var_A = 3
        var_B = None
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_None_int_true(self):
        var_A = None
        var_B = 3
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_int_int_false(self):
        var_A = 2
        var_B = 2
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_int_int_true(self):
        var_A = 2
        var_B = 3
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_int_float_false(self):
        var_A = 2
        var_B = 2.0
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_int_float_true(self):
        var_A = 2
        var_B = 3.0
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_int_str_true(self):
        var_A = 2
        var_B = 'abd'
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_float_float_false(self):
        var_A = 3.01
        var_B = 3.01
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_float_float_true(self):
        var_A = 3.01
        var_B = 3.02
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_str_str_true(self):
        var_A = 'abc'
        var_B = 'abd'
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_str_str_false(self):
        var_A = 'abd'
        var_B = 'abd'
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_str_list_true(self):
        var_A = 'abd'
        var_B = ['abd']
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_list1_list1_true(self):
        var_A = ['abd']
        var_B = ['abd2']
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_list1_list2_true(self):
        var_A = ['abd']
        var_B = ['abd','qwe']
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_list1_list1_false(self):
        var_A = ['abd']
        var_B = ['abd']
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_list2_list2_false(self):
        var_A = ['abd','qwe']
        var_B = ['abd','qwe']
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_list3_list3_false(self):
        var_A = [1,3]
        var_B = [1.0,3]
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_list3_list3_true(self):
        var_A = [3, 1]
        var_B = [1.0, 3]
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_list11_list11_true(self):
        var_A = [1,2,3,4,5,6,7,8, 9,10,11]
        var_B = [2,3,4,5,6,7,8,9,10,11,12]
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_list11_list11_true_verbose(self):
        var_A = [1,2,3,4,5,6,7,8, 9,10,11]
        var_B = [2,3,4,5,6,7,8,9,10,11,12]
        Diff = self._call_compare_two_parameters(var_A, var_B, verbose=True)
        self.assertTrue(Diff)

    def test_listOfLists2_listOfLists2_false(self):
        var_A = [[3  , 1  ], [5.0, 2  ]]
        var_B = [[3.0, 1.0], [5,   2.0]]
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_listOfLists2_listOfLists2_true(self):
        var_A = [[3, 1], [5.0, 2]]
        var_B = [[3.0, 2.5], [5, 2.0]]
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_array1_list_true(self):
        var_A = np.array([1])
        var_B = [1.0]
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_array1_array1_false(self):
        var_A = np.array([1])
        var_B = np.array([1.0])
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)

    def test_array11_array11_int_true(self):
        var_A = np.array([1,2,3,4,5,6,7,8, 9,10,11])
        var_B = np.array([2,3,4,5,6,7,8,9,10,11,12])
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_array11_array11_float_true(self):
        var_A = np.array([1.1,2.1,3.1,4.1,5.1,6.1,7.1,8.1, 9.1,10.1,11.1])
        var_B = np.array([2.1,3.1,4.1,5.1,6.1,7.1,8.1,9.1,10.1,11.1,12.1])
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_arrayOfArrays2_arrayOfArrays2_true(self):
        var_A = np.array([[3  , 1  ], [5.0, 2  ]])
        var_B = np.array([[3.0, 2.5], [5,   2.0]])
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertTrue(Diff)

    def test_arrayOfArrays2_arrayOfArrays2_false(self):
        var_A = np.array([[3  , 1  ], [5.0, 2  ]])
        var_B = np.array([[3.0, 1.0], [5,   2.0]])
        Diff = self._call_compare_two_parameters(var_A, var_B)
        self.assertFalse(Diff)