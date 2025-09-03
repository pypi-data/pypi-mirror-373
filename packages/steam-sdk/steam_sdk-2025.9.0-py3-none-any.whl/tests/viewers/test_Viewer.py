import shutil
import unittest
import os
import matplotlib.pyplot as plt

from steam_sdk.data.DataSignal import Configuration
from steam_sdk.viewers.Viewer import Viewer


class TestViewer(unittest.TestCase):

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

    def test_initialize_without_analysis(self):
        file_name_transients = os.path.join('input', 'file_name_transients_TEST.csv')
        V = Viewer(file_name_transients, verbose=True, list_events=[], flag_analyze=False) # if list_events is empty it reads all the rows in the file
        # These keys must be present
        self.assertTrue(hasattr(V, 'dict_events'))
        self.assertTrue(hasattr(V, 'list_events'))
        self.assertTrue(hasattr(V, 'verbose'))
        self.assertTrue(hasattr(V, 'dict_configs'))
        self.assertTrue(hasattr(V, 'dict_figures'))
        self.assertTrue('MBRD_1' in V.dict_configs)
        self.assertTrue(V.figure_types == 'png')
        print(V.dict_configs['MBRD_1'])
        # These keys must not be present


    def test_initialize_and_run_analysis(self):
        # arrange - input file
        file_name_transients = os.path.join('input', 'file_name_transients_TEST.csv')
        # arrange - expected output csv
        path_expected_meas_csv_folder = os.path.join(
            'output',
            'STEAM_CONVERTED_MEAS_REPO',
            'EXAMPLE_TEST_CAMPAIGN_NAME',)
        full_path_expected_converted_csv_file = os.path.join(path_expected_meas_csv_folder, 'EXAMPLE_TEST_NAME_2_MF.csv')
        # arrange - expected output png
        output_figure_folder = os.path.join('output', 'STEAM_ANALYSIS_OUTPUT')
        list_expected_figures = [
            os.path.join('case meas', 'case meas_measured_current'),
            os.path.join('case meas', 'case meas_measured_voltage'),
            os.path.join('case sim', 'case sim_simulated_current'),
            os.path.join('case sim', 'case sim_simulated_voltage'),
            os.path.join('case sim', 'case sim_simulated_U1_U2'),
            os.path.join('case meas+sim', 'case meas+sim_I_meas_cpr_sim'),
            os.path.join('case meas+sim', 'case meas+sim_Umeas_Imeas'),
        ]
        # arrange - expected html output
        path_output_html_report = os.path.join('output', 'STEAM_ANALYSIS_OUTPUT', 'output_html_report.html')

        # Delete folder and files that are already present
        if os.path.isdir(path_expected_meas_csv_folder):
            shutil.rmtree(path_expected_meas_csv_folder)
            print(f'Folder {path_expected_meas_csv_folder} was already present and was deleted. It will be re-written by this test.')
        if os.path.isdir(output_figure_folder):
            shutil.rmtree(output_figure_folder)
            print(f'Folder {output_figure_folder} was already present and was deleted. It will be re-written by this test.')
        if os.path.isdir(os.path.dirname(path_output_html_report)):
            print(f'Folder {os.path.isdir(os.path.dirname(path_output_html_report))} was already present and was deleted. It will be re-written by this test.')

        # act
        V = Viewer(file_name_transients, verbose=True, list_events=[], flag_display=False, flag_save_figures=True,
                   path_output_html_report=path_output_html_report, figure_types='svg')  # if list_events is empty it reads all the rows in the file

        # assert 1: check the object structure and key values
        # These keys must be present
        self.assertTrue(hasattr(V, 'dict_events'))
        self.assertTrue(hasattr(V, 'list_events'))
        self.assertTrue(hasattr(V, 'verbose'))
        self.assertTrue(hasattr(V, 'dict_configs'))
        self.assertTrue(hasattr(V, 'dict_figures'))
        # These dictionary keys must be present
        self.assertTrue('MBRD_1' in V.dict_configs)
        self.assertTrue(hasattr(V.dict_configs['MBRD_1'], 'SignalList'))
        self.assertTrue(hasattr(V.dict_configs['MBRD_1'].SignalList['measured_current'], 'meas_label'))

        # Check the type of these keys
        self.assertTrue(type(V.dict_configs) == dict)
        self.assertTrue(type(V.dict_configs['MBRD_1']) == Configuration)
        self.assertTrue(type(V.dict_configs['MBRD_1'].SignalList) == dict)
        self.assertTrue(type(V.dict_figures) == dict)

        # assert 2: check that the converted csv file exists
        self.assertTrue(os.path.isfile(full_path_expected_converted_csv_file))

        # assert 3: check that the generated .png figures exist
        for fig in list_expected_figures:
            self.assertTrue(os.path.isfile(os.path.join(output_figure_folder, f'{fig}.svg')))

        # assert 4: check values
        self.assertListEqual(V.dict_figures['case meas'], ['case meas_measured_current', 'case meas_measured_voltage'])
        self.assertListEqual(V.dict_figures['case sim'], ['case sim_simulated_current', 'case sim_simulated_voltage', 'case sim_simulated_U1_U2'])
        self.assertListEqual(V.dict_figures['case meas+sim'], ['case meas+sim_I_meas_cpr_sim', 'case meas+sim_Umeas_Imeas'])

        # assert 5: check that the generated .html report exists
        self.assertTrue(os.path.isfile(path_output_html_report))


    def test_initialize_and_run_analysis_with_pdf_report(self):
        # arrange - input file
        file_name_transients = os.path.join('input', 'file_name_transients_TEST.csv')
        # arrange - expected output csv
        path_expected_meas_csv_folder = os.path.join(
            'output',
            'STEAM_CONVERTED_MEAS_REPO',
            'EXAMPLE_TEST_CAMPAIGN_NAME',)
        full_path_expected_converted_csv_file = os.path.join(path_expected_meas_csv_folder, 'EXAMPLE_TEST_NAME_2_MF.csv')
        # arrange - expected output png
        output_figure_folder = os.path.join('output', 'STEAM_ANALYSIS_OUTPUT')
        list_expected_figures = [
            os.path.join('case meas', 'case meas_measured_current'),
            os.path.join('case meas', 'case meas_measured_voltage'),
            os.path.join('case sim', 'case sim_simulated_current'),
            os.path.join('case sim', 'case sim_simulated_voltage'),
            os.path.join('case sim', 'case sim_simulated_U1_U2'),
            os.path.join('case meas+sim', 'case meas+sim_I_meas_cpr_sim'),
            os.path.join('case meas+sim', 'case meas+sim_Umeas_Imeas'),
        ]
        # arrange - expected pdf output
        path_output_pdf_report = os.path.join('output', 'STEAM_ANALYSIS_OUTPUT', 'output_pdf_report.pdf')

        # Delete folder and files that are already present
        if os.path.isdir(path_expected_meas_csv_folder):
            shutil.rmtree(path_expected_meas_csv_folder)
            print(f'Folder {path_expected_meas_csv_folder} was already present and was deleted. It will be re-written by this test.')
        if os.path.isdir(output_figure_folder):
            shutil.rmtree(output_figure_folder)
            print(f'Folder {output_figure_folder} was already present and was deleted. It will be re-written by this test.')
        if os.path.isdir(os.path.dirname(path_output_pdf_report)):
            print(f'Folder {os.path.isdir(os.path.dirname(path_output_pdf_report))} was already present and was deleted. It will be re-written by this test.')

        # act
        V = Viewer(file_name_transients, verbose=True, list_events=[], flag_display=False, flag_save_figures=True,
                   path_output_pdf_report=path_output_pdf_report, figure_types='png')  # if list_events is empty it reads all the rows in the file

        # assert: check that the generated .pdf report exists
        self.assertTrue(os.path.isfile(path_output_pdf_report))