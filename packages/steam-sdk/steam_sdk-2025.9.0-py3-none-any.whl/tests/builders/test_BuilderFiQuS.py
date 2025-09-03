import unittest
import os
from pathlib import Path

from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.parsers.ParserRoxie import ParserRoxie
from steam_sdk.builders.BuilderFiQuS import BuilderFiQuS
from steam_sdk.parsers.ParserYAML import yaml_to_data


class TestBuilderFiQuS(unittest.TestCase):

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

    def test_BuilderFiQuS_attributes(self):
        # arrange
        magnet_names = ['CCT_1', 'HTS1', 'MQXA', 'MCBRD', 'CAC_Strand_hexFilaments', 'CAC_Rutherford']
        for magnet_name in magnet_names:

            # act
            input_file_path = os.path.join(Path(self.test_folder).parent, 'builders', 'model_library', 'magnets', magnet_name, 'input', 'modelData_' + magnet_name + '.yaml')
            print(f'Testing with input file: {input_file_path}.')

            model_data = yaml_to_data(input_file_path, DataModelMagnet)
            if model_data.GeneralParameters.magnet_type == 'multipole':
                path_data = Path.joinpath(Path(input_file_path).parent, model_data.Sources.coil_fromROXIE).resolve()
                path_cadata = Path.joinpath(Path(input_file_path).parent, model_data.Sources.conductor_fromROXIE).resolve()
                path_iron = Path.joinpath(Path(input_file_path).parent, model_data.Sources.iron_fromROXIE).resolve()
                pR = ParserRoxie()
                roxie_data = pR.getData(dir_data=path_data, dir_cadata=path_cadata, dir_iron=path_iron, path_to_yaml_model_data=input_file_path)
            else:
                roxie_data = RoxieData()
            bF = BuilderFiQuS(model_data=model_data, roxie_data=roxie_data, flag_build=True, verbose=True)

            # assert
            self.assertTrue(hasattr(bF, 'data_FiQuS'))  # check if data_FiQuS in an attribute of BuilderFiQuS
            self.assertTrue(bF.data_FiQuS.magnet.type in ['multipole', 'CCT_straight', 'CWS', 'Pancake3D', 'CACStrand', 'CACRutherford'])  # check if magnet type has been set_up to one of the currently supported types
            if bF.data_FiQuS.magnet.type == 'multipole':
                self.assertTrue(hasattr(bF, 'data_FiQuS_geo'))  # check if additional data_FiQuS_geo required by FiQuS multipole exists
