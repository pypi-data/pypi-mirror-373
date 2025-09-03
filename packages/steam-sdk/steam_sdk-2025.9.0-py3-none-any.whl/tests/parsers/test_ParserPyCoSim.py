import os
import unittest
from pathlib import Path

from steam_sdk.builders.BuilderCosim import BuilderCosim
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserPyCoSim import ParserPyCoSim
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.read_settings_file import read_settings_file
from tests.TestHelpers import assert_equal_yaml


class TestParserPyCoSim(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        local_PyCosim_folder = os.path.join(os.path.dirname(__file__), 'output', 'PyCoSim')  # Note: This should match the folder set by the setUp() method
        delete_if_existing(local_PyCosim_folder, verbose=True)

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Set settings without reading them from from SDK test settings file
        self.settings = DataSettings(local_PyCoSim_folder='output/output_library/PyCoSim')

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    def test_write_model_PyCoSim(self):
        '''
        Test that the method write_cosim_model() generates a correct .yaml file
        '''
        # arrange
        cosim_name = 'COSIM_NAME_RQX'
        sim_number = 125
        verbose = True
        path_output = str(Path(os.path.join(os.getcwd(), os.path.join(self.settings.local_PyCoSim_folder, 'RQX'))).resolve())
        delete_if_existing(path_output)
        path_model_data = os.path.join('input', 'COSIM', 'TestFile_model_data_write_model_COSIM_LEDET_PSPICE.yaml')
        path_file_name_REFERENCE = os.path.join('references', 'PyCoSim', 'TestFile_write_cosim_model_PyCoSim_REFERENCE.yaml')
        path_file_name_GENERATED = os.path.join(path_output, 'input', f'{cosim_name}_{sim_number}.yaml')

        BC = BuilderCosim(file_model_data=path_model_data, data_settings=self.settings, verbose=verbose)
        pPyCoSim = ParserPyCoSim(BC.cosim_data)
        pPyCoSim.write_cosim_model(full_path_file_name=path_file_name_GENERATED, verbose=verbose)

        # assert
        assert_equal_yaml(path_file_name_REFERENCE, path_file_name_GENERATED, check_for_same_order=True)
