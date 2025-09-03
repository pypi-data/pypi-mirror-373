import os
import unittest
from pathlib import Path

from steam_sdk.utils.MTF_reading_functions import read_MTF_equipment
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.utils.read_settings_file import read_settings_file


class Test_MTF_reading_functions(unittest.TestCase):

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

    def test_read_settings_file(self):
        # assign
        absolute_path_settings_folder = '../'

        # act
        data_settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)

        # assert
        print('REMEMBER: for this test to pass, the local settings file must contain all keys defined in the DataSettings class, i.e.')
        print(list(dict(DataSettings()).keys()))

        self.assertListEqual(list(dict(DataSettings()).keys()), list(dict(data_settings).keys()))
        # Check that all values in data_settings are not None
        for key, value in dict(data_settings).items():
            self.assertIsNotNone(value, f"Value for key '{key}' is None")

    def test_read_settings_file_error(self):
        wrong_absolute_path_settings = 'WRONG_PATH'
        with self.assertRaises(Exception) as context:
            data_settings = read_settings_file(absolute_path_settings_folder=wrong_absolute_path_settings, verbose=True)
        self.assertTrue(f'Settings file not found at: {wrong_absolute_path_settings}' in str(context.exception))
        print(f'This exception was correctly raised: {context.exception}')
