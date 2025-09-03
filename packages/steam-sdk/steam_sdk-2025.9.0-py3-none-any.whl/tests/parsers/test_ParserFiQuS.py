import unittest
import os
from pathlib import Path

from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.builders.BuilderFiQuS import BuilderFiQuS
from steam_sdk.parsers.ParserRoxie import ParserRoxie
from steam_sdk.parsers.ParserFiQuS import ParserFiQuS
from steam_sdk.parsers.ParserYAML import yaml_to_data
from tests.TestHelpers import assert_equal_yaml

class TestParserFiQuS(unittest.TestCase):

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

    def test_ParserFiQuS_write_yaml_file(self):

        # arrange
        magnet_names = ['CAC_Rutherford', 'CAC_Strand_hexFilaments', 'CCT_1', 'HTS1', 'MCBRD', 'MQXA', 'FALCOND_C_ESC']
        #magnet_names = ['FALCOND_C_ESC']
        append_to_magnet_name = '_FiQuS'
        software = 'FiQuS'
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

            output_file_base_path = os.path.join(self.test_folder, 'output', software, magnet_name)
            pF = ParserFiQuS(builder_FiQuS=bF, verbose=True)
            pF.writeFiQuS2yaml(output_path=output_file_base_path, append_str_to_magnet_name=append_to_magnet_name)

            # assert
            for file_ext in pF.file_exts:
                output_file = os.path.join(output_file_base_path, f'{magnet_name}{append_to_magnet_name}.{file_ext}')
                reference_file = os.path.join(self.test_folder, 'references', software, magnet_name, f'{magnet_name}_REFERENCE.{file_ext}')
                assert_equal_yaml(reference_file, output_file)



