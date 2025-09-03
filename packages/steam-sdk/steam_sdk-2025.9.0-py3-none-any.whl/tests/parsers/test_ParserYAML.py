import unittest
import os

from steam_sdk.parsers.ParserYAML import yaml_to_data, dict_to_yaml
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing

class TestParserYAML(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        self.test_folder = os.path.dirname(__file__)
        os.chdir(os.path.dirname(self.test_folder))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))


    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_read_and_write_with_comments(self):

        input_yaml = os.path.join(self.test_folder, 'input', 'YAML', 'commented_input.yaml')
        output_folder = os.path.join(self.test_folder, 'output', 'YAML')
        make_folder_if_not_existing(output_folder)
        output_yaml = os.path.join(output_folder, 'commented_output.yaml')
        data = yaml_to_data(input_yaml, dict)
        print(data)
        dict_to_yaml(data, output_yaml)
