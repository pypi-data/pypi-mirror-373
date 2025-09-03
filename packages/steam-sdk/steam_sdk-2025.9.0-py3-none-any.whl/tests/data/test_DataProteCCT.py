import unittest
import os

from steam_sdk.data import DataProteCCT


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


    def test_DataProteCCT_default(self):
        """
            Check that DataProteCCT object can be initialized
        """
        # arrange

        # act
        keys_ProteCCTInputs    = DataProteCCT.ProteCCTInputs()

        # assert
        # TODO: Add a sensible action to perform the test

    def test_DataProteCCT_setAttribute(self):
        """
            Check that values of DataProteCCT dataclasses can be set
        """

        # String key
        value = 'MCBRD_0'
        keys_ProteCCTInputs = DataProteCCT.ProteCCTInputs()
        keys_ProteCCTInputs.magnetIdentifier = value
        self.assertEqual(keys_ProteCCTInputs.magnetIdentifier, value)

        # Float key
        value = 12312.54
        keys_ProteCCTInputs = DataProteCCT.ProteCCTInputs()
        keys_ProteCCTInputs.totalConductorLength = value
        self.assertEqual(keys_ProteCCTInputs.totalConductorLength, value)

        # Int key
        value = 123
        keys_ProteCCTInputs = DataProteCCT.ProteCCTInputs()
        keys_ProteCCTInputs.numTurnsPerStrandTotal = value
        self.assertEqual(keys_ProteCCTInputs.numTurnsPerStrandTotal, value)

        # np.array key
        value = [123.3, 423.4, 43247, 453.8]
        keys_ProteCCTInputs = DataProteCCT.ProteCCTInputs()
        keys_ProteCCTInputs.windingOrder = value
        self.assertEqual(keys_ProteCCTInputs.windingOrder, value)

        # TODO Check why test does NOT fail when incorrect key types are set