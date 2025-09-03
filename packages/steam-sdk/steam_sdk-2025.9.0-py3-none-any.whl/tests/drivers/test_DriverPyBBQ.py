import unittest
import os
from pathlib import Path
import shutil

from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.drivers.DriverPyBBQ import DriverPyBBQ
from steam_sdk.utils.read_settings_file import read_settings_file



class TestDriverPyBBQ(unittest.TestCase):

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


    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    def test_runPyBBQ_fromConductorLibrary_multiple(self):
        '''
            This test runs iteratively the PyBBQ netlists in the provided list.
            Each input file is copied from the local STEAM_SDK test model library.
        '''
        conductor_names = ['MQY_OUT']
        for conductor_name in conductor_names:
            print('Circuit: {}'.format(conductor_name))
            self.runPyBBQ_fromCircuitLibrary(conductor_name=conductor_name)


    def runPyBBQ_fromCircuitLibrary(self, conductor_name = 'MQY_OUT'):
        '''
            This test checks that PyBBQ can be run programmatically using DriverPyBBQ.
            The input file is copied from the local STEAM_SDK test model library.
            The path of PyBBQ executable is set to be the one of the Gitlab runner.
            In order to run this test locally, path_exe should be changed.
        '''

        # arrange
        # Define working folder and make sure dedicated output folder exists
        path_folder_PyBBQ = os.path.join('output', 'PyBBQ', conductor_name)
        path_folder_PyBBQ_input = os.path.join('output', 'PyBBQ', conductor_name, 'input')
        print('path_folder_PyBBQ: {}'.format(path_folder_PyBBQ))
        if not os.path.isdir(path_folder_PyBBQ):
            print("Output folder {} does not exist. Making it now".format(path_folder_PyBBQ))
            Path(path_folder_PyBBQ).mkdir(parents=True)
        if not os.path.isdir(path_folder_PyBBQ_input):
            print("Output folder {} does not exist. Making it now".format(path_folder_PyBBQ_input))
            Path(path_folder_PyBBQ_input).mkdir(parents=True)

        # Copy input file from the STEAM_SDK test model library
        path_one_level_up = Path(os.path.dirname(__file__)).parent
        file_name_input = Path(path_one_level_up / os.path.join('builders', 'model_library', 'conductors', conductor_name, 'output', 'PyBBQ', conductor_name + '.yaml')).resolve()
        name_copied = conductor_name + '_COPIED'
        file_name_local = os.path.join(path_folder_PyBBQ_input, name_copied + '.yaml')
        shutil.copyfile(file_name_input, file_name_local)
        print(f'Simulation file {file_name_local} copied.')

        # Define expected output files, and delete them if they already exist
        expected_files = []
        expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'main' + '.csv'))
        expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'NZPV' + '.csv'))
        expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'temperature' + '.csv'))
        expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'voltage' + '.csv'))
        expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'summary' + '.csv'))
        expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'logfile'))
        # expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'main_results' + '.png'))
        # expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'Critical_current' + '.png'))
        # expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'Current_sharing_at_I_op' + '.png'))
        # expected_files.append(os.path.join(path_folder_PyBBQ, 'output', 'steam_sdk_test', 'NZPV' + '.png'))

        for expected_file in expected_files:
            if os.path.isfile(expected_file):
                os.remove(expected_file)
                print('File {} already existed. It was deleted now.'.format(expected_file))

        # Initialize Driver
        dPyBBQ = DriverPyBBQ(
            path_exe=self.settings.PyBBQ_path,
            path_folder_PyBBQ=path_folder_PyBBQ,
            path_folder_PyBBQ_input=path_folder_PyBBQ_input,
            verbose=True)

        # act - Run model
        output_PyBBQ = dPyBBQ.run_PyBBQ(simFileName=name_copied, outputDirectory='output', test='True')
        # print('output_PyBBQ = {}'.format(output_PyBBQ))

        # assert - Check that simulation generated expected output file
        for expected_file in expected_files:
            print('Expected file: {}'.format(expected_file))
            self.assertTrue(os.path.isfile(expected_file))
