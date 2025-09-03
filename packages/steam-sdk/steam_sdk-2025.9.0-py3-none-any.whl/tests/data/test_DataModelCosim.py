import os
import unittest

from deepdiff import DeepDiff

from steam_sdk.data.DataModelCosim import DataModelCosim, sim_FiQuS, sim_XYCE, sim_PSPICE, sim_LEDET, CosimPort, \
    CosimPortModel, CosimPortVariable, FileToCopy, VariableToCopy
from steam_sdk.parsers.ParserYAML import dict_to_yaml, yaml_to_data


class TestDataCosim(unittest.TestCase):

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


    def test_writeToFile_cosim(self):
        """
            Check that DataModelCosim generates a structure with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',      'data_model_cosim_TEST.yaml')
        reference_file =  os.path.join('references', 'data_model_cosim_REFERENCE.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataModelCosim = DataModelCosim()
        dict_to_yaml(data.model_dump(), generated_file, list_exceptions=['PortDefinition'])

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


    def test_writeToFile_cosim_all_keys(self):
        """
            Check that DataModelCosim generates a structure with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',      'data_model_cosim_TEST_all_keys.yaml')
        reference_file =  os.path.join('references', 'data_model_cosim_REFERENCE_all_keys.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataModelCosim = DataModelCosim()
        data.Simulations['FiQuS_1'] = sim_FiQuS(type='FiQuS')
        data.Simulations['FiQuS_1'].PreCoSim.files_to_copy_after_time_window = [FileToCopy()]
        data.Simulations['FiQuS_1'].PreCoSim.variables_to_copy_after_time_window = [VariableToCopy()]
        data.Simulations['FiQuS_1'].CoSim.files_to_copy_after_iteration = [FileToCopy()]
        data.Simulations['FiQuS_1'].CoSim.variables_to_copy_after_time_window = [VariableToCopy()]
        data.Simulations['FiQuS_1'].PostCoSim.files_to_copy_after_time_window = [FileToCopy()]
        data.Simulations['FiQuS_1'].PostCoSim.variables_to_copy_after_time_window = [VariableToCopy()]
        data.Simulations['LEDET_1'] = sim_LEDET(type='LEDET')
        data.Simulations['PSPICE_1'] = sim_PSPICE(type='PSPICE')
        data.Simulations['XYCE_1'] = sim_XYCE(type='XYCE')
        data.Options_COSIM.PortDefinition['port_1'] = CosimPort()
        data.Options_COSIM.PortDefinition['port_1'].Models['model_1'] = CosimPortModel()
        data.Options_COSIM.PortDefinition['port_1'].Models['model_1'].inputs['input_1'] = CosimPortVariable()
        data.Options_COSIM.PortDefinition['port_1'].Models['model_1'].outputs['output_1'] = CosimPortVariable()
        dict_to_yaml(data.model_dump(), generated_file, list_exceptions=['PortDefinition'])

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