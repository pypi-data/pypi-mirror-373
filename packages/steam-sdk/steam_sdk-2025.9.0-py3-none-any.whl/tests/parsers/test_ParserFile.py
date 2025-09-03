import os
import unittest

import numpy as np
import pandas as pd

from steam_sdk.parsers.ParserFile import get_signals_from_file
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class TestParserFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'File'), verbose=True)

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

    def test_read_file_csv_columns(self, max_relative_error=1e-6):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.csv')
        selected_signals = ['time_vector', 'I_CoilSections_1']
        output_path = os.path.join('output', 'File', 'test_read_csv', 'testcsv.csv')
        reference_path = os.path.join('references', 'testcsv_REFERENCE.csv')

        # act
        dict_signals = get_signals_from_file(file_name, selected_signals)

        # assert
        make_folder_if_not_existing(os.path.dirname(output_path), verbose=False)
        df = pd.DataFrame(dict_signals)
        df.to_csv(output_path, index=None)

        data_generated = np.genfromtxt(output_path, dtype=float, delimiter=',', skip_header=1)
        data_reference = np.genfromtxt(reference_path, dtype=float, delimiter=',', skip_header=1)

        # Check that the number of elements in the generated matrix is the same as in the reference file
        if data_generated.size != data_reference.size:
            raise Exception('Generated csv file does not have the correct size.')

        relative_differences = np.abs(data_generated - data_reference) / data_reference  # Matrix with absolute values of relative differences between the two matrices
        max_relative_difference = np.max(np.max(relative_differences))  # Maximum relative difference in the matrix
        self.assertAlmostEqual(0, max_relative_difference, delta=max_relative_error)  # Check that the maximum relative difference is below
        print(f"Files {output_path} and {reference_path} differ by less than {max_relative_difference * 100}%.")

    def test_read_file_mat(self, max_relative_error=1e-6):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.mat')
        selected_signals = ['time_vector', 'I_CoilSections']  # , 'HotSpotT']
        dict_variable_types = {'time_vector': '1D', 'I_CoilSections': '1D'}
        output_path = os.path.join('output', 'File', 'test_check_mat', 'testmat.csv')
        reference_path = os.path.join('references', 'testmat_REFERENCE.csv')

        # act
        dict_signals = get_signals_from_file(file_name, selected_signals, dict_variable_types=dict_variable_types)

        # assert
        make_folder_if_not_existing(os.path.dirname(output_path), verbose=False)
        df = pd.DataFrame(dict_signals)
        df.to_csv(output_path, index=None)

        data_generated = np.genfromtxt(output_path, dtype=float, delimiter=',', skip_header=1)
        data_reference = np.genfromtxt(reference_path, dtype=float, delimiter=',', skip_header=1)

        # Check that the number of elements in the generated matrix is the same as in the reference file
        if data_generated.size != data_reference.size:
            raise Exception('Generated csv file does not have the correct size.')

        data_generated[data_generated == 0] = 1e-12
        data_reference[data_reference == 0] = 1e-12

        relative_differences = np.abs(data_generated - data_reference) / data_reference  # Matrix with absolute values of relative differences between the two matrices
        max_relative_difference = np.max(np.max(relative_differences))  # Maximum relative difference in the matrix
        self.assertAlmostEqual(0, max_relative_difference, delta=max_relative_error)  # Check that the maximum relative difference is below
        print("Files {} and {} differ by less than {}%.".format(output_path, reference_path, max_relative_difference * 100))

    def test_read_file_csd(self, max_relative_error=1e-6):
        # arrange
        file_name_input = os.path.join('input', 'test_csd_time.csd')
        selected_signals = ['time', 'I(r1_warm)']
        output_path = os.path.join('output', 'File', 'test_get_signals_from_csd_one_signal_and_time', 'testcsd_2.csv')
        reference_path = os.path.join('references', 'testcsd_with_time_REFERENCE.csv')

        # act
        dict_signals = get_signals_from_file(file_name_input, selected_signals)

        # assert
        make_folder_if_not_existing(os.path.dirname(output_path), verbose=False)
        df = pd.DataFrame(dict_signals)
        df.to_csv(output_path, index=None)

        data_generated = np.genfromtxt(output_path, dtype=float, delimiter=',', skip_header=1)
        data_reference = np.genfromtxt(reference_path, dtype=float, delimiter=',', skip_header=1)

        # Check that the number of elements in the generated matrix is the same as in the reference file
        if data_generated.size != data_reference.size:
            raise Exception('Generated csv file does not have the correct size.')

        # Substitute 0 with small value to avoid error when dividing by zero
        data_generated[data_generated == 0] = 1e-12
        data_reference[data_reference == 0] = 1e-12

        relative_differences = np.abs(data_generated - data_reference) / data_reference  # Matrix with absolute values of relative differences between the two matrices
        max_relative_difference = np.max(np.max(relative_differences))  # Maximum relative difference in the matrix
        self.assertAlmostEqual(0, max_relative_difference, delta=max_relative_error)  # Check that the maximum relative difference is below
        print("Files {} and {} differ by less than {}%.".format(output_path, reference_path, max_relative_difference * 100))

    def test_read_file_csv_single_variable_matrix(self):
        # arrange
        file_name = os.path.join('input', 'read_file_csv_single_var', 'TEST_read_file_csv_single_var_matrix.csv')

        # act
        np_signal = get_signals_from_file(file_name)

        # assert
        self.assertListEqual([[5.019003062086528e-05, 5.019003062086528e-05],
                              [5.019003062086528e-05, 5.019003062086528e-05]], np_signal.tolist())

    def test_read_file_csv_single_variable_scalar(self):
        # arrange
        file_name = os.path.join('input', 'read_file_csv_single_var', 'TEST_read_file_csv_single_var_scalar.csv')

        # act
        np_signal = get_signals_from_file(file_name)

        # assert
        self.assertEqual(5.019003062086528e-05, np_signal)


    def test_read_file_stl(self):
        # arrange
        file_name = os.path.join('input', 'read_file_stl', 'TEST_read_file_stl.stl')
        ref_dict_all = {
                "I_power_supply": {'time': [0.000, 0.015, 0.016, 1000.0], 'value': [14500.0, 14500.0, 0, 0]},
                "V_cliq_control_1": {'time': [0.000, 0.015, 0.016, 1000.0], 'value': [0.0, 0.0, 2.0, 2.0]},
                "V_cliq_control_2": {'time': [0.000, 0.015, 0.016, 1000.0], 'value': [0.0, 0.0, 1.0, 1.0]},
        }
        list_signals = ['I_power_supply', 'V_cliq_control_2']
        ref_dict_sel = {key: ref_dict_all[key] for key in list_signals}

        # act
        dict_signals_all = get_signals_from_file(file_name)  # When list_signals is not passed, all signals are read
        dict_signals_sel = get_signals_from_file(file_name, list_signals=list_signals)  # When list_signals is passed, only selected signals are read

        # assert
        self.assertDictEqual(ref_dict_all, dict_signals_all)
        self.assertDictEqual(ref_dict_sel, dict_signals_sel)
