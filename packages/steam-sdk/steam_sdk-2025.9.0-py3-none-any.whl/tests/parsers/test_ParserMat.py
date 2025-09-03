import os
import unittest

import numpy as np

from steam_sdk.parsers.ParserMat import get_signals_from_mat, get_signals_from_mat_to_dict
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class TestParserMat(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'Mat'), verbose=True)

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


    def test_read_mat(self):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.mat')
        selected_signals = ['time_vector', 'I_CoilSections', 'HotSpotT']

        # act
        df_signals = get_signals_from_mat(file_name, selected_signals)


    def test_check_mat(self, max_relative_error=1e-6):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.mat')
        selected_signals = ['time_vector', 'I_CoilSections']#, 'HotSpotT']
        output_path = os.path.join('output', 'Mat', 'test_check_mat', 'testmat.csv')
        reference_path = os.path.join('references', 'testmat_REFERENCE.csv')
        make_folder_if_not_existing(os.path.dirname(output_path))

        # act
        df_signals = get_signals_from_mat(file_name, selected_signals)

        #assert
        # dictionary = df_signals.to_dict('list')
        # sio.savemat('output\\testmat.mat', dictionary)
        df_signals.to_csv(output_path, index=False)

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


    def test_read_mat_columns(self, max_relative_error=1e-6):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.mat')
        selected_signals = ['time_vector', 'I_QH(:,2)']
        output_path = os.path.join('output', 'Mat', 'test_read_mat_columns', 'testmat_columns.csv')
        reference_path = os.path.join('references', 'testcsv_columns_REFERENCE.csv')
        make_folder_if_not_existing(os.path.dirname(output_path))

        # act
        df_signals = get_signals_from_mat(file_name, selected_signals)

        # assert
        df_signals.to_csv(output_path, index=False)
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
        print("Files {} and {} differ by less than {}%.".format(output_path, reference_path,max_relative_difference * 100))

    def test_get_signals_from_mat_to_dict_different_types(self):
        # arrange
        file_name = os.path.join('input', 'TEST_FILE.mat')
        selected_signals = ['time_vector_params', 'I_PC_LUT', 'nCLIQ', 'DUMMY_MATRIX']
        dict_variable_types = {'time_vector_params': '1D', 'I_PC_LUT': '1D', 'nCLIQ': '0D', 'DUMMY_MATRIX': '2D'}
        expected_dict_signals = {
            'time_vector_params': np.array([-0.04, 5.0e-05, -0.001, -0.00095, 5.0e-05, 0.175, 0.1755, 0.0005, 1.0]),
            'I_PC_LUT': np.array([12300, 12300, 12300, 0]),
            'nCLIQ': 1,
            'DUMMY_MATRIX': np.array([[23, 1231.3], [32, 0.12e-4]]),
        }

        # act
        dict_signals = get_signals_from_mat_to_dict(file_name, selected_signals, dict_variable_types=dict_variable_types)

        # assert
        self.assertListEqual(list(expected_dict_signals.keys()), list(dict_signals.keys()))
        self.assertListEqual(
            expected_dict_signals['time_vector_params'].tolist(), dict_signals['time_vector_params'].tolist())
        self.assertListEqual(expected_dict_signals['I_PC_LUT'].tolist(), dict_signals['I_PC_LUT'].tolist())
        self.assertEqual(expected_dict_signals['nCLIQ'], dict_signals['nCLIQ'])
        self.assertListEqual(expected_dict_signals['DUMMY_MATRIX'].tolist(), dict_signals['DUMMY_MATRIX'].tolist())
