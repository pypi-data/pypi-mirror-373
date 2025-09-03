import os
import unittest
from pathlib import Path


from steam_sdk.cosims.CosimPyCoSim import CosimPyCoSim
from steam_sdk.data.DataCoSim import NSTI
from steam_sdk.data.DataFiQuS import DataFiQuS
from steam_sdk.data.DataModelCosim import DataModelCosim
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.read_settings_file import read_settings_file
from tests.TestHelpers import assert_equal_yaml
from steam_sdk.parsers.utils_ParserCosims import template_replace

class TestCosimPyCoSim(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output'), verbose=True)

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located

        # Read settings from SDK test settings file
        absolute_path_settings_folder = str(Path(os.path.join(os.getcwd(), '../')).resolve())
        self.settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)
        self.settings.local_PyCoSim_folder = str(Path('output/output_library/PyCoSim').resolve())

        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_add_nsti_to_file_name(self):
        '''
        Test the method _add_nsti_to_file_name()
        '''
        # arrange
        sim_number = 25
        path_cosim_data = os.path.join(os.getcwd(), 'CCT_FiQuS_LEDET', f'CCT_FiQuS_LEDET_{sim_number}.yaml')
        verbose = True
        pyCOSIM = CosimPyCoSim(file_model_data=path_cosim_data, sim_number=sim_number, data_settings=self.settings,
                               verbose=verbose)
        original_file_name_1 = 'TEST_NAME_01.txt'
        original_file_name_2 = 'TEST_NAME_02.tdms'

        # act+assert 1
        pyCOSIM.nsti = NSTI(pyCOSIM.sim_number, 0, 0, 0)
        self.assertEqual(f'TEST_NAME_01_{pyCOSIM.sim_number}_0_0_0.txt', pyCOSIM._add_nsti_to_file_name(original_file_name_1, pyCOSIM.nsti))
        self.assertEqual(f'TEST_NAME_02_{pyCOSIM.sim_number}_0_0_0.tdms', pyCOSIM._add_nsti_to_file_name(original_file_name_2, pyCOSIM.nsti))
        # act+assert 2
        self.assertEqual(f'TEST_NAME_01_85_3_2_10.txt', pyCOSIM._add_nsti_to_file_name(original_file_name_1, NSTI(85, 3, 2, 10)))
        self.assertEqual(f'TEST_NAME_02_85_3_2_10.tdms', pyCOSIM._add_nsti_to_file_name(original_file_name_2, NSTI(85, 3, 2, 10)))

    # def test_run_PyCoSim_CCT_FiQuS_LEDET(self):
    #     '''
    #     Test writing basic input files for the CCT_COSIM_1 straight CCT magnet co-simulation
    #     '''
    #     # arrange
    #     sim_number = 25
    #     max_relative_error = 1e-6  # Maximum accepted relative error for excel, csv and map2d file comparison
    #     verbose = True
    #
    #     path_cosim_data = os.path.join(os.getcwd(), 'CCT_FiQuS_LEDET', f'CCT_FiQuS_LEDET_{sim_number}.yaml')
    #     cosim_data = yaml_to_data(path_cosim_data, DataModelCosim)
    #
    #     output_path_common = str(Path(os.path.join(os.getcwd(), self.settings.local_PyCoSim_folder, cosim_data.GeneralParameters.cosim_name)).resolve())
    #     self.settings.local_library_path = str(Path(os.path.join(os.path.dirname(path_cosim_data), self.settings.local_library_path)).resolve())
    #     #
    #     # act
    #     pyCOSIM = CosimPyCoSim(file_model_data=path_cosim_data, sim_number=sim_number, data_settings=self.settings,
    #                            verbose=verbose)
    #     pyCOSIM.run()
    #
    #     # --- assert ---
    #     # - FiQuS_A -
    #     # build paths
    #     FiQuS_set_name = 'FiQuS_A'
    #     output_file_path_FiQuS = os.path.join(output_path_common, 'FiQuS', f'{cosim_data.Simulations[FiQuS_set_name].modelName}')
    #     nsti_FiQuS_A = NSTI(sim_number, 0, 0, 0)
    #     output_file_path_FiQuS_A_input_file = os.path.join(output_file_path_FiQuS, f'{cosim_data.Simulations[FiQuS_set_name].modelName}_{nsti_FiQuS_A.n_s_t_i}_FiQuS.yaml')
    #     data_model_FiQuS_A = yaml_to_data(output_file_path_FiQuS_A_input_file, DataFiQuS)
    #     FiQuS_A_brep = f'{data_model_FiQuS_A.magnet.geometry.formers.names[0]}.brep'
    #     FiQuS_A_cond = f'{data_model_FiQuS_A.magnet.geometry.windings.names[0]}.cond'
    #     output_file_path_FiQuS_A_output_brep = os.path.join(output_file_path_FiQuS, f'Geometry_{data_model_FiQuS_A.run.geometry}', FiQuS_A_brep)
    #     output_file_path_FiQuS_A_output_cond = os.path.join(output_file_path_FiQuS, f'Geometry_{data_model_FiQuS_A.run.geometry}', FiQuS_A_cond)
    #     reference_file_paths = os.path.join('references', cosim_data.GeneralParameters.cosim_name)
    #     reference_file_path_FiQuS_A_input_file = os.path.join(reference_file_paths, f'{cosim_data.Simulations[FiQuS_set_name].modelName}_{FiQuS_set_name}_REFERENCE.yaml')
    #     reference_file_path_FiQuS_A_output_brep = os.path.join(reference_file_paths, FiQuS_A_brep)
    #     reference_file_path_FiQuS_A_output_cond = os.path.join(reference_file_paths, FiQuS_A_cond)
    #
    #     # input files the same
    #     assert_equal_yaml(output_file_path_FiQuS_A_input_file, reference_file_path_FiQuS_A_input_file, max_relative_error=max_relative_error)
    #
    #     # output files the same
    #     assert_equal_yaml(output_file_path_FiQuS_A_output_brep, reference_file_path_FiQuS_A_output_brep, max_relative_error=max_relative_error)
    #     assert_equal_yaml(output_file_path_FiQuS_A_output_cond, reference_file_path_FiQuS_A_output_cond, max_relative_error=max_relative_error)
    #
    #     # - FiQuS_B -
    #     # build paths
    #     FiQuS_set_name = 'FiQuS_B'
    #     output_file_path_FiQuS = os.path.join(output_path_common, 'FiQuS', f'{cosim_data.Simulations[FiQuS_set_name].modelName}')
    #     nsti_FiQuS_B = NSTI(sim_number, 1, 0, 0)
    #     output_file_path_FiQuS_B_input_file =  os.path.join(output_file_path_FiQuS, f'{cosim_data.Simulations[FiQuS_set_name].modelName}_{nsti_FiQuS_B.n_s_t_i}_FiQuS.yaml')
    #     data_model_FiQuS_B = yaml_to_data(output_file_path_FiQuS_B_input_file, DataFiQuS)
    #     FiQuS_B_brep = f'{data_model_FiQuS_B.magnet.geometry.conductors.file_names[0]}_{data_model_FiQuS_B.magnet.geometry.formers.file_names[0]}_fused.brep'
    #     FiQuS_B_cond = f'{data_model_FiQuS_B.magnet.geometry.conductors.file_names_large[0]}.cond'
    #     output_file_path_FiQuS_B_output_brep = os.path.join(output_file_path_FiQuS, f'Geometry_{data_model_FiQuS_B.run.geometry}', FiQuS_B_brep)
    #     output_file_path_FiQuS_B_output_cond = os.path.join(output_file_path_FiQuS, f'Geometry_{data_model_FiQuS_B.run.geometry}', FiQuS_B_cond)
    #     reference_file_paths = os.path.join('references', cosim_data.GeneralParameters.cosim_name)
    #     reference_file_path_FiQuS_B_input_file = os.path.join(reference_file_paths, f'{cosim_data.Simulations[FiQuS_set_name].modelName}_{FiQuS_set_name}_REFERENCE.yaml')
    #     reference_file_path_FiQuS_B_output_brep = os.path.join(reference_file_paths, FiQuS_B_brep)
    #     reference_file_path_FiQuS_B_output_cond = os.path.join(reference_file_paths, FiQuS_B_cond)
    #
    #     # input files the same
    #     assert_equal_yaml(output_file_path_FiQuS_B_input_file, reference_file_path_FiQuS_B_input_file, max_relative_error=max_relative_error)
    #
    #     # output files the same
    #     #assert_equal_yaml(output_file_path_FiQuS_B_output_brep, reference_file_path_FiQuS_B_output_brep, max_relative_error=max_relative_error) # this causes issue on the runner, skipping for now.
    #     assert_equal_yaml(output_file_path_FiQuS_B_output_cond, reference_file_path_FiQuS_B_output_cond, max_relative_error=max_relative_error)
    #
    #     # assert - LEDET - input files the same
    #     LEDET_set_name = 'LEDET_A'
    #     nsti_LEDET_A = NSTI(sim_number, 2, 0, 0)
    #     output_file_path_LEDET = os.path.join(output_path_common, 'LEDET', str(nsti_LEDET_A.n), cosim_data.Simulations[LEDET_set_name].modelName, 'Input', f'{cosim_data.Simulations[LEDET_set_name].modelName}_{nsti_LEDET_A.n_s_t_i}.yaml')
    #     reference_file_path_LEDET = os.path.join(reference_file_paths, f'{cosim_data.Simulations[LEDET_set_name].modelName}_{LEDET_set_name}_REFERENCE.yaml')
    #     assert_equal_yaml(output_file_path_LEDET, reference_file_path_LEDET, max_relative_error=max_relative_error)
    #     # self.assertTrue(os.path.isfile(os.path.join(output_path_common, 'LEDET', 'Field maps', cosim_data.Simulations[LEDET_set_name].modelName, f'{cosim_data.Simulations[LEDET_set_name].modelName}_All_WithIron_WithSelfField.map2d')))  # Field map is not generated by this test
    #
    #     if cosim_data.Simulations[FiQuS_set_name].PreCoSim.files_to_copy_after_time_window[0].target_file_name_relative_path == 'Input/<<modelName>>_selfMutualInductanceMatrix_<<n>>.csv':
    #         target_file_name_relative_path = f'Input/{cosim_data.Simulations[FiQuS_set_name].modelName}_selfMutualInductanceMatrix_{sim_number}.csv'
    #     else:
    #         raise Exception(f'The hardcoded logic in test_run_PyCoSim_CCT_FiQuS_LEDET needs editing')
    #
    #     path_to_check = os.path.join(output_path_common, 'LEDET', str(nsti_LEDET_A.n),
    #                                                 cosim_data.Simulations[LEDET_set_name].modelName,
    #                                                 target_file_name_relative_path)
    #
    #     print(path_to_check)
    #     self.assertTrue(os.path.isfile(path_to_check))  # this entry matches the entry from the FiQuS model (not LEDET)
    #     # assert - LEDET output .mat files exist
    #     list_nsti = [NSTI(sim_number, 2, 0, 0), NSTI(sim_number, 2, 1, 0), NSTI(sim_number, 2, 1, 1), NSTI(sim_number, 2, 2, 0)]
    #     for nsti_LEDET_A in list_nsti:
    #         path_to_check = os.path.join(output_path_common, 'LEDET', str(nsti_LEDET_A.n),
    #                                                 cosim_data.Simulations[LEDET_set_name].modelName,
    #                                                 'Output', 'Mat Files', f'SimulationResults_LEDET_{nsti_LEDET_A.n_s_t_i}.mat')
    #         print(path_to_check)
    #         self.assertTrue(os.path.isfile(path_to_check))


    # def test_run_PyCoSim_COSIM_NAME_ABC(self):
    #     '''
    #     Test that the method write_cosim_model() generates a correct .json file
    #     '''
    #     # arrange
    #     sim_number = 25
    #     max_relative_error = 1e-6  # Maximum accepted relative error for excel, csv and map2d file comparison
    #     verbose = True
    #
    #     path_cosim_data = os.path.join('local_PyCoSim_folder', 'COSIM_NAME_ABC', 'COSIM_NAME_ABC_25.yaml')
    #     cosim_data: DataModelCosim = yaml_to_data(path_cosim_data, DataModelCosim)
    #     output_path_common = os.path.join('output', 'PyCoSim', cosim_data.GeneralParameters.cosim_name)
    #     delete_if_existing(output_path_common) # TODO uncomment
    #
    #     FiQuS_set_name = 'FiQuS_A'
    #     nsti_FiQuS_A = NSTI(sim_number, 0, 0, 0)
    #     output_file_path_FiQuS = os.path.join(output_path_common, 'FiQuS', f'{cosim_data.Simulations[FiQuS_set_name].modelName}')
    #     output_file_path_FiQuS_input_file =  os.path.join(output_file_path_FiQuS, f'{cosim_data.Simulations[FiQuS_set_name].modelName}_{nsti_FiQuS_A.n_s_t_i}_FiQuS.yaml')
    #
    #     LEDET_set_name = 'LEDET_A'
    #     nsti = NSTI(sim_number, 1, 0, 0)
    #     output_file_path_LEDET_input_file =  os.path.join(output_path_common, 'LEDET', str(nsti.n), cosim_data.Simulations[LEDET_set_name].modelName, 'Input', f'{cosim_data.Simulations[LEDET_set_name].modelName}_{nsti.n_s_t_i}.yaml')
    #
    #     reference_file_paths = os.path.join('references', cosim_data.GeneralParameters.cosim_name)
    #     reference_file_path_FiQuS = os.path.join(reference_file_paths, f'{cosim_data.Simulations[FiQuS_set_name].modelName}_FiQuS_REFERENCE.yaml')
    #     reference_file_path_LEDET = os.path.join(reference_file_paths, f'{cosim_data.Simulations[LEDET_set_name].modelName}_LEDET_REFERENCE.yaml')
    #
    #     # act
    #     pyCOSIM = CosimPyCoSim(file_model_data=path_cosim_data, sim_number=sim_number, data_settings=self.data_settings,
    #                            verbose=verbose)
    #     pyCOSIM.run()
    #
    #     # assert - check inputs
    #     assert_equal_yaml(output_file_path_FiQuS_input_file, reference_file_path_FiQuS, max_relative_error=max_relative_error)
    #     assert_equal_yaml(output_file_path_LEDET_input_file, reference_file_path_LEDET, max_relative_error=max_relative_error)
    #
    #     # assert - check outputs
    #     # TODO
