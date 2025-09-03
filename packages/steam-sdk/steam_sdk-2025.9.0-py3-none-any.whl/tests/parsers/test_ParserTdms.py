import unittest
import os
import numpy as np
import matplotlib.pyplot as plt

from steam_sdk.parsers import ParserTdms
from steam_sdk.plotters.PlotterModel import PlotterModel
from steam_sdk.parsers.ParserTdms import ParserTdms
from steam_sdk.utils.clean_NaN_from_signal import clean_NaN_from_signal
from steam_sdk.utils.delete_if_existing import delete_if_existing


class TestParserTdms(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'Tdms'), verbose=True)

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

        # Close all figures
        plt.close('all')


    def test_getspecificSignal(self):

        # Assign
        input_path = os.path.join('input', 'test_file_getSignal_ParserTDMS.tdms')
        reference_path = os.path.join('references', 'specificSignal_REFERENCE')
        output_path = os.path.join('references', 'test_TDMS.csv')

        tdms_file = ParserTdms(input_path)
        reference_array = np.loadtxt(reference_path)

        # Act
        # Print infos if needed
        # tdms_file.printTDMSproperties()
        # tdms_file.printTDMSgroups()

        group_name = 'MF'
        signal_name = 'I(PS_1)_YT111'

        output_signal = tdms_file.get_signal(group_name, signal_name)
        print('Output_signal:', output_signal)

        # Assert
        np.testing.assert_allclose(reference_array, output_signal, rtol=1e-5, atol=0)


    def test_appendColumnToSignalData(self):
        # Assign
        input_path = os.path.join('input', 'test_file_getSignal_ParserTDMS.tdms')
        dictionary_test = {'MF': ['I(PS_1)_YT111', 'U(PS_6)_YT124'], 'Vgnd_Time': ['Vtap_1_212']}
        tdms_file = ParserTdms(input_path)

        # Act
        tdms_file.appendColumnToSignalData(dictionary_test)
        print(tdms_file.signal_data)

        # Assert
        #Get reference data with other method
        reference_array = np.array([[]])
        for group in dictionary_test.keys():
            for channel in dictionary_test[group]:
                if reference_array.size == 0:
                    reference_array = np.atleast_2d(tdms_file.get_signal(group, channel)).T
                else:
                    reference_array = np.column_stack((reference_array, tdms_file.get_signal(group, channel)))

        for i in range(len(dictionary_test.values()) + 1):
            np.testing.assert_allclose(reference_array[i], tdms_file.signal_data[i], rtol=1e-5, atol=0)

    def test_writeTDMSToCsv_semimanual(self, maximum_allowed_rel_error=1e-6):
        # Assign
        input_file = os.path.join('input', 'test_file_getSignal_ParserTDMS.tdms')
        dictionary_test = {'MF': ['I(PS_1)_YT111', 'U(PS_6)_YT124'], 'Vgnd_Time': ['Vtap_1_212']}
        output_file = os.path.join('output', 'Tdms', 'test_writeTDMSToCsv_semimanual', 'test_writeTDMS.csv')
        reference_file = os.path.join('references', 'reference_writeTDMS_1.csv')

        if os.path.isfile(output_file):
            os.remove(output_file)
            print(f'File {output_file} was already present and was deleted. It will be re-written by this test.')

        # Act
        tdms_file = ParserTdms(input_file)
        tdms_file.appendColumnToSignalData(dictionary_test)
        tdms_file.writeTdmsToCsv(output_file, dictionary_test)

        # Assert
        data_generated = np.genfromtxt(output_file, dtype=float, delimiter=',', skip_header=1)
        data_reference = np.genfromtxt(reference_file, dtype=float, delimiter=',', skip_header=1)

        # Check that the number of elements in the generated matrix is the same as in the reference file
        if data_generated.size != data_reference.size:
            raise Exception('Generated csv file does not have the correct size.')

        relative_differences = np.abs(data_generated - data_reference) / data_reference  # Matrix with absolute values of relative differences between the two matrices
        max_relative_difference = np.max(np.max(relative_differences))  # Maximum relative difference in the matrix
        self.assertAlmostEqual(0, max_relative_difference, delta=maximum_allowed_rel_error)  # Check that the maximum relative difference is below
        print("Files {} and {} differ by less than {}%.".format(output_file, reference_file, max_relative_difference * 100))


    def test_convertTDMSToCsv(self, maximum_allowed_rel_error=1e-6):
        # Assign
        input_file = os.path.join('input', 'test_file_getSignal_ParserTDMS.tdms')
        output_file = os.path.join('output', 'Tdms', 'test_convertTDMSToCsv', 'test_writeTDMS.csv')

        # Reference files
        list_reference_files = [
            os.path.join('references', 'convertTdmsToCsv', 'reference_convertTdmsToCsv_MF.csv'),
            os.path.join('references', 'convertTdmsToCsv', 'reference_convertTdmsToCsv_Vgnd_Pos.csv'),
            os.path.join('references', 'convertTdmsToCsv', 'reference_convertTdmsToCsv_Vgnd_Time.csv') ]

        # Expected files
        list_expected_files = [
            os.path.join('output', 'Tdms', 'test_convertTDMSToCsv', 'test_writeTDMS_MF.csv'),
            os.path.join('output', 'Tdms', 'test_convertTDMSToCsv', 'test_writeTDMS_Vgnd_Pos.csv'),
            os.path.join('output', 'Tdms', 'test_convertTDMSToCsv', 'test_writeTDMS_Vgnd_Time.csv')]

        for file in list_expected_files:
            if os.path.isfile(file):
                os.remove(file)
                print(f'File {file} was already present and was deleted. It will be re-written by this test.')

        # Act
        tdms_file = ParserTdms(input_file)
        tdms_file.convertTdmsToCsv(output_file)

        # Assert
        for f, expected_file in enumerate(list_expected_files):
            reference_file = list_reference_files[f]
            data_generated = np.genfromtxt(expected_file,  dtype=float, delimiter=',', skip_header=1)
            data_reference = np.genfromtxt(reference_file, dtype=float, delimiter=',', skip_header=1)

            # Check that the number of elements in the generated matrix is the same as in the reference file
            if data_generated.size != data_reference.size:
                raise Exception('Generated .csv file does not have the correct size.')

            # Substitute 0 with small value to avoid error when dividing by zero
            data_generated[data_generated == 0] = 1e-12
            data_reference[data_reference == 0] = 1e-12

            relative_differences = np.abs(data_generated - data_reference) / data_reference  # Matrix with absolute values of relative differences between the two matrices
            max_relative_difference = np.max(np.max(relative_differences))  # Maximum relative difference in the matrix
            self.assertAlmostEqual(0, max_relative_difference, delta=maximum_allowed_rel_error)  # Check that the maximum relative difference is below
            print("Files {} and {} differ by less than {}%.".format(output_file, reference_file, max_relative_difference * 100))


    def test_time_vector(self):
        #Assign
        input_path = os.path.join('input', 'test_file_getSignal_ParserTDMS.tdms')
        tdms_file = ParserTdms(input_path)
        signal_name = 'U(PS_3)_YT112'
        group_name = 'MF'

        #Act
        time_vec = tdms_file.get_timeVector(group_name, signal_name)
        time_vec_ref = np.arange(- 4.0, - 4.0 + 0.001*24000, 0.001)

        #Assert
        np.testing.assert_allclose(time_vec_ref, time_vec, rtol=0, atol=0)


    def test_plot_TDMS(self):
        # Assign
        input_path = os.path.join('input', 'test_file_getSignal_ParserTDMS.tdms')
        tdms_file = ParserTdms(input_path)

        # Optional Infos
        #ParserTdms.printTDMSgroups(path)

        # Get signal_data
        output_signal = tdms_file.get_signal('MF', 'I(PS_1)_YT111')
        output_time = np.linspace(0, 24, num=len(output_signal))

        #Act
        data = [{'x': output_time.tolist(), 'y': output_signal.tolist(), 'z': list(range(len(output_time)))},
                {'x': output_time.tolist(), 'y': (2 * output_signal).tolist(), 'z': list(range(len(output_time)))},
                {'x': output_time.tolist(), 'y': (2 * output_signal).tolist(), 'z': list(range(len(output_time)))},
                {'x': [0, 1, 2], 'y': [0, 7, 2], 'z': list(range(len(output_time))), 'flag_yscale': 0},
                {'x': [0, 1, 2], 'y': [0, 3, 2], 'z': list(range(len(output_time))), 'flag_yscale': 1},
                {'x': [0, 1, 2], 'y': [50, 35, 12], 'z': list(range(len(output_time))), 'flag_yscale': 3}
                ]
        len_data = len(data)
        titles = ['TEST'] * len_data
        labels = [{'x': 'x', 'y': 'y', 'z': ''},
                  {'x': 'x', 'y': 't', 'z': ''},
                  {'x': 'x', 'y': 't', 'z': 'abc'},
                  {'x': 'x123', 'y': 't1', 'z': ''},
                  {'x': 'x', 'y': 't2', 'z': ''},
                  {'x': 'x', 'y': 't3', 'z': ''}]
        types = ['scatter', 'scatter', 'scatter', 'plot', 'plot', 'plot']
        texts = [{'x': [0], 'y': [0], 't': [1331313133]}] * len_data
        legends = ['Legend1','Legend2','Legend3','Legend4','Legend5','Legend6', ]
        style = [{'color': 'red', 'cmap': None, 'psize': 20, 'pstyle': '|'},
                 {'color': 'red', 'cmap': 'jet', 'psize': 20, 'pstyle': 'D'},
                 {'color': 'green', 'cmap': None, 'psize': 50,'pstyle': '+'},
                 {'color': 'green', 'cmap': None, 'psize': 1, 'pstyle': '-.'},
                 {'color': 'blue', 'cmap': None, 'psize': 5, 'pstyle': '-'},
                 {'color': 'red', 'cmap': None, 'psize': 1, 'pstyle': 'x-.'},]
        window = [1,2,1,3,3,3]
        scale = ['auto'] * len_data
        size = [12, 5]

        PM = PlotterModel()
        PM.plotterModel(data, titles, labels, types, texts, size, legends, style, window, scale)
