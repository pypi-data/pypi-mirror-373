import unittest
import os

from steam_sdk.data import DataLEDET


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


    def test_DataLEDET_default(self):
        """
            Check that DataLEDET object can be initialized
        """
        # arrange

        # act
        keys_LEDETInputs    = DataLEDET.LEDETInputs()
        keys_LEDETOptions   = DataLEDET.LEDETOptions()
        keys_LEDETPlots     = DataLEDET.LEDETPlots()
        keys_LEDETVariables = DataLEDET.LEDETVariables()

        # assert
        # TODO: Add a sensible action to perform the test

    def test_DataLEDET_setAttribute(self):
        """
            Check that values of DataLEDET dataclasses can be set
        """
        # TODO Programmatically set and check all entries
        value = 11
        keys_LEDETInputs = DataLEDET.LEDETInputs()
        keys_LEDETInputs.alphasDEG = value
        self.assertEqual(keys_LEDETInputs.alphasDEG, value)

        value = 12
        keys_LEDETOptions = DataLEDET.LEDETOptions()
        keys_LEDETOptions.flag_3D = value
        self.assertEqual(keys_LEDETOptions.flag_3D, value)

        value = 13
        keys_LEDETPlots = DataLEDET.LEDETPlots()
        keys_LEDETPlots.flagSavePlot = value
        self.assertEqual(keys_LEDETPlots.flagSavePlot, value)

        value = 14
        keys_LEDETVariables = DataLEDET.LEDETVariables()
        keys_LEDETVariables.typeVariableToSaveTxt = value
        self.assertEqual(keys_LEDETVariables.typeVariableToSaveTxt, value)

        value = 15
        keys_LEDETAuxiliary = DataLEDET.LEDETAuxiliary()
        keys_LEDETAuxiliary.heat_exchange_max_distance = value
        self.assertEqual(keys_LEDETAuxiliary.heat_exchange_max_distance, value)