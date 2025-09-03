import os
import unittest

import numpy as np

from steam_sdk.parsers.ParserCsv import get_signals_from_csv, write_signals_to_csv
from steam_sdk.parsers.ParserCsv import load_global_parameters_from_csv
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from tests.TestHelpers import assert_equal_yaml


class TestParserCsv(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'Csv'), verbose=True)

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


    def test_read_csv(self, max_relative_error=1e-6):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.csv')
        selected_signals = ['time_vector', 'I_CoilSections_1']
        output_path = os.path.join('output', 'Csv', 'test_read_csv', 'testcsv.csv')
        reference_path = os.path.join('references', 'testcsv_REFERENCE.csv')
        make_folder_if_not_existing(os.path.dirname(output_path))

        # act
        df_signals = get_signals_from_csv(file_name, selected_signals)

        # assert
        df_signals.to_csv(output_path, index=False)

        data_generated = np.genfromtxt(output_path, dtype=float, delimiter=',', skip_header=1)
        data_reference = np.genfromtxt(reference_path, dtype=float, delimiter=',', skip_header=1)

        # Check that the number of elements in the generated matrix is the same as in the reference file
        if data_generated.size != data_reference.size:
            raise Exception('Generated csv file does not have the correct size.')

        relative_differences = np.abs(data_generated - data_reference) / data_reference  # Matrix with absolute values of relative differences between the two matrices
        max_relative_difference = np.max(np.max(relative_differences))  # Maximum relative difference in the matrix
        self.assertAlmostEqual(0, max_relative_difference, delta=max_relative_error)  # Check that the maximum relative difference is below
        print("Files {} and {} differ by less than {}%.".format(output_path, reference_path,max_relative_difference * 100))

    def test_check_global_parameters_from_csv_table(self):
        #arrange
        reference_file = os.path.join('references', 'load_parameters_from_csv',
                                      'reference_file_load_parameters_from_csv.yaml')  # this is a  yaml model file with manually edited glocal parameters

        filename=os.path.join('input', 'load_parameters_from_csv', 'input_test_load_parameters_from_csv.csv')
        circuit_name="RCS.A12B1"
        steam_models_path='../builders/model_library'
        case_model="circuit"

        #act
        expected_file = load_global_parameters_from_csv(filename, circuit_name, steam_models_path, case_model) # this file will be written by the test. Its name is written programmatically

        #assert
        assert_equal_yaml(reference_file, expected_file)


    def test_write_signals_to_csv(self):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.csv')
        selected_signals = ['time_vector', 'I_CoilSections_1', 'U_QH_3']
        dict_translate_signal_names = {'time_vector': 'time', 'I_CoilSections_1': 'I', 'U_QH_3': 'U'}
        delim = ' '
        output_path = os.path.join('output', 'Csv', 'write_signals_to_csv', 'test_write_signals_to_csv.csv')
        make_folder_if_not_existing(os.path.dirname(output_path))

        # arrage - read input file
        dict_signals = dict(get_signals_from_csv(file_name, selected_signals))

        # act
        write_signals_to_csv(full_name_file=output_path, dict_signals=dict_signals, list_signals=selected_signals, dict_translate_signal_names=dict_translate_signal_names, delimiter=delim)

        # assert
        dict_read_signals = dict(get_signals_from_csv(output_path, dict_translate_signal_names.values(), delimiter=delim))  # read the written file
        self.assertListEqual(list(dict_read_signals.keys()), list(dict_translate_signal_names.values()))
        self.assertListEqual(list(dict_read_signals['time']), list(dict_signals['time_vector']))
        self.assertListEqual(list(dict_read_signals['I']), list(dict_signals['I_CoilSections_1']))
        self.assertListEqual(list(dict_read_signals['U']), list(dict_signals['U_QH_3']))
