import os
import unittest

import numpy as np

from steam_sdk.data.TemplateProteCCT import get_template_ProteCCT_input_sheet
from steam_sdk.parsers.ParserExcel import write2Excel
from steam_sdk.utils.delete_if_existing import delete_if_existing


class TestParserLEDET(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'Excel'), verbose=True)


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


    def test_write2Excel_default(self):
        # arrange
        file_name_GENERATED = os.path.join('output', 'Excel', 'test_write2Excel_default', 'TestFile_write2Excel_default.xlsx')
        # file_name_REFERENCE = os.path.join('references', 'TestFile_write2Excel_default.xlsx')

        # act
        write2Excel(name_file=file_name_GENERATED)

        # assert
        # TODO: Add check of the reference file


    def test_write2Excel_longList(self):
        # arrange
        file_name_GENERATED = os.path.join('output', 'Excel', 'test_write2Excel_longList', 'TestFile_write2Excel_longList.xlsx')
        # file_name_REFERENCE = os.path.join('references', 'TestFile_write2Excel_longList.xlsx')

        # act
        long_list  = list(range(16400))  # Excel cannot handle so many columns, but the parser will take care of this
        long_array = np.array(long_list)  # Excel cannot handle so many columns, but the parser will take care of this
        long_entries = [
            ['long_list',  long_list,  'long list'],
            ['long_array', long_array, 'long array'],
        ]
        write2Excel(name_file=file_name_GENERATED, name_sheets='long_list', listOf_variables_values_descriptions=[long_entries])

        # assert
        # TODO: Add check of the reference file


    def test_write2Excel_differentVariableTypes(self):
        # arrange
        file_name_GENERATED = os.path.join('output', 'Excel', 'test_write2Excel_differentVariableTypes', 'TestFile_write2Excel_differentVariableTypes.xlsx')
        # file_name_REFERENCE = os.path.join('references', 'TestFile_write2Excel_differentVariableTypes.xlsx')

        # act
        var_scalar = 123
        var_string = 'this is a string'
        var_list_of_strings = ['var_A', 'var_B']
        var_list   = list(range(10))
        var_array  = np.array(var_list)
        var_matrix = np.array([[1,2], [3,4]])
        var_matrix_of_strings = np.array([['var_A', 'var_B'], ['var_C', 'var_D']])

        var_entries = [
            ['var_scalar',  var_scalar,  'description var_scalar'],
            ['var_string', var_string, 'description var_string'],
            ['var_list', var_list, 'description var_list'],
            [None, None, 'This is a title row'],
            [None, None, None],
            ['var_list_of_strings', var_list_of_strings, 'description var_list_of_strings'],
            ['var_array', var_array, 'description var_array'],
            ['var_matrix', var_matrix, 'description var_matrix'],
            ['var_matrix_of_strings', var_matrix_of_strings, 'description var_matrix_of_strings'],
        ]
        write2Excel(name_file=file_name_GENERATED, name_sheets='different_vars', listOf_variables_values_descriptions=[var_entries])

        # assert
        # TODO: Add check of the reference file

    def test_write2Excel_templateProteCCT(self):
        # arrange
        file_name_GENERATED = os.path.join('output', 'Excel', 'test_write2Excel_templateProteCCT', 'TestFile_write2Excel_templateProteCCT.xlsx')
        # file_name_REFERENCE = os.path.join('references', 'TestFile_write2Excel_templateProteCCT.xlsx')

        template_ProteCCT_input_sheet = get_template_ProteCCT_input_sheet()

        # act
        write2Excel(name_file=file_name_GENERATED, name_sheets='different_vars', listOf_variables_values_descriptions=[template_ProteCCT_input_sheet])

        # assert
        # TODO: Add check of the reference file
