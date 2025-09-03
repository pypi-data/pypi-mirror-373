import unittest
import os
from deepdiff import DeepDiff
import yaml

from steam_sdk.data.DataEventCircuit import DataEventCircuit, Powering, EnergyExtraction, QuenchEvent
from steam_sdk.parsers.ParserYAML import yaml_to_data
from tests.TestHelpers import assert_equal_yaml


class TestDataEventCircuit(unittest.TestCase):

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
            Check that DataEventCircuit generates a structure with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',      'data_event_circuit_TEST.yaml')
        reference_file =  os.path.join('references', 'data_event_circuit_REFERENCE.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataEventCircuit = DataEventCircuit()
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
            Check that DataEventCircuit generates a yaml file with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',     'data_event_circuit_TEST_all_keys.yaml')
        reference_file = os.path.join('references', 'data_event_circuit_REFERENCE_all_keys.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataEventCircuit = DataEventCircuit()
        # add all possible keys
        dict_Powering = {'Powering_1': Powering()}  # example of Powering key
        dict_EnergyExtraction = {'EnergyExtraction_1': EnergyExtraction()}  # example of EnergyExtraction key
        dict_QuenchEvent = {'QuenchEvent_1': QuenchEvent()}  # example of Powering key
        data.PoweredCircuits = dict_Powering
        data.EnergyExtractionSystem = dict_EnergyExtraction
        data.QuenchEvents = dict_QuenchEvent

        with open(generated_file, 'w') as yaml_file:
            yaml.dump(data.model_dump(), yaml_file, default_flow_style=False, sort_keys=False)

        # assert
        # Check that the generated file is identical to the reference
        assert_equal_yaml(reference_file, generated_file)

