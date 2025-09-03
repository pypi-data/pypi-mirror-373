import unittest
import os

from steam_sdk.data.DictionaryProteCCT import lookupModelDataToProteCCT


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


    def test_readOneKey_level2(self):
        """
            Check that method returns one correct dictionary value (level 2 variable)
        """
        # arrange
        input_key = 'GeneralParameters.T_initial'
        expected_value = 'TOp'

        # act
        returned_value = lookupModelDataToProteCCT(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)

    def test_readOneKey_level3(self):
        """
            Check that method returns one correct dictionary value (level 3 variable)
        """
        # arrange
        input_key = 'Options_ProteCCT.time_vector.tMaxStopCondition'
        expected_value = 'tMaxStopCondition'

        # act
        returned_value = lookupModelDataToProteCCT(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)


    # TODO: Add test to check all variables in the dictionary at once