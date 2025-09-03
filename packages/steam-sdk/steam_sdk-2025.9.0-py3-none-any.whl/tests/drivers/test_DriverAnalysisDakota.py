import os
import unittest
from pathlib import Path

from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.data.DataAnalysis import DataAnalysis
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.drivers.DriverAnalysis import DriverAnalysis
from steam_sdk.parsers.ParserYAML import yaml_to_data, model_data_to_yaml
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from tests.TestHelpers import assert_string_in_file


class TestDriverAnalysisDakota(unittest.TestCase):

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

    def test_runAnalysisDakota_FiQuS(self):
        """
        Run simple FiQuS model to see if it runs
        """
        input_folder_path = os.path.join(os.getcwd(), 'input')
        analysis_yaml_path = os.path.join(input_folder_path, "TestFile_AnalysisSTEAM_FiQuS_MQXA.yaml")

        # run non iterable steps
        data_analysis: DataAnalysis = yaml_to_data(analysis_yaml_path, DataAnalysis)
        # data_analysis.WorkingFolders.library_path = str(Path(data_analysis.WorkingFolders.library_path).resolve())
        initial_steps = ['load_model', 'modify_model_for_geometry', 'run_sim_geometry']
        data_analysis.AnalysisStepSequence = initial_steps
        data_analysis.GeneralParameters.relative_path_settings = str(Path(os.path.join(input_folder_path, data_analysis.GeneralParameters.relative_path_settings)).resolve())
        initial_analysis_file_path = f'{analysis_yaml_path[:-5]}_0.yaml'
        model_data_to_yaml(data_analysis, initial_analysis_file_path)

        iterable_analysis_file_path = f'{analysis_yaml_path[:-5]}_1.yaml'
        model_data_to_yaml(data_analysis, iterable_analysis_file_path)

        a = AnalysisSTEAM(initial_analysis_file_path)
        a.run_analysis()

        iterable_steps = ['load_model', 'modify_model_for_geometry', 'modify_model_for_mesh', 'run_sim_mesh',
                          'modify_model_for_solution', 'run_sim_solve']  # skipping step 'run_sim_geometry'
        parameters_file = os.path.join(input_folder_path, "dakota_parameters_file_FiQuS")

        output_folder_path = os.path.join(os.getcwd(), 'output', 'AnalysisFiQuS')
        make_folder_if_not_existing(output_folder_path)
        results_file = os.path.join(output_folder_path, "dakota_results_file_FiQuS.txt")

        da = DriverAnalysis(analysis_yaml_path=iterable_analysis_file_path, iterable_steps=iterable_steps, sim_number_offset=0)

        da.run(parameters_file=parameters_file, results_file=results_file)

        assert_string_in_file(results_file, 'overall_error')


    def test_runAnalysisDakota_LEDET(self):
        """
        Run simple FiQuS model to see if it runs
        """

        input_folder_path = os.path.join(os.getcwd(), 'input')

        analysis_yaml_path = os.path.join(input_folder_path, "TestFile_AnalysisSTEAM_LEDET_SMC.yaml")
        iterable_steps = ['setup_folder', 'makeModel_BM', 'modifyModel_EE', 'RunSim_BM']
        data_analysis: DataAnalysis = yaml_to_data(analysis_yaml_path, DataAnalysis)
        data_analysis.GeneralParameters.relative_path_settings = str(Path(os.path.join(input_folder_path, data_analysis.GeneralParameters.relative_path_settings)).resolve())
        iterable_analysis_file_path = f'{analysis_yaml_path[:-5]}_1.yaml'
        model_data_to_yaml(data_analysis, iterable_analysis_file_path)
        parameters_file = os.path.join(input_folder_path, "dakota_parameters_file_LEDET")

        output_folder_path = os.path.join(os.getcwd(), 'output', 'AnalysisLEDET')
        make_folder_if_not_existing(output_folder_path)
        results_file = os.path.join(output_folder_path, "dakota_results_file_LEDET.txt")
        #reference_file_path = os.path.join(self.test_folder, 'references', 'AnalysisFiQuS', "dakota_results_file_REFERENCE")   # this file is not used, but it is kept as example of the output file.

        da = DriverAnalysis(analysis_yaml_path=iterable_analysis_file_path, iterable_steps=iterable_steps, sim_number_offset = 0)

        da.run(parameters_file=parameters_file, results_file=results_file)

        assert_string_in_file(results_file, 'dummy_value')


