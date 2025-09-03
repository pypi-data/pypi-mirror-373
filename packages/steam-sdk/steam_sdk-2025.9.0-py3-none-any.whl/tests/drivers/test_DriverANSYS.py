import os
import unittest
from pathlib import Path

import yaml

from steam_sdk.drivers.DriverANSYS import DriverANSYS


class TestDriverANSYS(unittest.TestCase):

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

        # Read ANSYS exe path from the settings file
        with open(path_settings, 'r') as stream:
            settings_dict = yaml.safe_load(stream)
        self.ANSYS_path = settings_dict['ANSYS_path']
        print('ANSYS_path:        {}'.format(self.ANSYS_path))

        if os.path.isfile(path_settings):
            print('path_settings {} exists '.format(path_settings))
        else:
            print('path_settings {} does not exist '.format(path_settings))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_DriverANSYS_initialize(self):
        '''
            This test checks that the DriverANSYS class can be run initialized.
        '''

        # arrange
        ANSYS_path = self.ANSYS_path
        input_file = 'DUMMY_INPUT_FILE.inp'

        # act
        da = DriverANSYS(ANSYS_path=ANSYS_path, input_file=input_file,
                         output_file='DUMMY_OUTPUT_FILE.txt', directory=os.path.dirname(input_file),
                         jobname='file', memory='2048', reserve='1024', n_processors=1, verbose=True)

        # assert
        self.assertTrue(hasattr(da, 'ANSYS_path'))
        self.assertTrue(hasattr(da, 'input_file'))
        self.assertTrue(hasattr(da, 'output_file'))
        self.assertTrue(hasattr(da, 'directory'))
        self.assertTrue(hasattr(da, 'jobname'))
        self.assertTrue(hasattr(da, 'memory'))
        self.assertTrue(hasattr(da, 'reserve'))
        self.assertTrue(hasattr(da, 'n_processors'))
        self.assertTrue(hasattr(da, 'verbose'))


    def test_DriverANSYS_make_callString(self):
        '''
            This test checks that the DriverANSYS class can be run initialized.
        '''

        # arrange
        ANSYS_path = self.ANSYS_path
        input_file = 'DUMMY_INPUT_FILE.inp'
        output_file = 'DUMMY_OUTPUT_FILE.txt'
        directory = os.path.dirname(input_file)
        jobname = 'file'
        memory = '2048'
        reserve = '1024'
        n_processors = 1
        expected_callString = f'\"{ANSYS_path}\" -p ansys -dir \"{directory}\" -j \"{jobname}\" -s noread ' +  f'-m {memory} -db {reserve} -t -d win32 -b -i \"{input_file}\" ' + f'-o \"{output_file}\" -smp -np {n_processors}'

        # act
        da = DriverANSYS(ANSYS_path=ANSYS_path, input_file=input_file, output_file=output_file, directory=directory,
                         jobname=jobname, memory=memory, reserve=reserve, n_processors=n_processors, verbose=True)
        returned_callString = da._make_callString()
        print(f'Returned callString:\n{returned_callString}')

        # assert
        self.assertEqual(expected_callString, returned_callString)


    # def test_runANSYS_simplest(self):
    #     '''
    #         This test checks that ANSYS can be run programmatically using DriverANSYS.
    #         The path of ANSYS executable is set to be the one of the Gitlab runner.
    #         In order to run this test locally, path_exe should be changed.
    #     '''
    #
    #     # arrange
    #     ANSYS_path = self.ANSYS_path
    #     input_file = os.path.join('input', 'DUMMY_INPUT_FILE.inp')
    #
    #     # act
    #     da = DriverANSYS(ANSYS_path=ANSYS_path, input_file=input_file,
    #                     output_file='DUMMY_OUTPUT_FILE.txt', directory=os.path.dirname(input_file),
    #                     jobname='file', memory='2048', reserve='1024', n_processors=1, verbose=True)
    #     da.run()
    #
    #     # TODO Decide whether this test should be setup and added: it requires input files and ANSYS to be installed in the virtual machine used as a Gitlab runner
