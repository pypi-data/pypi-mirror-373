import unittest
import os
import yaml
from deepdiff import DeepDiff

from steam_sdk.data import DataRoxieParser as rp
from steam_sdk.parsers.ParserYAML import yaml_to_data


class TestModelData(unittest.TestCase):

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

    def test_writeToFile_RoxieData(self):
        """
            Check that DataModelMagnet generates a structure with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',     'roxie_data_TEST.yaml')
        reference_file = os.path.join('references', 'roxie_data_REFERENCE.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: rp.RoxieData = rp.RoxieData()
        with open(generated_file, 'w') as yaml_file:
            # ruamel.yaml.dump(data.dict(), yaml_file, default_flow_style=False)
            yaml.dump(data.dict(), yaml_file, default_flow_style=False, sort_keys=False)

        # assert
        # Check that the generated file exists
        self.assertTrue(os.path.isfile(generated_file))

        # Check that the generated file is identical to the reference
        # TODO: Check that order of the keys is the same
        a = yaml_to_data(generated_file)
        b = yaml_to_data(reference_file)
        ddiff = DeepDiff(a, b, ignore_order=False)
        self.assertTrue(len(ddiff)==0)
