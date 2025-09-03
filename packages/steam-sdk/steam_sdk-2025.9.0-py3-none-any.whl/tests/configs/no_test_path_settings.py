import unittest
import os
from pathlib import Path


class TestDriverLEDET(unittest.TestCase):

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

    def test_runPSPICE_simplest(self):
        '''
            This test checks that the user-specific settings file is present in the tests folder.
        '''

        # arrange
        user_name = os.getlogin()
        name_file_settings = 'settings.' + user_name + '.yaml'
        path_settings = Path(Path('..') / name_file_settings).resolve()
        print('user_name:          {}'.format(user_name))
        print('name_file_settings: {}'.format(name_file_settings))
        print('path_settings:      {}'.format(path_settings))

        # for debugging purposes: write the settings file path in a temporary file
        # with open('temp_path_settings_TO_DELETE.txt', 'w') as file:
        #     file.write(str(path_settings))

        # assert - check that the settings file exists
        self.assertTrue(os.path.isfile(path_settings))




