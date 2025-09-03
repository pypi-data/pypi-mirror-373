import os
import unittest
from pathlib import Path

from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.data.DataFiQuS import DataFiQuS
from steam_sdk.drivers.DriverFiQuS import DriverFiQuS
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.utils.read_settings_file import read_settings_file
from tests.TestHelpers import assert_equal_yaml


class TestDriverFiQuS(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        self.test_folder = os.path.dirname(__file__)
        os.chdir(self.test_folder)  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        absolute_path_settings_folder = str(Path(os.path.join(os.getcwd(), '../')).resolve())
        self.settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)
        print('FiQuS_path:        {}'.format(self.settings.FiQuS_path))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_runFiQuS(self):
        """
        Run simple FiQuS model to see if it runs.
        """
        test_dict_list = [
            {'magnet_name': 'CCT_1', 'output_files_names': ['selfMutualInductanceMatrix_static.csv']},
            {'magnet_name': 'TEST_CAC_Strand_hexFilaments', 'output_files_names': ['b.pos']},
            #{'magnet_name': 'TEST_CAC_Rutherford', 'output_files_names': ['j.pos']}, # temporary disabled as there have been many changes due to adding E-CLIQ etc.
        ]

        for test_dict in test_dict_list:
            magnet_name = test_dict['magnet_name']
            input_folder_path = os.path.join(self.test_folder, 'input', 'FiQuS', magnet_name)
            print(f'test_runFiQuS input folder path: {input_folder_path}')
            output_folder_path = os.path.join(self.test_folder, 'output', 'FiQuS', magnet_name)
            print(f'test_runFiQuS output folder path: {output_folder_path}')
            df = DriverFiQuS(FiQuS_path=self.settings.FiQuS_path, path_folder_FiQuS_input=input_folder_path,
                             path_folder_FiQuS_output=output_folder_path, GetDP_path=self.settings.GetDP_path, verbose=True)
            reference_folder_path = os.path.join(self.test_folder, 'references', 'FiQuS', magnet_name)
            fdm = yaml_to_data(os.path.join(input_folder_path, f'{magnet_name}.yaml'), DataFiQuS)

            df.run_FiQuS(sim_file_name=magnet_name)

            for output_file_name in test_dict['output_files_names']:
                if fdm.run.type in ['geometry_only']:
                    output_file = os.path.join(output_folder_path, f'Geometry_{fdm.run.geometry}', output_file_name)
                elif fdm.run.type == ['mesh_only']:
                    output_file = os.path.join(output_folder_path, f'Geometry_{fdm.run.geometry}', f'Mesh_{fdm.run.mesh}', output_file_name)
                else:
                    output_file = os.path.join(output_folder_path, f'Geometry_{fdm.run.geometry}', f'Mesh_{fdm.run.mesh}', f'Solution_{fdm.run.solution}', output_file_name)
                print(f'Checking if output file exists: {output_file}')
                self.assertTrue(os.path.exists(output_file))

