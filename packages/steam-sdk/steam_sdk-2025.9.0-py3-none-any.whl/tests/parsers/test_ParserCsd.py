import os
import unittest

import numpy as np

from steam_sdk.parsers.ParserCsd import get_signals_from_csd
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class TestParserCsd(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'Csd'), verbose=True)


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


    def test_get_signals_from_csd_one_signal(self, max_relative_error=1e-6):
        # arrange
        file_name_input = os.path.join('input', 'test_csd_time.csd')
        selected_signals = ['I(r1_warm)']
        output_path = os.path.join('output', 'Csd', 'test_get_signals_from_csd_one_signal', 'testcsd.csv')
        reference_path = os.path.join('references', 'testcsd_REFERENCE.csv')
        make_folder_if_not_existing(os.path.dirname(output_path))

        # act
        df_signals = get_signals_from_csd(file_name_input, selected_signals)

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


    # def test_get_signals_from_csd_two_signals(self, max_relative_error=1e-6):
    #     return

    def test_get_signals_from_csd_one_signal_and_time(self, max_relative_error=1e-6):
        # arrange
        file_name_input = os.path.join('input', 'test_csd_time.csd')
        selected_signals = ['time', 'I(r1_warm)']
        output_path = os.path.join('output', 'Csd', 'test_get_signals_from_csd_one_signal_and_time', 'testcsd_2.csv')
        reference_path = os.path.join('references', 'testcsd_with_time_REFERENCE.csv')

        # act
        df_signals = get_signals_from_csd(file_name_input, selected_signals)

        # assert
        make_folder_if_not_existing(os.path.dirname(output_path), verbose=False)
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
        print("Files {} and {} differ by less than {}%.".format(output_path, reference_path, max_relative_difference * 100))
