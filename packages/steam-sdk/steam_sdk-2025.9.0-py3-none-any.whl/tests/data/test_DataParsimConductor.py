import unittest
import os
import yaml

from steam_sdk.data.DataParsimConductor import DataParsimConductor, ConductorSample, IcMeasurement, Coil
from tests.TestHelpers import assert_equal_yaml


class TestDataParsimConductor(unittest.TestCase):

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
            Check that DataParsimConductor generates a structure with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',      'data_parsim_conductor_TEST.yaml')
        reference_file =  os.path.join('references', 'data_parsim_conductor_REFERENCE.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataParsimConductor = DataParsimConductor()
        with open(generated_file, 'w') as yaml_file:
            yaml.dump(data.model_dump(), yaml_file, default_flow_style=False, sort_keys=False)

        # assert
        # Check that the generated file exists
        self.assertTrue(os.path.isfile(generated_file))

        # Check that the generated file is identical to the reference
        assert_equal_yaml(generated_file, reference_file, check_for_same_order=True)


    def test_writeToFile_all_keys(self):
        """
            Check that DataParsimConductor generates a yaml file with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',      'data_parsim_conductor_TEST_all_keys.yaml')
        reference_file =  os.path.join('references', 'data_parsim_conductor_REFERENCE_all_keys.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataParsimConductor = DataParsimConductor()
        # add all possible keys
        data.Coils['TEST_NAME'] = Coil()
        data.Coils['TEST_NAME'].conductorSamples = ConductorSample()
        data.Coils['TEST_NAME'].conductorSamples.Ic_measurements.append(IcMeasurement())



        with open(generated_file, 'w') as yaml_file:
            yaml.dump(data.model_dump(), yaml_file, default_flow_style=False, sort_keys=False)

        # assert
        # Check that the generated file exists
        self.assertTrue(os.path.isfile(generated_file))
        # Check that the generated file is identical to the reference
        assert_equal_yaml(generated_file, reference_file, check_for_same_order=True)
