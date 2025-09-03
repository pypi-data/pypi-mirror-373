import unittest
import os

from steam_sdk.builders.BuilderProteCCT import BuilderProteCCT
from steam_sdk.parsers.ParserProteCCT import ParserProteCCT
from steam_sdk.utils.delete_if_existing import delete_if_existing
from tests.TestHelpers import assert_two_parameters


class TestParserProteCCT(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'ProteCCT'), verbose=True)

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

    def test_readFromExcel(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readProteCCTExcel.xlsx')
        builder_ledet = BuilderProteCCT(flag_build=False)

        # act
        pl = ParserProteCCT(builder_ledet)
        pl.readFromExcel(file_name, verbose=True)

        # assert
        # TODO: Add check of the read file


    def test_readProteCCTExcel(self):
        """
            **Test if the method readProteCCTExcel() reads correct values from input file to parametersProteCCT object**
            Returns error if any of the values read from file differs from what they should be
            Note: the input file is a read-only file such that the local parameter values and input file are equal.
            This test requires that getAttribute() works as intended
        """
        # Define default parameters
        file_name = os.path.join('references', 'TestFile_readProteCCTExcel.xlsx')
        pl = ParserProteCCT()

        # act
        bProteCCT = pl.readFromExcel(file_name, verbose=True)

        # assert
        # check that the parameters read from file are equal to those initialized locally
        for attribute in self.local_Inputs:
            self.assertIn(attribute, {**bProteCCT.Inputs.__annotations__})
            assert_two_parameters(self.local_Inputs[attribute], bProteCCT.getAttribute('Inputs', attribute))


    def test_write2Excel(self):
        # arrange
        name_file = os.path.join('output', 'ProteCCT', 'test_write2Excel', 'MCBRD_TEST.xlsx')
        bProteCCT = BuilderProteCCT(flag_build=False)

        # act
        pp = ParserProteCCT(bProteCCT)
        pp.writeProtecct2Excel(full_path_file_name=name_file, verbose=True)

        # assert
        # TODO: Add check of the read file