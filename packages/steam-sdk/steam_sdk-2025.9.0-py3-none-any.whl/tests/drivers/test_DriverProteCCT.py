import os
import shutil
import unittest
from pathlib import Path

from steam_sdk.drivers.DriverProteCCT import DriverProteCCT
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.read_settings_file import read_settings_file


class TestDriverProteCCT(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))
        absolute_path_settings_folder = str(Path(os.path.join(os.getcwd(), '../')).resolve())
        self.settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)
        self.settings.local_ProteCCT_folder = 'output/output_library/ProteCCT'

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    def test_runProteCCT_fromCircuitLibrary_multiple(self):
        '''
            This test runs iteratively the ProteCCT netlists in the provided list.
            Each input file is copied from the local STEAM_SDK test model library.
        '''
        magnet_names = ['MCBRD']
        for magnet_name in magnet_names:
            print('Circuit: {}'.format(magnet_name))
            self.runProteCCT_fromCircuitLibrary(magnet_name=magnet_name)


    def runProteCCT_fromCircuitLibrary(self, magnet_name = 'MCBRD'):
        '''
            This test checks that ProteCCT can be run programmatically using DriverProteCCT.
            The input file is copied from the local STEAM_SDK test model library.
            The path of ProteCCT executable is set to be the one of the Gitlab runner.
            In order to run this test locally, path_exe should be changed.
        '''

        # arrange
        # Define working folder and make sure dedicated output folder exists
        software = 'ProteCCT'
        sim_number = 0
        path_folder_ProteCCT = Path(os.path.join(os.getcwd(), self.settings.local_ProteCCT_folder)).resolve()
        path_folder_ProteCCT_input = os.path.join(path_folder_ProteCCT, 'input')
        path_folder_ProteCCT_output = os.path.join(path_folder_ProteCCT, 'output')
        print('path_folder_ProteCCT: {}'.format(path_folder_ProteCCT_input))
        make_folder_if_not_existing(path_folder_ProteCCT_input)

        # Copy input file from the STEAM_SDK test model library
        file_name_input = Path(Path(os.getcwd()).parent / os.path.join('builders', 'model_library', 'magnets', magnet_name, 'output', software, f'{magnet_name}_{sim_number}.xlsx')).resolve()
        name_copied = f'{magnet_name}_{software}_COPIED'
        file_name_local = os.path.join(path_folder_ProteCCT_input, f'{name_copied}.xlsx')
        shutil.copyfile(file_name_input, file_name_local)
        print(f'Simulation file {file_name_local} copied.')

        # Dictionary with manually-written expected names of ProteCCT output files (one per magnet)
        expected_file_names = {
            'MCBRD': 'MCBRD, I0=394A, TOp=1.9K, tQB=34ms, QI=0.01652, VGnd=529.7V, VEE=532.3V, addedHeCpFrac=0.006, fLoopFactor=0.8',
        }

        # Define expected output files, and delete them if they already exist
        expected_file_xls = os.path.join(path_folder_ProteCCT_output, expected_file_names[magnet_name] + '.xls')
        if os.path.isfile(expected_file_xls):
            os.remove(expected_file_xls)
            print('File {} already existed. It was deleted now.'.format(expected_file_xls))

        # Initialize Driver
        dProteCCT = DriverProteCCT(
            path_exe=self.settings.ProteCCT_path,
            path_folder_ProteCCT=path_folder_ProteCCT,
            verbose=True)
        dProteCCT.run_ProteCCT(simFileName=file_name_local, inputDirectory=path_folder_ProteCCT_input, outputDirectory=path_folder_ProteCCT_output)

        # assert
        print('Expected file: {}'.format(expected_file_xls))
        # self.assertTrue(os.path.isfile(expected_file_xls))  # Note: Assert is disabled in the CI/CD pipeline because the runner can't call ProteCCT (since it uses Excel)
