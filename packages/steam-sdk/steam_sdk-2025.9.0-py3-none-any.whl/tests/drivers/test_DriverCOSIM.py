import os
import unittest
from pathlib import Path

import yaml

from steam_sdk.drivers.DriverCOSIM import DriverCOSIM


class TestDriverCOSIM(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Define settings file
        user_name = os.getlogin()
        name_file_settings = 'settings.' + user_name + '.yaml'
        path_settings = Path(Path('..') / name_file_settings).resolve()
        print('user_name:          {}'.format(user_name))
        print('name_file_settings: {}'.format(name_file_settings))
        print('path_settings:      {}'.format(path_settings))

        # Read COSIM exe path from the settings file
        with open(path_settings, 'r') as stream:
            settings_dict = yaml.safe_load(stream)
        self.COSIM_path = settings_dict['COSIM_path']
        self.path_folder_COSIM = settings_dict['local_COSIM_folder']
        print('COSIM_path:        {}'.format(self.COSIM_path))
        print('path_folder_COSIM: {}'.format(self.path_folder_COSIM))

        if os.path.isfile(path_settings):
            print('path_settings {} exists '.format(path_settings))
        else:
            print('path_settings {} does not exist '.format(path_settings))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_DriverCOSIM_initialize(self):
        '''
            This test checks that the DriverCOSIM class can be run initialized.
        '''

        # arrange
        COSIM_path = self.COSIM_path
        path_folder_COSIM = self.path_folder_COSIM

        # act
        da = DriverCOSIM(COSIM_path=COSIM_path, path_folder_COSIM=path_folder_COSIM, verbose=True)

        # assert
        self.assertTrue(hasattr(da, 'COSIM_path'))
        self.assertTrue(hasattr(da, 'path_folder_COSIM'))
        self.assertTrue(hasattr(da, 'verbose'))


    def test_DriverCOSIM_make_callString(self):
        '''
            This test checks that the DriverCOSIM class can be run initialized.
        '''

        # arrange
        COSIM_path = self.COSIM_path
        path_folder_COSIM = self.path_folder_COSIM
        model_name = 'DUMMY_MODEL'
        sim_number = 'SIM_NUMBER'
        expected_callString = f'java -jar {COSIM_path} {Path(path_folder_COSIM).resolve()}\{model_name}\{sim_number}\Input\COSIMConfig.json'

        # act
        da = DriverCOSIM(COSIM_path=COSIM_path, path_folder_COSIM=path_folder_COSIM, verbose=True)
        returned_callString = da._make_callString(model_name=model_name, sim_number=sim_number)
        print(f'Returned callString:\n{returned_callString}')

        # Temporary manual test
        # da.run(simulation_name=model_name, sim_number=sim_number, verbose = None, flag_report_LEDET = True)

        # assert
        self.assertEqual(expected_callString, returned_callString)


    # def test_runCOSIM_simplest(self):
    #     '''
    #         This test checks that COSIM can be run programmatically using DriverCOSIM.
    #         The path of COSIM executable is set to be the one of the Gitlab runner.
    #     '''
    #     # TODO Decide whether this test should be setup and added: it requires input files and COSIM to be accessible in the virtual machine used as a Gitlab runner
