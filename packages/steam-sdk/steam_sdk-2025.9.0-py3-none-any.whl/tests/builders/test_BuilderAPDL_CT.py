import os
from pathlib import Path
import unittest


from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.utils.read_settings_file import read_settings_file
from tests.TestHelpers import assert_equal_readable_files


class TestBuilderAPDL_CT(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))
        absolute_path_settings_folder = str(Path(os.path.join(os.getcwd(), '../')).resolve())
        self.settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_APDL_CT_write_file(self, magnet_name='MDP_20T_CT_V28'):
        # arrange - Define output file name. If file already exists, delete it
        sim_name = magnet_name
        sim_number = 28
        output_folder = os.path.join('output', 'APDL_CT')
        path_name_input = os.path.join('model_library', 'magnets', magnet_name, 'input', f'modelData_{magnet_name}.yaml')
        path_name_REFERENCE = os.path.join('references', 'APDL_CT', 'TestFile_APDL_CT_28_REFERENCE.inp')
        path_name_GENERATED = os.path.join(output_folder, 'MDP_20T_CT_V28_28.inp')
        if os.path.isfile(path_name_GENERATED):
            os.remove(path_name_GENERATED)
            print('File {} already existed. It was deleted now.'.format(path_name_GENERATED))

        # act
        BM = BuilderModel(file_model_data=path_name_input, case_model='magnet', data_settings=self.settings, verbose=True)
        BM.buildAPDL_CT(sim_name=sim_name, sim_number=sim_number, output_path=output_folder, flag_plot_all=False)

        # assert
        self.assertTrue(os.path.isfile(path_name_GENERATED))
        print('File {} was generated.'.format(path_name_GENERATED))
        assert_equal_readable_files(path_name_REFERENCE, path_name_GENERATED, n_lines_to_skip_file1=0, n_lines_to_skip_file2=4)
