import unittest
import os

from steam_sdk.data.DictionaryPyBBQ import lookupModelDataToPyBBQ


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
        input_key = 'Power_Supply.I_initial'
        expected_value = 'Current'

        # act
        returned_value = lookupModelDataToPyBBQ(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)

    def test_readOneKey_level3(self):
        """
            Check that method returns one correct dictionary value (level 3 variable)
        """
        # arrange
        input_key = 'Options_PyBBQ.physics.withCoolingToBath'
        expected_value = 'Helium_cooling'

        # act
        returned_value = lookupModelDataToPyBBQ(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)

    def test_readOneKey_level3_2(self):
        """
            Check that method returns one correct dictionary value (level 3 variable)
        """
        # arrange
        input_key = 'Options_PyBBQ.physics.VThreshold'
        expected_value = 'Detection_Voltage'

        # act
        returned_value = lookupModelDataToPyBBQ(input_key)

        # assert
        self.assertEqual(expected_value, returned_value)




    def test_readOneKey_level3_inverted(self):
        """
            Check that method returns one correct dictionary value (level 3 variable)
        """
        # arrange
        expected_value = 'Options_PyBBQ.physics.withCoolingToBath'
        input_key = 'Helium_cooling'

        # act
        returned_value = lookupModelDataToPyBBQ(input_key, mode='PyBBQ2data')

        # assert
        self.assertEqual(expected_value, returned_value)


    # TODO: Add test to check all variables in the dictionary at once