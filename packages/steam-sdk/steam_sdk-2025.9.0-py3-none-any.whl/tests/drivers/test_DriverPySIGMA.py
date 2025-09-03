import os
import unittest
import subprocess
from pathlib import Path

from steam_sdk.data import DataPySIGMA as dS
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.drivers.DriverPySIGMA import DriverPySIGMA
from steam_pysigma.postprocessing.postprocessing import export_B_field_txt_to_map2d


class TestDriverPysigma(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        self.test_folder = os.path.dirname(__file__)
        # os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Define settings file
        user_name = os.getlogin()
        name_file_settings = 'settings.' + user_name + '.yaml'
        path_settings = Path(Path(self.test_folder).parent / name_file_settings).resolve()
        print('user_name:          {}'.format(user_name))
        print('name_file_settings: {}'.format(name_file_settings))
        print('path_settings:      {}'.format(path_settings))

        self.settings = yaml_to_data(path_settings, DataSettings)

        self.magnet_names = ['MQXA']

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_01_run_PySIGMA(self):
        """
        This simply runs the Comsol model with the version specified in the settings.username.yaml and the entries in the data model
        """
        for magnet_name in self.magnet_names:
            input_folder_path = os.path.join(Path(self.test_folder).parent, 'builders', 'model_library', 'magnets', magnet_name, 'output', 'PySIGMA')
            ds = DriverPySIGMA(path_input_folder=input_folder_path)
            ds.run_PySIGMA(magnet_name)

    def test_02_export_B_txt_to_map2d(self):
        sim_numer = 1

        for magnet_name in self.magnet_names:
            output_folder_path = os.path.join(Path(self.test_folder).parent, 'builders', 'model_library', 'magnets', magnet_name, 'output', 'PySIGMA')
            input_file_path = os.path.join(output_folder_path, f'{magnet_name}_{sim_numer}.yaml')
            dm = yaml_to_data(input_file_path, dS.DataPySIGMA)
            reference_folder_path = os.path.join(Path(self.test_folder).parent, 'builders', 'model_library', 'magnets', magnet_name, 'input')
            path_map2d_roxie_reference = Path(reference_folder_path, dm.Options_SIGMA.postprocessing.out_2D_at_points.map2d).resolve()
            path_result_txt_Bx = os.path.join(output_folder_path, 'output', 'mf.Bx.txt')
            path_result_txt_By = os.path.join(output_folder_path, 'output', 'mf.By.txt')
            path_output_map2d_file = os.path.join(output_folder_path, f'{magnet_name}_SIGMA.map2d')
            export_B_field_txt_to_map2d(path_map2d_roxie_reference, path_result_txt_Bx, path_result_txt_By, path_output_map2d_file)
