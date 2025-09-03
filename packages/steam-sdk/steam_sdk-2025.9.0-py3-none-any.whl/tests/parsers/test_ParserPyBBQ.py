import unittest
import os

from steam_sdk.builders.BuilderProteCCT import BuilderProteCCT
from steam_sdk.builders.BuilderPyBBQ import BuilderPyBBQ
from steam_sdk.parsers.ParserProteCCT import ParserProteCCT
from steam_sdk.parsers.ParserPyBBQ import ParserPyBBQ
from tests.TestHelpers import assert_two_parameters


class TestParserProteCCT(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # TODO: Add all parameters to check
        # Define Inputs parameters that are equal to input file
        self.local_Inputs = {
            'TOp': 1.9,
        }

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_readFromYaml(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_ParserPyBBQ_REFERENCE.yaml')
        builder_pybbq = BuilderPyBBQ(flag_build=False)

        # act
        pl = ParserPyBBQ(builder_pybbq)
        pl.readFromYaml(file_name, verbose=True)

        # assert
        self.assertEqual(hasattr(pl.builder_PyBBQ.data_PyBBQ, 'T1'), True)
        self.assertEqual(hasattr(pl.builder_PyBBQ.data_PyBBQ, 'width'), True)
        self.assertEqual(0.0015, pl.builder_PyBBQ.data_PyBBQ.width)
        # TODO: Add other checks

