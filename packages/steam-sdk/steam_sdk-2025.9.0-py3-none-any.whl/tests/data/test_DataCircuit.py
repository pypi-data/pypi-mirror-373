import unittest
import os
from deepdiff import DeepDiff
from steam_sdk.parsers.ParserYAML import dict_to_yaml

from steam_sdk.data.DataModelCircuit import DataModelCircuit
from steam_sdk.parsers.ParserYAML import yaml_to_data


class TestDataCircuit(unittest.TestCase):

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
            Check that DataModelCircuit generates a structure with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',      'data_circuit_TEST.yaml')
        reference_file = os.path.join('references', 'data_model_circuit_REFERENCE.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataModelCircuit = DataModelCircuit()
        dict_to_yaml(data.model_dump(), generated_file, list_exceptions=['Conductors'])

        # assert
        # Check that the generated file exists
        self.assertTrue(os.path.isfile(generated_file))

        # Check that the generated file is identical to the reference
        # TODO: Check that order of the keys is the same
        a = yaml_to_data(generated_file)
        b = yaml_to_data(reference_file)
        ddiff = DeepDiff(a, b, ignore_order=False)
        if len(ddiff) > 0:
            [print(ddiff[i]) for i in ddiff]
        self.assertTrue(len(ddiff)==0)


    def test_loadYamlFile(self):
        """
            Check that a yaml file can be loaded
        """
        # arrange
        reference_file =  os.path.join('references', 'data_model_circuit_REFERENCE.yaml')

        # act
        cicuit_input = yaml_to_data(reference_file, data_class=DataModelCircuit)

        # assert - Check that the 1st-level keys are present
        print(cicuit_input)
        self.assertIn('GeneralParameters', {**cicuit_input.__annotations__})
        self.assertIn('AuxiliaryFiles', {**cicuit_input.__annotations__})
        self.assertIn('Stimuli', {**cicuit_input.__annotations__})
        self.assertIn('Libraries', {**cicuit_input.__annotations__})
        self.assertIn('GlobalParameters', {**cicuit_input.__annotations__})
        self.assertIn('Netlist', {**cicuit_input.__annotations__})
        self.assertIn('Options', {**cicuit_input.__annotations__})
        self.assertIn('Analysis', {**cicuit_input.__annotations__})
        self.assertIn('BiasPoints', {**cicuit_input.__annotations__})
        self.assertIn('PostProcess', {**cicuit_input.__annotations__})
