import os
import unittest
from pathlib import Path

#import getpass

from steam_sdk.data.DataModelParsimDakota import DataModelParsimDakota
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.parsers.ParserDakota import ParserDakota
from steam_sdk.utils.read_settings_file import read_settings_file
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from tests.TestHelpers import assert_equal_readable_files



class TestDriverAnalysis(unittest.TestCase):


    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Define settings file
        # user_name = getpass.getuser()
        # print(f'AnalysisSTEAM is running on machine with user name: {user_name}')
        # if user_name in ['root', 'MP-WIN-02$']:
        #     user_name = 'SYSTEM'
        # name_file_settings = 'settings.' + user_name + '.yaml'
        # path_settings = Path(self.settings_path / name_file_settings).resolve()
        # print('user_name:          {}'.format(user_name))
        # print('name_file_settings: {}'.format(name_file_settings))
        # print('path_settings:      {}'.format(path_settings))
        #
        # # Read DAKOTA executable from the settings file
        # self.settings = yaml_to_data(path_settings, DataSettings)
        # print('Dakota_path:        {}'.format(self.settings.Dakota_path))
        #
        # self.folder = {}
        # for folder in ['input', 'output']:
        #     self.folder[folder] = Path(Path(f'../parsims/{folder}/Dakota')).resolve()
        #     print(f'{folder} folder: {self.folder[folder]}')
        #     make_folder_if_not_existing(self.folder[folder])

        absolute_path_settings_folder = str(Path(os.path.join(os.getcwd(), '../')).resolve())
        self.settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)  # TODO consider NOT reading the settings file here

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_assemble_IN_from_yaml_multidim_parameter_study(self):
        """
        Test function to test basic input conversion .yaml -> .in
        """
        # arrange
        data_dakota_input_file_path = os.path.join(os.getcwd(), 'input', 'Dakota', 'DAKOTA_input_multidim_parameter_study.yaml')
        dakota_in_output_folder_path = str(Path(os.path.join(os.path.dirname(data_dakota_input_file_path), self.settings.local_Dakota_folder)).resolve())
        make_folder_if_not_existing(dakota_in_output_folder_path)
        output_file_name = 'DAKOTA_output_multidim_parameter_study.in'
        # act
        data_model_dakota: DataModelParsimDakota = yaml_to_data(data_dakota_input_file_path, DataModelParsimDakota)

        ParserDakota.assemble_in_file(data_model_dakota=data_model_dakota, dakota_working_folder=dakota_in_output_folder_path, dakota_file_name=output_file_name)

        # assert
        dakota_in_output_file_path = os.path.join(dakota_in_output_folder_path, output_file_name)
        dakota_in_file_reference_path = os.path.join(os.getcwd(), 'references', 'Dakota', 'DAKOTA_input_multidim_parameter_study_REFERENCE.in')
        assert_equal_readable_files(dakota_in_output_file_path, dakota_in_file_reference_path)

    def test_assemble_IN_from_yaml_optpp_q_newton_study(self):
        """
        Test function to test basic input conversion .yaml -> .in
        """
        # arrange
        data_dakota_input_file_path = os.path.join(os.getcwd(), 'input', 'Dakota', 'DAKOTA_input_optpp_q_newton_study.yaml')
        dakota_in_output_folder_path = str(Path(os.path.join(os.path.dirname(data_dakota_input_file_path), self.settings.local_Dakota_folder)).resolve())
        output_file_name = 'DAKOTA_output_optpp_q_newton_study.in'
        # act
        full_path_file_settings = os.path.join(Path(Path('..')).resolve(), f"settings.{os.getlogin()}.yaml")   # use settings file from the tests folder of the SDK
        settings: DataSettings = yaml_to_data(full_path_file_settings, DataSettings)
        data_model_dakota: DataModelParsimDakota = yaml_to_data(data_dakota_input_file_path, DataModelParsimDakota)

        ParserDakota.assemble_in_file(data_model_dakota=data_model_dakota, dakota_working_folder=dakota_in_output_folder_path, dakota_file_name=output_file_name)

        # assert
        dakota_in_output_file_path = os.path.join(dakota_in_output_folder_path, output_file_name)
        dakota_in_file_reference_path = os.path.join(os.getcwd(), 'references', 'Dakota', 'DAKOTA_output_optpp_q_newton_study_REFERENCE.in')
        assert_equal_readable_files(dakota_in_output_file_path, dakota_in_file_reference_path)

    def test_assemble_IN_from_yaml_coliny_pattern_search(self):
        """
        Test function to test basic input conversion .yaml -> .in
        """
        # arrange
        data_dakota_input_file_path = os.path.join(os.getcwd(), 'input', 'Dakota', 'DAKOTA_input_coliny_pattern_search.yaml')
        dakota_in_output_folder_path = str(Path(os.path.join(os.path.dirname(data_dakota_input_file_path), self.settings.local_Dakota_folder)).resolve())
        make_folder_if_not_existing(dakota_in_output_folder_path)
        output_file_name = 'DAKOTA_output_coliny_pattern_search.in'
        # act
        full_path_file_settings = os.path.join(Path(Path('..')).resolve(), f"settings.{os.getlogin()}.yaml")   # use settings file from the tests folder of the SDK
        settings: DataSettings = yaml_to_data(full_path_file_settings, DataSettings)
        data_model_dakota: DataModelParsimDakota = yaml_to_data(data_dakota_input_file_path, DataModelParsimDakota)

        ParserDakota.assemble_in_file(data_model_dakota=data_model_dakota, dakota_working_folder=dakota_in_output_folder_path, dakota_file_name=output_file_name)

        # assert
        dakota_in_output_file_path = os.path.join(dakota_in_output_folder_path, output_file_name)
        dakota_in_file_reference_path = os.path.join(os.getcwd(), 'references', 'Dakota', 'DAKOTA_output_coliny_pattern_search.in')
        assert_equal_readable_files(dakota_in_output_file_path, dakota_in_file_reference_path)
