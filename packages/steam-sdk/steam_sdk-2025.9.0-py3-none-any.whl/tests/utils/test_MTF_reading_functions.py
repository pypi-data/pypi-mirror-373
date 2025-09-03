import os
import unittest
from pathlib import Path

from steam_sdk.utils.MTF_reading_functions import read_MTF_equipment
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserYAML import yaml_to_data


class Test_MTF_reading_functions(unittest.TestCase):

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


    def test_read_MTF_equipment(self):
        # Assign the keys read either from permanent-settings or local-settings
        user_name = os.getlogin()
        settings_file = f"settings.{user_name}.yaml"
        full_path_file_settings = os.path.join(Path('../').resolve(), settings_file)
        settings_dict = yaml_to_data(full_path_file_settings)
        settings = DataSettings()
        for name, _ in settings.__dict__.items():
            if name in settings_dict:
                setattr(settings, name, settings_dict[name])
        credentials_file = settings.MTF_credentials_path  # read path to credentials file

        # developers that have not specified a path, skip this test - pipeline never skips it
        if user_name != 'SYSTEM' and not credentials_file:
            print(f'NOTE: Test is skipped because user "{user_name}" has no valid path to a credentials file.')
            self.assertTrue(True)
        else:
            # act
            df = read_MTF_equipment(credentials_file, 'HCMQXFBS01-CR000002')

            # assert
            self.assertEqual(13.2, df.loc[1]['Value'])
            self.assertEqual('mm', df.loc[1]['Unit'])
            self.assertEqual('Key size (centering)', df.loc[1]['Field'])
            self.assertEqual(-4, df.loc[10]['Value'])
            self.assertEqual('MPa', df.loc[10]['Unit'])
            self.assertEqual('Coil azimuthal stress, P4, LE (after centering)', df.loc[10]['Field'])
