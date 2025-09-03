import unittest
import os

from steam_sdk.data.DataPyBBQ import DataPyBBQ


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


    def test_DataPyBBQ_default(self):
        """
            Check that DataPyBBQ object can be initialized
        """
        # arrange

        # act
        keys_DataPyBBQ    = DataPyBBQ()

        # assert
        # TODO: Add a sensible action to perform the test


    def test_DataPyBBQ_setAttribute(self):
        """
            Check that values of DataPyBBQ dataclasses can be set
        """

        # String key
        value = 'width'
        keys_DataPyBBQ = DataPyBBQ()
        keys_DataPyBBQ.shape = value
        self.assertEqual(keys_DataPyBBQ.shape, value)

        # Float key
        value = 12312.54
        keys_DataPyBBQ = DataPyBBQ()
        keys_DataPyBBQ.width = value
        self.assertEqual(keys_DataPyBBQ.width, value)

        # Int key
        value = 123
        keys_DataPyBBQ = DataPyBBQ()
        keys_DataPyBBQ.sections = value
        self.assertEqual(keys_DataPyBBQ.sections, value)

        # list
        value = [123.3, 423.4, 43247, 453.8]
        keys_DataPyBBQ = DataPyBBQ()
        keys_DataPyBBQ.t0 = value
        self.assertEqual(keys_DataPyBBQ.t0, value)

        # TODO Check why test does NOT fail when incorrect key types are set