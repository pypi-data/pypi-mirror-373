import unittest
import os
from deepdiff import DeepDiff
import yaml

from steam_sdk.data.DataEventMagnet import DataEventMagnet, QuenchHeaterCircuit
from steam_sdk.parsers.ParserYAML import yaml_to_data
from tests.TestHelpers import assert_equal_yaml


class TestDataEventMagnet(unittest.TestCase):

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


    def test_writeToFile_default(self):
        """
            Check that DataEventMagnet generates a structure with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',      'data_event_magnet_TEST.yaml')
        reference_file =  os.path.join('references', 'data_event_magnet_REFERENCE.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataEventMagnet = DataEventMagnet()
        with open(generated_file, 'w') as yaml_file:
            yaml.dump(data.model_dump(), yaml_file, default_flow_style=False, sort_keys=False)

        # assert
        # Check that the generated file exists
        self.assertTrue(os.path.isfile(generated_file))

        # Check that the generated file is identical to the reference
        # TODO: Check that order of the keys is the same
        a = yaml_to_data(generated_file)
        b = yaml_to_data(reference_file)
        ddiff = DeepDiff(a, b, ignore_order=False)
        if len(ddiff) > 0:
            print('Diffence found:')
            [print(ddiff[i]) for i in ddiff]
        self.assertTrue(len(ddiff)==0)


    def test_writeToFile_all_keys(self):
        """
            Check that DataAnalysis generates a yaml file with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',     'data_event_magnet_TEST_all_keys.yaml')
        reference_file = os.path.join('references', 'data_event_magnet_REFERENCE_all_keys.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataEventMagnet = DataEventMagnet()
        # add all possible keys
        dict_QH = {'Quench_Heater_Unit_1': QuenchHeaterCircuit()}  # example of QuenchHeaterCircuit key
        data.QuenchProtection.Quench_Heaters = dict_QH

        with open(generated_file, 'w') as yaml_file:
            yaml.dump(data.model_dump(), yaml_file, default_flow_style=False, sort_keys=False)

        # assert
        # Check that the generated file is identical to the reference
        assert_equal_yaml(reference_file, generated_file)

