import unittest
import os

from steam_sdk.data.DictionaryLEDET import lookupModelDataToLEDET


class TestModelData(unittest.TestCase):

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


    def test_readOneKey_level1(self):
        """
            Check that method returns one correct dictionary value (level 1 variable)
        """
        # arrange
        input_key = 'GeneralParameters.T_initial'
        expected_value = 'T00'

        # act
        returned_value = lookupModelDataToLEDET(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)

    def test_readOneKey_level2(self):
        """
            Check that method returns one correct dictionary value (level 2 variable)
        """
        # arrange
        input_key = 'Quench_Protection.Energy_Extraction.t_trigger'
        expected_value = 'tEE'

        # act
        returned_value = lookupModelDataToLEDET(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)

    def test_readOneKey_level2B(self):
        """
            Check that method returns one correct dictionary value (level 2 variable)
        """
        # arrange
        input_key = 'Power_Supply.t_off'
        expected_value = 't_PC'

        # act
        returned_value = lookupModelDataToLEDET(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)


    #TODO: Add test to check all variables in the dictionary at once