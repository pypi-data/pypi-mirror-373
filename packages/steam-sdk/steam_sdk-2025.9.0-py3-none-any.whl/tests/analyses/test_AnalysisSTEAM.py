import io
import os
import shutil
import unittest
from pathlib import Path

import matplotlib.pyplot as plt

from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.data.DataAnalysis import DataAnalysis, ModifyModelMultipleVariables
from steam_sdk.data.DataSignal import Configuration
from steam_sdk.parsers.ParserLEDET import ParserLEDET, CompareLEDETParameters
from steam_sdk.parsers.ParserPSPICE import ParserPSPICE
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.read_settings_file import read_settings_file
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from tests.TestHelpers import assert_equal_readable_files, assert_equal_yaml


class TestAnalysisSTEAM(unittest.TestCase):

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
        self.test_folder = os.path.dirname(__file__)
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:        {}'.format(self.current_path))
        print('Test is run from folder: {}'.format(os.getcwd()))


    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

        # Close all figures
        plt.close('all')

    # def test_AnalysisSTEAM_exceptionMissingAnalysisFile(self):
    #     """
    #         Check that AnalysisSTEAM object raises an exception if the input file is not defined
    #     """
    #     # act + assert
    #     pass  # this test is disabled as analysis file input has been changed from optional to required argument
    #     # with self.assertRaises(Exception) as context:
    #     #     AnalysisSTEAM()
    #     # self.assertTrue('No .yaml input file provided.' in str(context.exception))
    #     # print('This exception was correctly raised: {}'.format(context.exception))

    def test_AnalysisSTEAM_init_LocalSettings(self):
        """
            Check that AnalysisSTEAM object can be initialized and settings can be read when flag_permanent_settings=False
        """
        # arrange
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_LEDET_REFERENCE.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)

        # assert 1 - Class attributes correctly initialized
        self.assertTrue(hasattr(aSTEAM.data_analysis, 'GeneralParameters'))
        self.assertTrue(hasattr(aSTEAM.data_analysis, 'PermanentSettings'))
        self.assertTrue(hasattr(aSTEAM.data_analysis, 'AnalysisStepDefinition'))
        self.assertTrue(hasattr(aSTEAM.data_analysis, 'AnalysisStepSequence'))
        # assert 2 - settings correctly read from local settings file
        self.assertEqual(settings.comsolexe_path, aSTEAM.settings.comsolexe_path)
        self.assertEqual(settings.JAVA_jdk_path, aSTEAM.settings.JAVA_jdk_path)
        self.assertEqual(settings.CFunLibPath, aSTEAM.settings.CFunLibPath)
        self.assertEqual(settings.ProteCCT_path, aSTEAM.settings.ProteCCT_path)
        self.assertEqual(settings.LEDET_path, aSTEAM.settings.LEDET_path)
        self.assertEqual(settings.PSPICE_path, aSTEAM.settings.PSPICE_path)
        self.assertEqual(settings.COSIM_path, aSTEAM.settings.COSIM_path)
        self.assertEqual(settings.FiQuS_path, aSTEAM.settings.FiQuS_path)
        self.assertEqual(settings.PSPICE_library_path, aSTEAM.settings.PSPICE_library_path)

    def test_AnalysisSTEAM_init_PermanentSettings(self):
        """
            Check that AnalysisSTEAM object can be initialized and settings can be read when flag_permanent_settings=True
        """
        # arrange
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_WORKING_FOLDERS.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)

        # assert
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.comsolexe_path, aSTEAM.settings.comsolexe_path)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.JAVA_jdk_path, aSTEAM.settings.JAVA_jdk_path)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.CFunLibPath, aSTEAM.settings.CFunLibPath)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.ProteCCT_path, aSTEAM.settings.ProteCCT_path)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.LEDET_path, aSTEAM.settings.LEDET_path)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.PSPICE_path, aSTEAM.settings.PSPICE_path)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.COSIM_path, aSTEAM.settings.COSIM_path)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.FiQuS_path, aSTEAM.settings.FiQuS_path)
        self.assertEqual(aSTEAM.data_analysis.PermanentSettings.PSPICE_library_path, aSTEAM.settings.PSPICE_library_path)

    def test_AnalysisSTEAM_exceptionSettingsFileNotFound(self):
        """
            Check that AnalysisSTEAM object raises an exception if the settings file is not found when flag_permanent_settings=False
        """
        # arrange
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_exceptionSettingsFileNotFound.yaml')
        # arrange - delete temporary settings file, if present
        user_name = os.getlogin()
        temp_settings_file = Path(os.path.join('', f"settings.{user_name}.yaml")).resolve()
        if os.path.isfile(temp_settings_file):
            os.remove(temp_settings_file)
            print('File {} already existed. It was removed.'.format(temp_settings_file))

        # act
        with self.assertRaises(Exception) as context:
            AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)

        # assert
        print(F'This exception was correctly raised: {context.exception}')
        self.assertTrue('Settings file not found at' in str(context.exception))

    def test_AnalysisSTEAM_exceptionLibraryFolderNotExisting(self):
        """
            Check that AnalysisSTEAM object raises an exception if the working folders are not defined
        """
        # arrange
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_exceptionLibraryFolderNotExisting.yaml')
        dummy_folder_name = 'DUMMY_NOT_EXISTING'

        # act + assert
        with self.assertRaises(Exception) as context:
            AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        print('This exception was correctly raised: {}'.format(context.exception))
        self.assertTrue('Defined library folder ' in str(context.exception))
        self.assertTrue(f'{dummy_folder_name}' in str(context.exception))
        self.assertTrue(' does not exist. Key to change: "local_library_path" in the settings.' in str(context.exception))

    def test_AnalysisSTEAM_write_analysis_file(self):
        """
            Check that AnalysisSTEAM object can be initialized and settings can be read when flag_permanent_settings=True
        """
        # arrange
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_WORKING_FOLDERS.yaml')
        reference_file = os.path.join(os.getcwd(), 'references', 'output_for_write_analysis_file_test', 'reference_written_analysis_file.yaml')
        path_output_file = os.path.join(os.getcwd(), 'output', 'output_for_write_analysis_file_test', 'output_analysis_file.yaml')

        # arrange - make a new object and programmatically add an analysis step
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        current_step = 'programmatically_added_step'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step] = ModifyModelMultipleVariables(type='ModifyModelMultipleVariables')
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].model_name = 'BM'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_to_change = [
            'Options_LEDET.magnet_inductance.flag_calculate_inductance',
            'Conductors[0].strand.RRR',
        ]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_value = [
            [False],
            [150],
        ]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_name = 'MQSX'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].software = 'LEDET'
        aSTEAM.data_analysis.AnalysisStepSequence.append(current_step)

        # update the library path as the output folder is one folder deeper
        aSTEAM.data_analysis.PermanentSettings.local_library_path = '../' + aSTEAM.data_analysis.PermanentSettings.local_library_path

        # act
        aSTEAM.write_analysis_file(path_output_file=path_output_file)

        # assert 1: output file exists
        self.assertTrue(os.path.isfile(path_output_file))
        # assert 2: output file has the same information as the reference file
        aSTEAM_reference = AnalysisSTEAM(file_name_analysis=reference_file, verbose=False)
        aSTEAM_generated = AnalysisSTEAM(file_name_analysis=path_output_file, verbose=False)
        self.assertEqual(aSTEAM_reference.data_analysis, aSTEAM_generated.data_analysis)

    def test_AnalysisSTEAM_FiQuS_CWS(self):
        """
        Test if Analysis involving FiQuS CWS magnet works
        """
        #simulation_number = 1
        g_n = 1     # geometry_number
        m_n = 1     # mesh_number
        s_n = 1     # solution_number
        magnet_name = 'CWS_1'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_FiQuS_CWS.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        absolute_local_FiQuS_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_FiQuS_folder)).resolve())
        if os.path.exists(absolute_local_FiQuS_folder) and os.path.isdir(absolute_local_FiQuS_folder):
            shutil.rmtree(absolute_local_FiQuS_folder)
            print(f"Deleted folder: {absolute_local_FiQuS_folder}")
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        geometry_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                 magnet_name,
                                                                 f'Geometry_{g_n}',
                                                                 f'{magnet_name}.brep')).resolve()

        print(f'Checking if geometry_file exists: {geometry_file}')
        self.assertTrue(os.path.exists(geometry_file))

        mesh_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                 magnet_name,
                                                                 f'Geometry_{g_n}',
                                                                 f'Mesh_{m_n}',
                                                                 f'{magnet_name}.msh')).resolve()

        print(f'Checking if mesh_file exists: {mesh_file}')
        self.assertTrue(os.path.exists(mesh_file))

        selfMutualInductanceMatrix_transient = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                magnet_name,
                                                                f'Geometry_{g_n}',
                                                                f'Mesh_{m_n}',
                                                                f'Solution_{s_n}',
                                                                f'selfMutualInductanceMatrix_transient.csv')).resolve()

        print(f'Checking if selfMutualInductanceMatrix_transient exists: {selfMutualInductanceMatrix_transient}')
        self.assertTrue(os.path.isfile(selfMutualInductanceMatrix_transient))

    def test_AnalysisSTEAM_FiQuS_CACStrand(self):
        """
        Test if Analysis involving FiQuS CAC Strand works
        """
        #simulation_number = 1
        g_n = 1     # geometry_number
        m_n = 1     # mesh_number
        s_n = 1     # solution_number
        magnet_name = 'CAC_Strand_hexFilaments'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_FiQuS_CAC.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        absolute_local_FiQuS_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_FiQuS_folder)).resolve())
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        geometry_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                magnet_name,
                                                                f'Geometry_{g_n}',
                                                                f'{magnet_name}.brep')).resolve()

        print(f'Checking if geometry_file exists: {geometry_file}')
        self.assertTrue(os.path.exists(geometry_file))

        mesh_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                magnet_name,
                                                                f'Geometry_{g_n}',
                                                                f'Mesh_{m_n}',
                                                                f'{magnet_name}.msh')).resolve()

        print(f'Checking if mesh_file exists: {mesh_file}')
        self.assertTrue(os.path.exists(mesh_file))

        outputPower = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                magnet_name,
                                                                f'Geometry_{g_n}',
                                                                f'Mesh_{m_n}',
                                                                f'Solution_{s_n}',
                                                                'test_temporary',
                                                                f'power.txt')).resolve()

        print(f'Checking if power.txt exists: {outputPower}')
        self.assertTrue(os.path.isfile(outputPower))

    def test_AnalysisSTEAM_FiQuS_Multipole_EM(self):
        """
            Check that AnalysisSTEAM analysis can be run with a FiQuS inputs
        """
        # arrange - set inputs
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_FiQuS_Multipole_EM.yaml')
        method_name = self.test_AnalysisSTEAM_FiQuS_Multipole_EM.__name__
        output_path = os.path.join(os.getcwd(), 'output', method_name[method_name.find('FiQuS'):])

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        make_folder_if_not_existing(output_path)
        aSTEAM.data_analysis.AnalysisStepDefinition['step_postprocess'].path_to_saved_files = output_path
        aSTEAM.run_analysis()
        pass
        #self.assertTrue(os.path.exists(os.path.join(post_proc_path, 'MQXA_plot_difference_Bx_By_FiQuS_ROXIE.png')))

    def test_AnalysisSTEAM_FiQuS_Multipole_TH(self):
        """
            Check that AnalysisSTEAM analysis can be run with a FiQuS inputs
        """
        # arrange - set inputs
        # simulation_number = 1
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_FiQuS_Multipole_TH.yaml')
        method_name = self.test_AnalysisSTEAM_FiQuS_Multipole_TH.__name__
        output_path = os.path.join(os.getcwd(), 'output', method_name[method_name.find('FiQuS'):])
        # data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        # absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        # settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        # absolute_local_FiQuS_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_FiQuS_folder)).resolve())

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        # analysis_name = aSTEAM.data_analysis.GeneralParameters.analysis_name
        # post_proc_path = os.path.join(absolute_local_FiQuS_folder, analysis_name, f'{simulation_number}')
        make_folder_if_not_existing(output_path)
        aSTEAM.data_analysis.AnalysisStepDefinition['step_postprocess'].path_to_saved_files = output_path
        aSTEAM.run_analysis()
        pass
        #self.assertTrue(os.path.exists(os.path.join(post_proc_path, 'MQXA_plot_difference_Bx_By_FiQuS_ROXIE.png')))

    def test_AnalysisSTEAM_FiQuS_Pancake3D(self):
        """
        Test if Analysis involving FiQuS Pancake3D works
        """
        #simulation_number = 1
        g_n = 1     # geometry_number
        m_n = 1     # mesh_number
        s_n = 1     # solution_number
        magnet_name = 'HTS1'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_FiQuS_HTS.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        absolute_local_FiQuS_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_FiQuS_folder)).resolve())
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        geometry_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                magnet_name,
                                                                f'Geometry_{g_n}',
                                                                f'{magnet_name}.brep')).resolve()

        print(f'Checking if geometry_file exists: {geometry_file}')
        self.assertTrue(os.path.exists(geometry_file))

        mesh_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                magnet_name,
                                                                f'Geometry_{g_n}',
                                                                f'Mesh_{m_n}',
                                                                f'{magnet_name}.msh')).resolve()

        print(f'Checking if mesh_file exists: {mesh_file}')
        self.assertTrue(os.path.exists(mesh_file))

        outputTemperature = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                magnet_name,
                                                                f'Geometry_{g_n}',
                                                                f'Mesh_{m_n}',
                                                                f'Solution_{s_n}',
                                                                f'Temperature-DefaultFormat.pos')).resolve()

        print(f'Checking if Temperature-DefaultFormat.pos exists: {outputTemperature}')
        self.assertTrue(os.path.isfile(outputTemperature))

    def test_AnalysisSTEAM_FiQuS_parsim_magnet_parallel(self):
        """
        Test if parallel analysis involving FiQuS Pancake3D works
        """
        #simulation_number = 1
        g_n = [1, 2, 3, 4]     # geometry_numbers
        g_should_exist = [1, 1, 0, 1]     # should geometry_number exist
        m_n = 1             # mesh_number
        s_n = 1             # solution_number
        magnet_name = 'HTS1'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_FiQuS_parsim_magnet_parallel.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        absolute_local_FiQuS_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_FiQuS_folder)).resolve())
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        for g, g_should_exist in zip(g_n, g_should_exist):
            geometry_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                    magnet_name,
                                                                    f'Geometry_{g}',
                                                                    f'{magnet_name}.brep')).resolve()

            if g_should_exist:
                print(f'Checking if geometry_file exists: {geometry_file}')
                self.assertTrue(os.path.exists(geometry_file))
            else:
                print(f'Checking if geometry_file does NOT exist: {geometry_file}')
                self.assertFalse(os.path.exists(geometry_file))

            mesh_file = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                    magnet_name,
                                                                    f'Geometry_{g}',
                                                                    f'Mesh_{m_n}',
                                                                    f'{magnet_name}.msh')).resolve()

            if g_should_exist:
                print(f'Checking if mesh_file exists: {mesh_file}')
                self.assertTrue(os.path.exists(mesh_file))
            else:
                print(f'Checking if mesh_file does NOT exist: {mesh_file}')
                self.assertFalse(os.path.exists(mesh_file))

            outputTemperature = Path(os.path.join(absolute_local_FiQuS_folder,
                                                                    magnet_name,
                                                                    f'Geometry_{g}',
                                                                    f'Mesh_{m_n}',
                                                                    f'Solution_{s_n}',
                                                                    f'Temperature-DefaultFormat.pos')).resolve()

            if g_should_exist:
                print(f'Checking if Temperature-DefaultFormat.pos exists: {outputTemperature}')
                self.assertTrue(os.path.isfile(outputTemperature))
            else:
                print(f'Checking if Temperature-DefaultFormat.pos does NOT exist: {outputTemperature}')
                self.assertFalse(os.path.isfile(outputTemperature))

    def test_AnalysisSTEAM_LEDET_magnet_conductor(self):
        """
            Check that AnalysisSTEAM analysis can be run
        """
        # arrange - got local settings (done in the setUp() function)
        # arrange - set inputs
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_LEDET_REFERENCE.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        absolute_local_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_LEDET_folder)).resolve())
        absolute_local_ANSYS_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_ANSYS_folder)).resolve())
        expected_default_file_LEDET = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_1' + '.xlsx')
        expected_mod1_file_LEDET = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_10' + '.xlsx')
        expected_mod1bis_file_LEDET = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_11' + '.xlsx')
        expected_mod2_file_LEDET = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_12' + '.xlsx')
        expected_default_file_LEDET_json = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_1' + '.json')
        expected_mod1_file_LEDET_json = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_10' + '.json')
        expected_mod1bis_file_LEDET_json = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_11' + '.json')
        expected_mod2_file_LEDET_json = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Input', 'MBRB' + '_12' + '.json')
        expected_model_name = 'BM'  # manually written, but it corresponds to the entry in the input analysis file
        expected_model_name_mod1 = 'BM_mod1'
        expected_model_name_mod2 = 'BM_mod2'
        expected_output_file_LEDET_mat1 = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Output', 'Mat Files', 'SimulationResults_LEDET_10.mat')
        expected_output_file_LEDET_mat2 = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Output', 'Mat Files', 'SimulationResults_LEDET_1.mat')
        expected_output_file_LEDET_mat3 = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Output', 'Mat Files', 'SimulationResults_LEDET_12.mat')
        expected_output_file_LEDET_txt1 = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Output', 'Txt Files', 'MBRB_VariableHistory_12.txt')
        expected_output_file_LEDET_txt2 = os.path.join(absolute_local_LEDET_folder, 'MBRB', 'Output', 'Txt Files', 'MBRB_VariableStatus_12.txt')
        expected_output_file_APDL_CT_1 = os.path.join(absolute_local_ANSYS_folder, 'MBRB', '_STRING_123', 'MBRB_STRING_123.inp')  # string "_STRING_123" comes from the STEAM analysis yaml file

        # arrange: delete output files, if already existing
        if os.path.isfile(expected_output_file_LEDET_mat1):
            os.remove(expected_output_file_LEDET_mat1)
            print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_LEDET_mat1))
        if os.path.isfile(expected_output_file_LEDET_mat2):
            os.remove(expected_output_file_LEDET_mat2)
            print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_LEDET_mat2))
        if os.path.isfile(expected_output_file_LEDET_mat3):
            os.remove(expected_output_file_LEDET_mat3)
            print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_LEDET_mat3))
        if os.path.isfile(expected_output_file_LEDET_txt1):
            os.remove(expected_output_file_LEDET_txt1)
            print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_LEDET_txt1))
        if os.path.isfile(expected_output_file_LEDET_txt2):
            os.remove(expected_output_file_LEDET_txt2)
            print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_LEDET_txt2))

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # assert that MakeModel step works correctly
        print('### Checking the output ###')
        # assert 1 - check that BuilderModel object exists and it contains a key with the model name
        self.assertTrue(hasattr(aSTEAM, 'list_models'))
        self.assertTrue(expected_model_name in aSTEAM.list_models)
        print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name))
        # assert 2 - check that LEDET reference file exists
        self.assertTrue(os.path.isfile(expected_default_file_LEDET))
        print('File {} exists.'.format(expected_default_file_LEDET))
        # assert 3 - check entries in LEDET reference file
        pl = ParserLEDET(BuilderLEDET(flag_build=False))
        pl.readFromExcel(expected_default_file_LEDET, verbose=False)
        self.assertEqual(4.5, pl.builder_ledet.Inputs.T00)

        # assert that ModifyModel step works correctly
        # assert 4 - check that new BuilderModel objects exist and they contain a key with the model name
        self.assertTrue(expected_model_name_mod1 in aSTEAM.list_models)
        print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name_mod1))
        self.assertTrue(expected_model_name_mod2 in aSTEAM.list_models)
        print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name_mod2))
        # assert 5 - check that values of the modified keys are correct
        self.assertEqual(1.9, aSTEAM.list_models['BM_mod1'].model_data.GeneralParameters.T_initial)
        self.assertEqual(3, aSTEAM.list_models['BM_mod2'].model_data.GeneralParameters.T_initial)
        self.assertEqual(110, aSTEAM.list_models['BM'].model_data.Conductors[0].strand.RRR)
        self.assertEqual(110, aSTEAM.list_models['BM_mod1'].model_data.Conductors[0].strand.RRR)
        self.assertEqual(110, aSTEAM.list_models['BM_mod2'].model_data.Conductors[0].strand.RRR)
        self.assertEqual(0, aSTEAM.list_models['BM_mod1'].model_data.Options_LEDET.post_processing.flag_saveTxtFiles)
        self.assertEqual(1, aSTEAM.list_models['BM_mod2'].model_data.Options_LEDET.post_processing.flag_saveTxtFiles)
        # assert 6 - check entries in LEDET modified files
        pl = ParserLEDET(BuilderLEDET(flag_build=False))
        pl.readFromExcel(expected_mod1_file_LEDET, verbose=False)
        self.assertEqual(1.9, pl.builder_ledet.Inputs.T00)
        self.assertEqual(0.001, pl.builder_ledet.Inputs.R_crowbar)
        self.assertEqual(1.25, pl.builder_ledet.Inputs.f_ro_eff_inGroup[0])
        pl = ParserLEDET(BuilderLEDET(flag_build=False))
        pl.readFromExcel(expected_mod2_file_LEDET, verbose=False)
        self.assertEqual(3, pl.builder_ledet.Inputs.T00)
        self.assertEqual(0.001, pl.builder_ledet.Inputs.R_crowbar)
        self.assertEqual(1.25, pl.builder_ledet.Inputs.f_ro_eff_inGroup[0])
        pl = ParserLEDET(BuilderLEDET(flag_build=False))
        pl.readFromExcel(expected_mod1bis_file_LEDET, verbose=False)
        self.assertEqual(4.5, pl.builder_ledet.Inputs.T00)
        self.assertEqual(0.001, pl.builder_ledet.Inputs.R_crowbar)
        self.assertEqual(1.25, pl.builder_ledet.Inputs.f_ro_eff_inGroup[0])
        # assert 6bis - check that json files were generated
        self.assertTrue(os.path.isfile(expected_default_file_LEDET_json))
        self.assertTrue(os.path.isfile(expected_mod1_file_LEDET_json))
        self.assertTrue(os.path.isfile(expected_mod1bis_file_LEDET_json))
        self.assertTrue(os.path.isfile(expected_mod2_file_LEDET_json))

        # ## assert that RunSimulation step works correctly
        # # assert 7 - check that LEDET .mat output files exist
        # self.assertTrue(os.path.isfile(expected_output_file_LEDET_mat1))  # won't work in Gitlab CI/CD pipeline
        # print('File {} exists.'.format(expected_output_file_LEDET_mat1))
        # self.assertTrue(os.path.isfile(expected_output_file_LEDET_mat2))  # won't work in Gitlab CI/CD pipeline
        # print('File {} exists.'.format(expected_output_file_LEDET_mat2))
        self.assertTrue(os.path.isfile(expected_output_file_LEDET_mat3))
        print(f'File {expected_output_file_LEDET_mat3} exists.')
        # # assert 8 - check that LEDET .txt output files exist
        self.assertTrue(os.path.isfile(expected_output_file_LEDET_txt1))
        print(f'File {expected_output_file_LEDET_txt1} exists.')
        self.assertTrue(os.path.isfile(expected_output_file_LEDET_txt2))
        print(f'File {expected_output_file_LEDET_txt2} exists.')

        # Assert that step for writing the APDL_CT model works correctly
        # assert 9 - check that the APDL_CT output file exists
        self.assertTrue(os.path.isfile(expected_output_file_APDL_CT_1))

    def test_AnalysisSTEAM_PSPICE_RB(self):
        """
            Check that AnalysisSTEAM analysis can be run
        """
        # arrange - got local settings (done in the setUp() function)
        # arrange - set inputs
        sim_number = 1
        circuit_name = 'RB'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PSPICE_RB.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        absolute_local_PSPICE_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_PSPICE_folder)).resolve())
        expected_output_file_PSPICE_out1 = os.path.join(absolute_local_PSPICE_folder, circuit_name, str(sim_number), f'{circuit_name}.out')

        # arrange: delete output files, if already existing
        if os.path.isfile(expected_output_file_PSPICE_out1):
            os.remove(expected_output_file_PSPICE_out1)
            print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_PSPICE_out1))

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # assert that MakeModel step works correctly
        print('### Checking the output ###')
        # assert 1 - check that BuilderModel object exists and it contains a key with the model name
        expected_model_name = 'BM'  # manually written, but it corresponds to the entry in the input analysis file
        self.assertTrue(hasattr(aSTEAM, 'list_models'))
        self.assertTrue(expected_model_name in aSTEAM.list_models)
        print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name))

        # assert 2 - check that the PSPICE netlist has a correctly-changed GlobalParameters.global_parameters entry
        pPSPICE_1 = ParserPSPICE(None)
        pPSPICE_1.read_netlist(expected_output_file_PSPICE_out1, flag_acquire_auxiliary_files=True, verbose=True)
        self.assertEqual(pPSPICE_1.circuit_data.GlobalParameters.global_parameters['R1_Warm'], '0.123')

        # assert 3 - check that the PSPICE netlist has a correctly-changed Netlist entry
        self.assertEqual(pPSPICE_1.circuit_data.Netlist['r1_warm'].value, 'R1_Warm*1.123')

        # assert 4 - check that the PSPICE netlist has a correctly-changed Netlist entry
        self.assertEqual(pPSPICE_1.circuit_data.Netlist['r1_warm'].nodes, ['4', '3'])

        # ## assert that RunSimulation step works correctly
        # # assert 7 - check that PSPICE .out output files exist
        self.assertTrue(os.path.isfile(expected_output_file_PSPICE_out1))
        print('File {} exists.'.format(expected_output_file_PSPICE_out1))

    def test_AnalysisSTEAM_PySIGMA(self):
        """
        Test if Analysis involving PySIGMA works
        """
        simulation_number = 1
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PySIGMA.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_SIGMA_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_SIGMA_folder)).resolve())
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()
        magnet_name = 'MQXA'
        output_file = Path(os.path.join(expected_local_SIGMA_folder,
                                        f'{magnet_name}', f'{simulation_number}', f'{magnet_name}_ROXIE_COORD.csv')).resolve()
        print(f'Checking if file exists: {output_file}')
        self.assertTrue(os.path.exists(output_file))

    def test_AnalysisSTEAM_XYCE_RU(self):
        """
            Check that AnalysisSTEAM analysis can be run
        """
        simulation_number = 1
        analysis_name = 'RU'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_XYCE_RU.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_XYCE_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_XYCE_folder)).resolve())
        expected_output_file_XYCE_out1 = os.path.join(expected_local_XYCE_folder, f'{analysis_name}', f'{simulation_number}', f'{analysis_name}.csd')
        # arrange: delete output files, if already existing
        if os.path.isfile(expected_output_file_XYCE_out1):
            os.remove(expected_output_file_XYCE_out1)
            print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_XYCE_out1))

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # assert
        self.assertTrue(os.path.isfile(expected_output_file_XYCE_out1))

    def test_AnalysisSTEAM_CopyFileRelative(self):
        """
        Test if Analysis involving FiQuS CWS magnet works
        """
        ''
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_CopyFileRelative.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        list_core_paths_and_software = []
        for attr_name, attr_value in settings.model_dump().items():
            if 'local_' and '_folder' in str(attr_name):
                index_from = attr_name.find('local_') + len('local_')
                index_to = attr_name.find('_folder')
                software_name = attr_name[index_from:index_to].strip()
                path_folder_core = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), attr_value, 'test_CopyFileRelative')).resolve())
                list_core_paths_and_software.append((path_folder_core, software_name))
                path_folder = os.path.join(path_folder_core, 'Source')
                make_folder_if_not_existing(path_folder)
                file_name = os.path.join(path_folder, f'{software_name}.txt')
                print(f'Writing test file {file_name}')
                with open(file_name, 'w') as file:
                    file.write(f'Dummy string in a dummy file used by test_AnalysisSTEAM_CopyFileRelative and for software folder used by {software_name}')

        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        for path_folder_core, software_name in list_core_paths_and_software:
            file_name = os.path.join(path_folder_core, 'Destination', f'{software_name}_copied.txt')
            print(f'Checking if file {file_name} exists.')
            self.assertTrue(os.path.exists(file_name))

    #
    # def test_AnalysisSTEAM_runAnalysis_circuit(self):
    #     """
    #         Check that AnalysisSTEAM analysis can be run
    #     """
    #     # arrange - get local settings
    #     user_name = os.getlogin()
    #     name_file_settings = 'settings.' + user_name + '.yaml'
    #     full_path_file_settings = Path(self.local_path_settings / name_file_settings).resolve()
    #     print('user_name:               {}'.format(user_name))
    #     print('name_file_settings:      {}'.format(name_file_settings))
    #     print('full_path_file_settings: {}'.format(full_path_file_settings))
    #
    #     # Read ProteCCT exe path from the settings file
    #     with open(full_path_file_settings, 'r') as stream:
    #         local_settings_dict = yaml.safe_load(stream)
    #
    #     # arrange - set inputs
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_RB.yaml')
    #     expected_reference_file_LEDET = os.path.join('output', 'analysis_RB', '1', 'RB' + '.cir')
    #     expected_model_name = 'BM'  # manually written, but it corresponds to the entry in the input analysis file
    #     expected_output_file_PSPICE_out1 = os.path.join(local_settings_dict['local_PSPICE_folder'], 'RB', '1', 'RB.out')
    #
    #     # arrange: delete output files, if already existing
    #     if os.path.isfile(expected_output_file_PSPICE_out1):
    #         os.remove(expected_output_file_PSPICE_out1)
    #         print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_PSPICE_out1))
    #
    #     # act
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
    #     aSTEAM.run_analysis()
    #
    #     ## assert that MakeModel step works correctly
    #     print('### Checking the output ###')
    #     # assert 1 - check that BuilderModel object exists and it contains a key with the model name
    #     self.assertTrue(hasattr(aSTEAM, 'list_models'))
    #     self.assertTrue(expected_model_name in aSTEAM.list_models)
    #     print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name))
    #     # # assert 2 - check that LEDET reference file exists
    #     # self.assertTrue(os.path.isfile(expected_reference_file_LEDET))
    #     # print('File {} exists.'.format(expected_reference_file_LEDET))
    #     # # assert 3 - check entries in LEDET reference file
    #     # pl = ParserLEDET(BuilderLEDET(flag_build=False))
    #     # pl.readFromExcel(expected_reference_file_LEDET, verbose=False)
    #     # self.assertEqual(4.5, pl.builder_ledet.Inputs.T00)
    #     #
    #     # ## assert that ModifyModel step works correctly
    #     # # assert 4 - check that new BuilderModel objects exist and they contain a key with the model name
    #     # self.assertTrue(expected_model_name_mod1 in aSTEAM.list_models)
    #     # print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name_mod1))
    #     # self.assertTrue(expected_model_name_mod2 in aSTEAM.list_models)
    #     # print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name_mod2))
    #     # # assert 5 - check that values of the modified keys are correct
    #     # self.assertEqual(1.9, aSTEAM.list_models['BM_mod1'].model_data.GeneralParameters.T_initial)
    #     # self.assertEqual(3  , aSTEAM.list_models['BM_mod2'].model_data.GeneralParameters.T_initial)
    #     # self.assertEqual(110, aSTEAM.list_models['BM'].model_data.Conductors[0].strand.RRR)
    #     # self.assertEqual(110, aSTEAM.list_models['BM_mod2'].model_data.Conductors[0].strand.RRR)
    #     # self.assertEqual(110, aSTEAM.list_models['BM_mod2'].model_data.Conductors[0].strand.RRR)
    #     # self.assertEqual(1, aSTEAM.list_models['BM_mod1'].model_data.Options_LEDET.post_processing.flag_saveTxtFiles)
    #     # self.assertEqual(0, aSTEAM.list_models['BM_mod2'].model_data.Options_LEDET.post_processing.flag_saveTxtFiles)
    #     # # assert 6 - check entries in LEDET modified files
    #     # pl = ParserLEDET(BuilderLEDET(flag_build=False))
    #     # pl.readFromExcel(expected_mod1_file_LEDET, verbose=False)
    #     # self.assertEqual(1.9, pl.builder_ledet.Inputs.T00)
    #     # self.assertEqual(0.001, pl.builder_ledet.Inputs.R_crowbar)
    #     # self.assertEqual(1.25, pl.builder_ledet.Inputs.f_ro_eff_inGroup[0])
    #     # pl = ParserLEDET(BuilderLEDET(flag_build=False))
    #     # pl.readFromExcel(expected_mod2_file_LEDET, verbose=False)
    #     # self.assertEqual(3, pl.builder_ledet.Inputs.T00)
    #     # self.assertEqual(0.001, pl.builder_ledet.Inputs.R_crowbar)
    #     # self.assertEqual(1.25, pl.builder_ledet.Inputs.f_ro_eff_inGroup[0])
    #     # pl = ParserLEDET(BuilderLEDET(flag_build=False))
    #     # pl.readFromExcel(expected_mod1bis_file_LEDET, verbose=False)
    #     # self.assertEqual(4.5, pl.builder_ledet.Inputs.T00)
    #     # self.assertEqual(0.001, pl.builder_ledet.Inputs.R_crowbar)
    #     # self.assertEqual(1.25, pl.builder_ledet.Inputs.f_ro_eff_inGroup[0])
    #
    #     # ## assert that RunSimulation step works correctly
    #     # # assert 7 - check that LEDET .mat output files exist
    #     self.assertTrue(os.path.isfile(expected_output_file_PSPICE_out1))
    #     print('File {} exists.'.format(expected_output_file_PSPICE_out1))
    #
    #
    # def test_AnalysisSTEAM_runAnalysis_circuit_XYCE(self):
    #     """
    #         Check that AnalysisSTEAM analysis can be run
    #     """
    #     # arrange - get local settings
    #     user_name = os.getlogin()
    #     name_file_settings = 'settings.' + user_name + '.yaml'
    #     full_path_file_settings = Path(self.local_path_settings / name_file_settings).resolve()
    #     print('user_name:               {}'.format(user_name))
    #     print('name_file_settings:      {}'.format(name_file_settings))
    #     print('full_path_file_settings: {}'.format(full_path_file_settings))
    #
    #     with open(full_path_file_settings, 'r') as stream:
    #         local_settings_dict = yaml.safe_load(stream)
    #
    #     # arrange - set inputs
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_RB_XYCE.yaml')
    #     expected_model_name = 'BM'  # manually written, but it corresponds to the entry in the input analysis file
    #     expected_output_file_XYCE_out1 = os.path.join(local_settings_dict['local_XYCE_folder'], 'RB', '1', 'RB.csd')
    #
    #     # arrange: delete output files, if already existing
    #     if os.path.isfile(expected_output_file_XYCE_out1):
    #         os.remove(expected_output_file_XYCE_out1)
    #         print('File {} already existed. It was removed. This test will re-make it.'.format(expected_output_file_XYCE_out1))
    #
    #     # act
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
    #     aSTEAM.run_analysis()
    #
    #     ## assert that MakeModel step works correctly
    #     print('### Checking the output ###')
    #     # assert 1 - check that BuilderModel object exists and it contains a key with the model name
    #     self.assertTrue(hasattr(aSTEAM, 'list_models'))
    #     self.assertTrue(expected_model_name in aSTEAM.list_models)
    #     print('Key {} exists in aSTEAM.list_models.'.format(expected_model_name))
    #     # ## assert that RunSimulation step works correctly
    #     # # assert 2 - check that XYCE .mat output files exist
    #     self.assertTrue(os.path.isfile(expected_output_file_XYCE_out1))
    #     print('File {} exists.'.format(expected_output_file_XYCE_out1))
    #

    def test_AnalysisSTEAM_PyBBQ_conductor(self):
        """
            Check that AnalysisSTEAM analysis can be run with a PyBBQ inputs
        """
        # arrange - set inputs
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PyBBQ_REFERENCE.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()

        # assert TODO

    # def test_AnalysisSTEAM_addAuxiliaryFiles(self):
    #     """
    #         Check that the method add_auxiliary_file() correctly completes its tasks
    #     """
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_ADD_AUXILIARY_FILE.yaml')
    #     list_expected_files = [
    #         'aux_file_relative_path.txt',
    #         'add_file_relative_path_name_changed.txt'
    #         ]
    #
    #     # arrange: delete output folder, if existing
    #     output_folder_name = os.path.join('output', 'output_for_auxiliary_files_test')  # manually written, but it corresponds to the entry in the input analysis file
    #     if os.path.exists(output_folder_name) and os.path.isdir(output_folder_name):
    #         shutil.rmtree(output_folder_name)
    #         print('Folder {} already existed. It was removed. This test will re-make it.'.format(output_folder_name))
    #
    #     # act
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
    #     aSTEAM.run_analysis()
    #
    #     # assert - check output files were generated
    #     for fil in list_expected_files:
    #         full_path_fil = os.path.join(output_folder_name, fil)
    #         self.assertTrue(os.path.isfile(full_path_fil))
    #         print(f'File {full_path_fil} was correctly generated.')

    def test_AnalysisSTEAM_runCustomPyFunction(self):
        """
            Check that the method run_custom_py_function() correctly completes its tasks
            The analysis is composed of two steps, each checking one functionality (run from default folder and run from selected folder):
            - one step to run a custom function that is in the default steam_sdk.analyses.custom_analyses
            - one step to run a custom function that is in a selected folder
        """
        # arrange
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_run_custom_py_function.yaml')
        list_expected_files = [
            'output_run_custom_py_function_1.csv',
            'output_run_custom_py_function_2.csv',
            ]
        list_reference_files = [
            'reference_run_custom_py_function_1.csv',
            'reference_run_custom_py_function_2.csv',
            ]

        # arrange: delete output folder, if existing
        output_folder_name = os.path.join('output', 'output_for_run_custom_py_function')  # manually written, but it corresponds to the entry in the input analysis file
        if os.path.exists(output_folder_name) and os.path.isdir(output_folder_name):
            shutil.rmtree(output_folder_name)
            print('Folder {} already existed. It was removed. This test will re-make it.'.format(output_folder_name))

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()

        # # assert - check output files were generated
        for fil in range(len(list_expected_files)):
            full_path_fil = os.path.join(output_folder_name, list_expected_files[fil])
            full_path_ref = os.path.join('references', list_reference_files[fil])
            self.assertTrue(os.path.isfile(full_path_fil))
            print(f'File {full_path_fil} was correctly generated.')
            assert_equal_readable_files(full_path_fil, full_path_ref)

    def test_AnalysisSTEAM_runViewer(self):
        # arrange - input file
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_run_viewer.yaml')
        # file_name_transients = os.path.join('input', 'run_viewer', 'file_name_transients_TEST.csv')
        # arrange - expected output csv
        path_expected_meas_csv_folder = os.path.join('output', 'STEAM_CONVERTED_MEAS_REPO', 'EXAMPLE_TEST_CAMPAIGN_NAME',)
        full_path_expected_converted_csv_file = os.path.join(path_expected_meas_csv_folder, 'EXAMPLE_TEST_NAME_2_MF.csv')
        # arrange - expected output png
        output_figure_folder = os.path.join('output', 'STEAM_ANALYSIS_OUTPUT')
        list_expected_figures = [
            os.path.join('case meas', 'case meas_measured_current'),
            os.path.join('case meas', 'case meas_measured_voltage'),
            os.path.join('case sim', 'case sim_simulated_current'),
            os.path.join('case sim', 'case sim_simulated_U1_U2'),
            os.path.join('case sim', 'case sim_simulated_voltage'),
            os.path.join('case meas+sim', 'case meas+sim_I_meas_cpr_sim'),
            os.path.join('case meas+sim', 'case meas+sim_Umeas_Imeas'),
        ]
        # arrange - expected html and pdf output
        path_output_html_report = os.path.join('output', 'STEAM_ANALYSIS_OUTPUT', 'output_html_report.html')
        path_output_pdf_report = os.path.join('output', 'STEAM_ANALYSIS_OUTPUT', 'output_pdf_report.pdf')

        # Delete folder and files that are already present
        if os.path.isdir(path_expected_meas_csv_folder):
            shutil.rmtree(path_expected_meas_csv_folder)
            print(f'Folder {path_expected_meas_csv_folder} was already present and was deleted. It will be re-written by this test.')
        if os.path.isdir(output_figure_folder):
            shutil.rmtree(output_figure_folder)
            print(f'Folder {output_figure_folder} was already present and was deleted. It will be re-written by this test.')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()

        # Assign the Viewer object from the AnalysisSTEAM object to the workspace
        V = aSTEAM.list_viewers['V']

        # assert 1: check the object structure and key values
        # These keys must be present
        self.assertTrue(hasattr(V, 'dict_events'))
        self.assertTrue(hasattr(V, 'list_events'))
        self.assertTrue(hasattr(V, 'verbose'))
        self.assertTrue(hasattr(V, 'dict_configs'))
        # These dictionary keys must be present
        self.assertTrue('MBRD_1' in V.dict_configs)
        self.assertTrue(hasattr(V.dict_configs['MBRD_1'], 'SignalList'))
        self.assertTrue(hasattr(V.dict_configs['MBRD_1'].SignalList['measured_current'], 'meas_label'))
        # Check the type of these keys
        self.assertTrue(type(V.dict_configs) is dict)
        self.assertTrue(type(V.dict_configs['MBRD_1']) is Configuration)
        self.assertTrue(type(V.dict_configs['MBRD_1'].SignalList) is dict)

        # assert 2: check that the converted csv file exists
        self.assertTrue(os.path.isfile(full_path_expected_converted_csv_file))

        # assert 3: check that the generated .png figures exist
        for fig in list_expected_figures:
            self.assertTrue(os.path.isfile(os.path.join(output_figure_folder, f'{fig}.png')))
            self.assertTrue(os.path.isfile(os.path.join(output_figure_folder, f'{fig}.svg')))
            self.assertTrue(os.path.isfile(os.path.join(output_figure_folder, f'{fig}.pdf')))

        # assert 4: check values
        self.assertListEqual(V.dict_figures['case meas'], ['case meas_measured_current', 'case meas_measured_voltage'])
        self.assertListEqual(V.dict_figures['case sim'], ['case sim_simulated_current', 'case sim_simulated_voltage', 'case sim_simulated_U1_U2'])
        self.assertListEqual(V.dict_figures['case meas+sim'], ['case meas+sim_I_meas_cpr_sim', 'case meas+sim_Umeas_Imeas'])

        # assert 5: check that the generated .html report exists
        self.assertTrue(os.path.isfile(path_output_html_report))

        # assert 6: check that the generated .pdf report exists
        self.assertTrue(os.path.isfile(path_output_pdf_report))

    def test_AnalysisSTEAM_calculate_metrics(self):
        # arrange - input file
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_CALCULATE_METRICS.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()

        # Assign the Viewer object from the AnalysisSTEAM object to the workspace
        V = aSTEAM.list_viewers['V']

        # assert 1: check the object structure and key values
        # These keys must be present
        self.assertTrue(hasattr(V, 'dict_events'))
        self.assertTrue(hasattr(V, 'list_events'))
        self.assertTrue(hasattr(V, 'verbose'))
        self.assertTrue(hasattr(V, 'dict_configs'))
        self.assertTrue(hasattr(aSTEAM, 'list_metrics'))
        # These dictionary keys must be present
        self.assertTrue('MBRD_1' in V.dict_configs)
        self.assertTrue(hasattr(V.dict_configs['MBRD_1'], 'SignalList'))
        self.assertTrue(hasattr(V.dict_configs['MBRD_1'].SignalList['measured_current'], 'meas_label'))
        self.assertTrue('metrics_analysis_1' in aSTEAM.list_metrics)
        # Check the type of these keys
        self.assertTrue(type(V.dict_configs) is dict)
        self.assertTrue(type(V.dict_configs['MBRD_1']) is Configuration)
        self.assertTrue(type(V.dict_configs['MBRD_1'].SignalList) is dict)
        # Check the value of these keys
        self.assertTrue(len(aSTEAM.list_metrics['metrics_analysis_1']['case meas']) == 0)  # empty dictionary
        self.assertTrue(len(aSTEAM.list_metrics['metrics_analysis_1']['case sim']) == 0)  # empty dictionary
        self.assertListEqual(aSTEAM.list_metrics['metrics_analysis_1']['case meas+sim']['I_sim'], [5490.133642141358, 5880.754315913736])
        self.assertListEqual(aSTEAM.list_metrics['metrics_analysis_1']['case meas+sim']['U_sim_vs_I_sim'], [0.5, 0.4920554088026804])

    def test_AnalysisSTEAM_load_circuit_parameters(self):
        # arrange
        file_name_analysis = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PSPICE_load_circuit_parameters_IPQ.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()

        # assert
        self.assertEqual(aSTEAM.list_models["IPQ_RQ10_2_2xRPHGA_2xMQML"].circuit_data.GlobalParameters.global_parameters["R_Warm_1"], '0.0002071')

    def test_AnalysisSTEAM_writeStimuliFromInterpolation_general(self):
        # arrange
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_writeStimuliFromInterpolation.yaml')
        outputfile = os.path.join(os.getcwd(), 'output', 'TEST_Interpolation_Resistance_MQY.stl')
        if os.path.exists(outputfile): os.remove(outputfile)

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()

        # assert
        ref_path = os.path.join(os.getcwd(), 'references', 'Reference_Interpolation_Resistance_MQY.stl')
        tst_path = outputfile
        self.assertListEqual(list(io.open(tst_path)), list(io.open(ref_path)))

    def test_AnalysisSTEAM_writeStimuliFromInterpolation_general_two_csv(self):
        # arrange
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_writeStimuliFromInterpolationGeneral.yaml')
        outputfile = os.path.join(os.getcwd(), 'output', 'TEST_Interpolation_Resistance_MQY_RQD_51magnets.stl')
        if os.path.exists(outputfile): os.remove(outputfile)

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()

        # assert
        ref_path = os.path.join(os.getcwd(), 'references', 'Reference_MQY_RQD_51magnets.stl')
        tst_path = outputfile
        self.assertListEqual(list(io.open(tst_path)), list(io.open(ref_path)))

    def test_AnalysisSTEAM_LEDET_parsim_event_magnet(self, max_relative_error=1E-5, verbose=True):
        # arrange - got local settings (done in the setUp() function)
        magnet_name = 'MBRB'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_LEDET_parsim_event_magnet.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_LEDET_folder)).resolve())
        outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event', 'TestFile_AnalysisSTEAM_run_parsim_event_output.yaml')
        sim_numbers = [1, 2, 3]
        list_output_file = [os.path.join(expected_local_LEDET_folder, magnet_name, 'Input', f'{magnet_name}_{i}.xlsx') for i in sim_numbers]
        if os.path.exists(outputfile): os.remove(outputfile)
        for file in list_output_file:
            if os.path.exists(file): os.remove(file)
        list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event', f'{magnet_name}_reference_{i}.xlsx') for i in sim_numbers]

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()
        aSTEAM.write_analysis_file(path_output_file=outputfile)

        # assert
        for i, _ in enumerate(sim_numbers):
            self.assertTrue(CompareLEDETParameters(list_reference_file[i], list_output_file[i], max_relative_error=max_relative_error, verbose=verbose))
        # self.assertTrue(CompareLEDETParameters(list_reference_file[0], list_output_file[0], max_relative_error=max_relative_error, verbose=verbose))
        # self.assertTrue(CompareLEDETParameters(list_reference_file[1], list_output_file[1], max_relative_error=max_relative_error, verbose=verbose))
        # self.assertTrue(CompareLEDETParameters(list_reference_file[2], list_output_file[2], max_relative_error=max_relative_error, verbose=verbose))


    def test_AnalysisSTEAM_LEDET_parsim_conductor_opt_fCu(self, max_relative_error=1E-5, verbose=True):
        # arrange
        sim_number = 21
        magnet_name = 'MBRB'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_LEDET_parsim_conductor.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_LEDET_folder)).resolve())
        outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_conductor', 'TestFile_AnalysisSTEAM_LEDET_parsim_conductor.yaml')
        output_xlsx = os.path.join(expected_local_LEDET_folder, magnet_name, 'Input', f'{magnet_name}_{sim_number}.xlsx')
        output_yaml = os.path.join(expected_local_LEDET_folder, magnet_name, 'Input', f'{magnet_name}_{sim_number}.yaml')
        delete_if_existing(outputfile, verbose=verbose)
        delete_if_existing(output_xlsx, verbose=verbose)
        reference_xlsx = os.path.join(os.getcwd(), 'references', 'run_parsim_conductor', f'{magnet_name}_reference_{sim_number}.xlsx')
        reference_yaml = os.path.join(os.getcwd(), 'references', 'run_parsim_conductor', f'{magnet_name}_reference_{sim_number}.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()
        aSTEAM.write_analysis_file(path_output_file=outputfile)

        # assert
        self.assertTrue(os.path.isfile(output_yaml))
        assert_equal_yaml(output_yaml, reference_yaml, max_relative_error=max_relative_error) # useful for debugging
        self.assertTrue(CompareLEDETParameters(reference_xlsx, output_xlsx, max_relative_error=max_relative_error, verbose=verbose))


    def test_AnalysisSTEAM_LEDET_parsim_conductor_opt_length(self, max_relative_error=1E-5, verbose=True):
        # arrange
        sim_number = 22
        magnet_name = 'MBRB'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_LEDET_parsim_conductor_variation1.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_LEDET_folder)).resolve())
        outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_conductor', 'TestFile_AnalysisSTEAM_LEDET_parsim_conductor_variation1.yaml')
        output_xlsx = os.path.join(expected_local_LEDET_folder, magnet_name, 'Input', f'{magnet_name}_{sim_number}.xlsx')
        output_yaml = os.path.join(expected_local_LEDET_folder, magnet_name, 'Input', f'{magnet_name}_{sim_number}.yaml')
        if os.path.exists(outputfile): os.remove(outputfile)
        if os.path.exists(output_xlsx): os.remove(output_xlsx)
        reference_xlsx = os.path.join(os.getcwd(), 'references', 'run_parsim_conductor', f'{magnet_name}_reference_{sim_number}.xlsx')
        reference_yaml = os.path.join(os.getcwd(), 'references', 'run_parsim_conductor', f'{magnet_name}_reference_{sim_number}.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()
        aSTEAM.write_analysis_file(path_output_file=outputfile)

        # assert
        self.assertTrue(os.path.isfile(output_yaml))
        assert_equal_yaml(output_yaml, reference_yaml, max_relative_error=max_relative_error) # useful for debugging
        self.assertTrue(CompareLEDETParameters(reference_xlsx, output_xlsx, max_relative_error=max_relative_error, verbose=verbose))


    def test_AnalysisSTEAM_LEDET_parsim_event_with_Viewer_csv(self, verbose: bool = False):
        # arrange
        file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_LEDET_parsim_event_magnet_with_Viewer_csv.yaml')
        outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_with_Viewer_csv', 'TestFile_AnalysisSTEAM_run_parsim_event_with_Viewer_csv_output.yaml')
        outputfile_csv = os.path.join(os.getcwd(), 'output', 'run_parsim_event_with_Viewer_csv', 'setUpViewer_output_1.csv')
        delete_if_existing(outputfile, verbose=verbose)
        delete_if_existing(outputfile_csv, verbose=verbose)
        ref_viewer_csv = os.path.join('references', 'run_parsim_event', 'setUpViewer_reference_1.csv')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=True)
        aSTEAM.run_analysis()
        aSTEAM.write_analysis_file(path_output_file=outputfile)

        # assert
        assert_equal_readable_files(ref_viewer_csv, outputfile_csv)


    def test_AnalysisSTEAM_LEDET_parsim_sweep_magnet(self, max_relative_error=1E-5, verbose=True):
        # arrange
        magnet_name = 'MBRB'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_LEDET_parsim_sweep_magnet.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_LEDET_folder)).resolve())
        list_output_file = [os.path.join(expected_local_LEDET_folder, magnet_name, 'Input', f'{magnet_name}_{i}.xlsx')
                            for i in range(9997, 9999)]
        for file in list_output_file:
            delete_if_existing(file, verbose=verbose)
        list_reference_file = [
            os.path.join(os.getcwd(), 'references', 'run_parsim_sweep', 'LEDET', f'{magnet_name}_reference_{i}.xlsx')
            for i in range(9997, 9999)]

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # # assert - check output files were generated and match reference ones
        for file_ref, file_out in zip(list_reference_file, list_output_file):
            self.assertTrue(os.path.isfile(file_out))
            print(f'File {file_out} was correctly generated.')
            self.assertTrue(CompareLEDETParameters(file_ref, file_out, max_relative_error=max_relative_error, verbose=verbose))


    def test_AnalysisSTEAM_LEDET_parsim_sweep_conductor(self):
        # arrange
        conductor_name = 'generic_busbar'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_LEDET_parsim_sweep_conductor.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_LEDET_folder)).resolve())
        list_output_file = [
            os.path.join(expected_local_LEDET_folder, conductor_name, 'Input', f'{conductor_name}_{i}.yaml') for i in
            range(9997, 9999)]
        for file in list_output_file:
            if os.path.exists(file): os.remove(file)
        list_reference_file = [
            os.path.join(os.getcwd(), 'references', 'run_parsim_sweep', 'LEDET', f'{conductor_name}_reference_{i}.yaml')
            for i in range(9997, 9999)]

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # # assert - check output files were generated and match reference ones
        for file_ref, file_out in zip(list_reference_file, list_output_file):
            self.assertTrue(os.path.isfile(file_out))
            print(f'File {file_out} was correctly generated.')
            assert_equal_yaml(file_ref, file_out)


    def test_AnalysisSTEAM_PSPICE_parsim_sweep_circuit(self):
        # arrange
        circuit_name = 'RQX'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_sweep_circuit.yaml')
        data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
        absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
        settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
        expected_local_PSPICE_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_PSPICE_folder)).resolve())
        list_output_file = [os.path.join(expected_local_PSPICE_folder, circuit_name, f'{i}', f'{circuit_name}.cir') for
                            i in
                            range(9997, 10000)]  # note that the path C:\tempPSPICE comes from the permanent settings in the input analysis yaml file
        for file in list_output_file:
            if os.path.exists(file): os.remove(file)
        list_reference_file = [
            os.path.join(os.getcwd(), 'references', 'run_parsim_sweep', 'PSPICE', f'{circuit_name}_reference_{i}.cir')
            for i in range(9997, 10000)]

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # assert - check output files were generated and match reference ones
        for file_ref, file_out in zip(list_reference_file, list_output_file):
            self.assertTrue(os.path.isfile(file_out))
            print(f'File {file_out} was correctly generated.')

            # Read the netlists and compare them
            pPSPICE_ref = ParserPSPICE(None).read_netlist(file_ref, verbose=False)
            pPSPICE_out = ParserPSPICE(None).read_netlist(file_out, verbose=False)
            # assert - check that the both output files contain the same information as the original file
            self.assertDictEqual(dict(pPSPICE_ref.Analysis), dict(pPSPICE_out.Analysis))  # a key here should be changed in two of the three files
            self.assertDictEqual(dict(pPSPICE_ref.Netlist), dict(pPSPICE_out.Netlist))  # no keys here should be changed
            self.assertDictEqual(dict(pPSPICE_ref.GlobalParameters), dict(pPSPICE_out.GlobalParameters))  # a dictionary key here should be changed in two of the three files

    def test_AnalysisSTEAM_PyCoSim_makeModel_RunModel_ParSweep(self):
        # arrange
        cosim_name = 'CCT_FiQuS_LEDET'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PyCoSim_makeModel_RunModel_ParSweep.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # assert - TODO

    def test_AnalysisSTEAM_PyCoSim_PostProcess_Plot(self):
        # arrange
        cosim_name = 'CCT_FiQuS_LEDET'
        absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PyCoSim_PostProcess_Plot.yaml')

        # act
        aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
        aSTEAM.run_analysis()

        # assert - TODO

    # def test_AnalysisSTEAM_PyCoSim_makeModel_RunModel_DUMMY_PSPICE_LEDET(self):
    #     # arrange
    #     cosim_name = 'DUMMY_PSPICE_LEDET'
    #     absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PyCoSim_makeModel_RunModel_DUMMY_PSPICE_LEDET.yaml')
    #     data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
    #     absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
    #     settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
    #     expected_PSPICE_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_PyCoSim_folder, cosim_name, 'PSPICE')).resolve())
    #     expected_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_PyCoSim_folder, cosim_name, 'LEDET')).resolve())
    #     ref_folder = os.path.join('references', 'test_AnalysisSTEAM_PyCoSim_makeModel_RunModel_DUMMY_PSPICE_LEDET')
    #
    #     dict_files_to_check = {
    #         os.path.join(ref_folder, r'1_0_1_0\ExternalStimulus_1_0_1_0.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\ExternalStimulus_1_0_1_0.stl'),
    #         os.path.join(ref_folder, r'1_0_1_0\bias_points_saved_1_0_1_0.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\bias_points_saved_1_0_1_0.stl'),
    #         os.path.join(ref_folder, r'1_0_1_0\coil_resistances_1_0_1_0.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\coil_resistances_1_0_1_0.stl'),
    #         os.path.join(ref_folder, r'1_0_1_0\internal_stimulus_1_0_1_0.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\internal_stimulus_1_0_1_0.stl'),
    #         os.path.join(ref_folder, r'1_0_1_1\MO_1AP_VariableStatus_1_1_1_0.txt'): os.path.join(expected_LEDET_folder,r'Txt Files\MO_1AP_VariableStatus_1_1_1_0.txt'),
    #         os.path.join(ref_folder, r'1_0_1_1\MO_1AP_VariableHistory_1_1_1_0.txt'): os.path.join(expected_LEDET_folder,r'Txt Files\MO_1AP_VariableHistory_1_1_1_0.txt'),
    #         os.path.join(ref_folder, r'1_0_1_1\ExternalStimulus_1_0_1_1.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\ExternalStimulus_1_0_1_1.stl'),
    #         os.path.join(ref_folder, r'1_0_1_1\bias_points_saved_1_0_1_1.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\bias_points_saved_1_0_1_1.stl'),
    #         os.path.join(ref_folder, r'1_0_1_1\coil_resistances_1_0_1_1.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\coil_resistances_1_0_1_1.stl'),
    #         os.path.join(ref_folder, r'1_0_1_1\internal_stimulus_1_0_1_1.stl'): os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\internal_stimulus_1_0_1_1.stl'),
    #     }
    #
    #     # act
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=True)
    #     aSTEAM.run_analysis()
    #
    #     # # assert - check output files were generated and match reference ones
    #     # for file_ref, file_out in dict_files_to_check.items():
    #     #     self.assertTrue(os.path.isfile(file_out))
    #     #     print(f'File {file_out} was correctly generated.')
    #     #     assert_equal_readable_files(file_ref, file_out, n_lines_to_skip_file1=0, n_lines_to_skip_file2=0)


    # def test_AnalysisSTEAM_run_parsim_event_circuit(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCB', f'{i+1}', 'RCB.cir') for i in range(4)]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCB_REFERENCE_{i + 1}.cir') for i in range(4)]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RCB(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RCB.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCB', '1', 'RCB.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCB_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_60A_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_60A.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_60A')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_60A/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_60A_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCB', f'{file_counter}', 'RCB.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_60A', f'RCB_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             #assert # check that the generated .cir file is identical to a reference
    #             for file_ref, file_out in zip(list_reference_file, list_output_file):
    #                 pPSPICE_ref = ParserPSPICE(None)
    #                 pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #                 pPSPICE_out = ParserPSPICE(None)
    #                 pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #                 # assert - check that the read information from the original and re-written files is the same
    #                 self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_IPD(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_IPD.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'IPD', '0', 'IPD.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'IPD_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)

        # assert #TODO check that the generated .cir file is identical to a reference
        # for file_ref, file_out in zip(list_reference_file, list_output_file):
        #     pPSPICE_ref = ParserPSPICE(None)
        #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
        #     pPSPICE_out = ParserPSPICE(None)
        #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
        #     # assert - check that the read information from the original and re-written files is the same
        #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_IPD_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_IPD.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_IPD')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_IPD/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_IPD_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'IPD', f'{file_counter}', 'IPD.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_IPD', f'IPD_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             # assert # check that the generated .cir file is identical to a reference
    #             for file_ref, file_out in zip(list_reference_file, list_output_file):
    #                 pPSPICE_ref = ParserPSPICE(None)
    #                 pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #                 pPSPICE_out = ParserPSPICE(None)
    #                 pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #                 # assert - check that the read information from the original and re-written files is the same
    #                 self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RQ(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RQ.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RQ_47magnets', '1', 'RQ_47magnets.cir'), os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RQ_47magnets', '2', 'RQ_47magnets.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RQ_REFERENCE_from_eos_1.cir'), os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RQ_REFERENCE_from_eos_2.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)

    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_RQ(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_all_RQ.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_RQ')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 52
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_RQ/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].default_keys.file_counter = file_counter
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter, file_counter + 200]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_all_RQ_{file_counter}.yaml')
    #             magnet_number = self.find_magnets(os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/RQ_circuit_parameters.csv"), file_name.split("_")[0].replace(".", "D_"))
    #             circuit_substrings = {
    #                 "RQ.": f"RQ_{magnet_number}magnets"
    #             }
    #             circuit_type = next((ctype for substring, ctype in circuit_substrings.items() if file_name.startswith(substring)), None)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['setup_folder_PSPICE'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['makeModel_ref'].file_model_data = circuit_type
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter}', f'{circuit_type}.cir'), os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter + 200}', f'{circuit_type}.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RQ_REFERENCE_{file_counter}_1.cir'), os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RQ_REFERENCE_{file_counter}_2.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             # assert check that the generated .cir file is identical to a reference
    #             # for file_ref, file_out in zip(list_reference_file, list_output_file):
    #             #     pPSPICE_ref = ParserPSPICE(None)
    #             #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #             #     pPSPICE_out = ParserPSPICE(None)
    #             #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #             #     # assert - check that the read information from the original and re-written files is the same
    #             #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1

    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RQX(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RQX.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RQX', '0', 'RQX.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RQX_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)

        # assert #TODO check that the generated .cir file is identical to a reference
        # for file_ref, file_out in zip(list_reference_file, list_output_file):
        #     pPSPICE_ref = ParserPSPICE(None)
        #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
        #     pPSPICE_out = ParserPSPICE(None)
        #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
        #     # assert - check that the read information from the original and re-written files is the same
        #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_RQX_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_RQX.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_RQX')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_RQX/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_RQX_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RQX', f'{file_counter}', 'RQX.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_RQX', f'RQX_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             # assert # check that the generated .cir file is identical to a reference
    #             for file_ref, file_out in zip(list_reference_file, list_output_file):
    #                 pPSPICE_ref = ParserPSPICE(None)
    #                 pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #                 pPSPICE_out = ParserPSPICE(None)
    #                 pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #                 # assert - check that the read information from the original and re-written files is the same
    #                 self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_IPQ(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_IPQ.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'IPQ_RQ4_2_2xRPHH_2xMQY', '1', 'IPQ_RQ4_2_2xRPHH_2xMQY.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'IPQ_RQ4_2_2xRPHH_2xMQY_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_IPQ_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_IPQ.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_IPQ')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_IPQ/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             # aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name =
    #             # aSTEAM.data_analysis.AnalysisStepDefinition['setup_folder_PSPICE'].simulation_name  =
    #             # aSTEAM.data_analysis.AnalysisStepDefinition['makeModel_ref'].file_model_data =
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_IPQ_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RQX', f'{file_counter}', 'RQX.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_IPQ', f'IPQ_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             # assert # check that the generated .cir file is identical to a reference
    #             # for file_ref, file_out in zip(list_reference_file, list_output_file):
    #             #     pPSPICE_ref = ParserPSPICE(None)
    #             #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #             #     pPSPICE_out = ParserPSPICE(None)
    #             #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #             #     # assert - check that the read information from the original and re-written files is the same
    #             #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RCBY(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RCBY.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCBY', '1', 'RCBY.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCBY_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_80_120A_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_80_120A.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_80_120A')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_80_120A/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_80_120A_{file_counter}.yaml')
    #             if file_name.startswith("RCBC"):
    #                 circuit_type = "RCBC"
    #             elif file_name.startswith("RCBY"):
    #                 circuit_type = "RCBY"
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['setup_folder_PSPICE'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['makeModel_ref'].file_model_data = circuit_type
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter}', f'{circuit_type}.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_80_120A', f'80_120A_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             #assert # check that the generated .cir file is identical to a reference
    #             for file_ref, file_out in zip(list_reference_file, list_output_file):
    #                 pPSPICE_ref = ParserPSPICE(None)
    #                 pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #                 pPSPICE_out = ParserPSPICE(None)
    #                 pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #                 # assert - check that the read information from the original and re-written files is the same
    #                 self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RQT12(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RQT12.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RQT12', '1', 'RQT12.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RQT12_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RCS(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RCS.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCS', '1', 'RCS.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCS_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RB(self, verbose=True):
    #     # arrange
    #     sim_number = 2
    #     circuit_name = 'RB'
    #     absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RB.yaml')
    #     data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
    #     absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
    #     settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
    #     expected_local_PSPICE_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_PSPICE_folder)).resolve())
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(expected_local_PSPICE_folder, circuit_name, str(sim_number), f'{circuit_name}.cir')]
    #     list_output_file.append(os.path.join(expected_local_PSPICE_folder, circuit_name, str(sim_number), 'coil_resistances.stl'))
    #     delete_if_existing(outputfile, verbose=verbose)
    #     for file in list_output_file:
    #         delete_if_existing(file, verbose=verbose)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'{circuit_name}_REFERENCE_from_eos_2.cir')]
    #
    #     # act
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=absolute_path_analysis_file, verbose=verbose)
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)

    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_RB_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_RB.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_RB')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 840
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_RB/{file_name}'
    #             row_counter = self.count_rows_in_csv(file_path) - 1
    #             list=[]
    #             for i in range(1, row_counter+1):
    #                 list.append(i)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].default_keys.file_counter = file_counter
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_RB_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RB', f'{file_counter}', 'RB.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_RB', f'RB_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             # assert # check that the generated .cir file is identical to a reference
    #             # for file_ref, file_out in zip(list_reference_file, list_output_file):
    #             #     pPSPICE_ref = ParserPSPICE(None)
    #             #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #             #     pPSPICE_out = ParserPSPICE(None)
    #             #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #             #     # assert - check that the read information from the original and re-written files is the same
    #             #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    # #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_RCBX_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_RCBX.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_RCBX')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_RCBX/{file_name}'
    #             #aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             if file_name.startswith("RCBX"):
    #                 circuit_name = "RCBX"
    #                 aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].default_keys.file_counter = file_counter
    #                 aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter, file_counter + 200]
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name = circuit_name
    #             aSTEAM.data_analysis.AnalysisStepDefinition['setup_folder_PSPICE'].simulation_name = circuit_name
    #             aSTEAM.data_analysis.AnalysisStepDefinition['makeModel_ref'].file_model_data = circuit_name
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_{circuit_name}_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_name}', f'{file_counter}', f'{circuit_name}.cir'), os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_name}', f'{file_counter + 200}', f'{circuit_name}.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_RCBX', f'{circuit_name}_REFERENCE_{file_counter}.cir'), os.path.join(os.getcwd(), 'references', 'run_parsim_event_RCBX', f'{circuit_name}_REFERENCE_{file_counter + 200}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             # assert # check that the generated .cir file is identical to a reference
    #             for file_ref, file_out in zip(list_reference_file, list_output_file):
    #                 pPSPICE_ref = ParserPSPICE(None)
    #                 pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #                 pPSPICE_out = ParserPSPICE(None)
    #                 pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #                 # assert - check that the read information from the original and re-written files is the same
    #                 self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1

    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RCBX(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RCBX.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCBX', '1', 'RCBX.cir'), os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCBX', '2', 'RCBX.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCBX_REFERENCE_from_eos_1.cir'), os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCBX_REFERENCE_from_eos_2.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_RQX_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_RQX.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_RQX')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_RQX/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_RQX_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RQX', f'{file_counter}', 'RQX.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_RQX', f'RQX_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             # assert # check that the generated .cir file is identical to a reference
    #             for file_ref, file_out in zip(list_reference_file, list_output_file):
    #                 pPSPICE_ref = ParserPSPICE(None)
    #                 pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #                 pPSPICE_out = ParserPSPICE(None)
    #                 pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #                 # assert - check that the read information from the original and re-written files is the same
    #                 self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_from_eos_RCD_RCO(self, verbose=True):
    #     # arrange
    #     file_name_analysis_1 = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RCO.yaml')
    #     file_name_analysis_2 = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_RCD.yaml')
    #     aSTEAM_1 = AnalysisSTEAM(file_name_analysis=file_name_analysis_1, verbose=verbose)
    #     aSTEAM_2 = AnalysisSTEAM(file_name_analysis=file_name_analysis_2, verbose=verbose)
    #     outputfile_1 = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output_1.yaml')
    #     outputfile_2 = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_from_eos_output_2.yaml')
    #     list_output_file = [os.path.join(aSTEAM_1.settings.local_PSPICE_folder, 'RCO', '1', 'RCO.cir'), os.path.join(aSTEAM_2.settings.local_PSPICE_folder, 'RCD', '1', 'RCD.cir')]
    #     if os.path.exists(outputfile_1): os.remove(outputfile_1)
    #     if os.path.exists(outputfile_2): os.remove(outputfile_2)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCO_REFERENCE_from_eos_1.cir'), os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCD_REFERENCE_from_eos_1.cir')]
    #
    #     # act
    #     aSTEAM_1.run_analysis()
    #     aSTEAM_1.write_analysis_file(path_output_file=outputfile_1)
    #
    #     aSTEAM_2.run_analysis()
    #     aSTEAM_2.write_analysis_file(path_output_file=outputfile_2)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_RCD_RCO_files(self, verbose=True):
    #     # arrange
    #     file_name_analysis_1 = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_all_RCO.yaml')
    #     file_name_analysis_2 = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_all_RCD.yaml')
    #     aSTEAM_1 = AnalysisSTEAM(file_name_analysis=file_name_analysis_1, verbose=verbose)
    #     aSTEAM_2 = AnalysisSTEAM(file_name_analysis=file_name_analysis_2, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_RCD_RCO')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 82
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             aSTEAM_1.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_RCD_RCO/{file_name}'
    #             aSTEAM_2.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_RCD_RCO/{file_name}'
    #             aSTEAM_1.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             aSTEAM_2.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             aSTEAM_1.data_analysis.AnalysisStepDefinition['runParsimEvent'].default_keys.file_counter = file_counter
    #             aSTEAM_2.data_analysis.AnalysisStepDefinition['runParsimEvent'].default_keys.file_counter = file_counter
    #             outputfile_1 = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_RCO_{file_counter}.yaml')
    #             outputfile_2 = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_RCD_{file_counter}.yaml')
    #             list_output_file = [os.path.join(aSTEAM_1.settings.local_PSPICE_folder, 'RCO', f'{file_counter}', 'RCO.cir'), os.path.join(aSTEAM_2.settings.local_PSPICE_folder, 'RCD', f'{file_counter}', 'RCD.cir')]
    #             if os.path.exists(outputfile_1): os.remove(outputfile_1)
    #             if os.path.exists(outputfile_2): os.remove(outputfile_2)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCO_REFERENCE_{file_counter}.cir'), os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCD_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM_1.run_analysis()
    #             aSTEAM_1.write_analysis_file(path_output_file=outputfile_1)
    #
    #             aSTEAM_2.run_analysis()
    #             aSTEAM_2.write_analysis_file(path_output_file=outputfile_2)
    #
    #             # assert #TODO check that the generated .cir file is identical to a reference
    #             # for file_ref, file_out in zip(list_reference_file, list_output_file):
    #             #     pPSPICE_ref = ParserPSPICE(None)
    #             #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #             #     pPSPICE_out = ParserPSPICE(None)
    #             #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #             #     # assert - check that the read information from the original and re-written files is the same
    #             #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_I_off_less_than_delta_I_parabolic(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_I_off_less_than_I_parabolic.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_I_off_less_than_I_parabolic.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCB', '1', 'RCB.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCB_REFERENCE_I_off_less_than_I_parabolic.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_I_off_less_than_delta_I_parabolic_neg_ramp_rate(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_I_off_less_than_I_parabolic_neg_ramp_rate.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_I_off_less_than_I_parabolic_neg_ramp_rate.yaml')
    #     list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, 'RCB', '1', 'RCB.cir')]
    #     if os.path.exists(outputfile): os.remove(outputfile)
    #     for file in list_output_file:
    #         if os.path.exists(file): os.remove(file)
    #     list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_circuit', f'RCB_REFERENCE_I_off_less_than_I_parabolic_neg_ramp_rate.cir')]
    #
    #     # act
    #     aSTEAM.run_analysis()
    #     aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #     # assert #TODO check that the generated .cir file is identical to a reference
    #     for file_ref, file_out in zip(list_reference_file, list_output_file):
    #         pPSPICE_ref = ParserPSPICE(None)
    #         pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #         pPSPICE_out = ParserPSPICE(None)
    #         pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #         # assert - check that the read information from the original and re-written files is the same
    #         self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #
    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_600A_files(self, verbose = True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_600A.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_600A')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             file_path = os.path.join(folder_path, file_name)
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_600A/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_600A_{file_counter}.yaml')
    #             circuit_substrings = {
    #                 "RCS": "RCS",
    #                 "RQ6": "RQ6",
    #                 "RQS.A": "RQS_AxxBx",
    #                 "RQS.L": "RQS_R_LxBx",
    #                 "RQS.R": "RQS_R_LxBx",
    #                 "RQSX3": "RQSX3",
    #                 "RQT1": "RQT_12_13",
    #                 "RQTD": "RQT",
    #                 "RQTF": "RQT",
    #                 "RQTL7": "RQTL_7_8_10_11",
    #                 "RQTL8": "RQTL_7_8_10_11",
    #                 "RQTL1": "RQTL_7_8_10_11",
    #                 "RQTL9": "RQTL9",
    #                 "RSS": "RSS"
    #             }
    #
    #             circuit_type = next(
    #                 (ctype for substring, ctype in circuit_substrings.items() if file_name.startswith(substring)),
    #                 None)
    #
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['setup_folder_PSPICE'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['makeModel_ref'].file_model_data = circuit_type
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter}', f'{circuit_type}.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_600A', f'600A_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)

    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_600A_files_2(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_600A_2.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_600A_2')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 1
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_600A_2/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_600A_{file_counter}.yaml')
    #             magnet_number = self.find_magnets(os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/600A_circuit_parameters.csv"), file_name.split("_")[0])
    #             circuit_substrings = {
    #                 "RSD": f"RSD_{magnet_number}magnets",
    #                 "RSF": f"RSF_{magnet_number}magnets",
    #                 "RO": f"RO_{magnet_number}magnets"
    #             }
    #
    #             circuit_type = next((ctype for substring, ctype in circuit_substrings.items() if file_name.startswith(substring)), None)
    #
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['setup_folder_PSPICE'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['makeModel_ref'].file_model_data = circuit_type
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter}', f'{circuit_type}.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_600A', f'600A_REFERENCE_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             #assert # check that the generated .cir file is identical to a reference
    #             # for file_ref, file_out in zip(list_reference_file, list_output_file):
    #             #     pPSPICE_ref = ParserPSPICE(None)
    #             #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #             #     pPSPICE_out = ParserPSPICE(None)
    #             #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #             #     # assert - check that the read information from the original and re-written files is the same
    #             #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1

    # def test_AnalysisSTEAM_run_parsim_event_circuit_all_IPQ_files(self, verbose=True):
    #     # arrange
    #     file_name_analysis = os.path.join('input', 'TestFile_AnalysisSTEAM_PSPICE_parsim_event_all_IPQ.yaml')
    #     aSTEAM = AnalysisSTEAM(file_name_analysis=file_name_analysis, verbose=verbose)
    #     folder_path = os.path.join(os.getcwd(), 'input', 'test_run_parsim_event_IPQ')
    #     file_list = os.listdir(folder_path)
    #     file_counter = 400
    #     for file_name in file_list:
    #         if file_name.endswith('.csv'):
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = f'input/test_run_parsim_event_IPQ/{file_name}'
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers = [file_counter]
    #             outputfile = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit', f'TestFile_AnalysisSTEAM_PSPICE_parsim_event_circuit_IPQ_{file_counter}.yaml')
    #             circuit_type = self.find_circuit_model(os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/IPQ_circuit_parameters.csv"), file_name.split("_")[0])
    #             aSTEAM.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['setup_folder_PSPICE'].simulation_name = circuit_type
    #             aSTEAM.data_analysis.AnalysisStepDefinition['makeModel_ref'].file_model_data = circuit_type
    #             list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter}', f'{circuit_type}.cir')]
    #             if os.path.exists(outputfile): os.remove(outputfile)
    #             for file in list_output_file:
    #                 if os.path.exists(file): os.remove(file)
    #             list_reference_file = [os.path.join(os.getcwd(), 'references', 'run_parsim_event_IPQ', f'IPQ_REFERENCE_all_{file_counter}.cir')]
    #
    #             # act
    #             aSTEAM.run_analysis()
    #             aSTEAM.write_analysis_file(path_output_file=outputfile)
    #
    #             #assert # check that the generated .cir file is identical to a reference
    #             # for file_ref, file_out in zip(list_reference_file, list_output_file):
    #             #     pPSPICE_ref = ParserPSPICE(None)
    #             #     pPSPICE_ref.read_netlist(file_ref, verbose=verbose)
    #             #     pPSPICE_out = ParserPSPICE(None)
    #             #     pPSPICE_out.read_netlist(file_out, verbose=verbose)
    #             #     # assert - check that the read information from the original and re-written files is the same
    #             #     self.assertEqual(pPSPICE_ref.circuit_data, pPSPICE_out.circuit_data)
    #             file_counter = file_counter + 1
    #
    # def count_rows_in_csv(self, file_path: str):
    #     row_count = 0
    #
    #     # Open the CSV file
    #     with open(file_path, 'r') as file:
    #         reader = csv.reader(file)
    #
    #         # Iterate over each row in the file
    #         for row in reader:
    #             row_count += 1
    #
    #     return row_count
    #
    #
    # def find_magnets(self, filename, key):
    #     with open(filename, 'r') as file:
    #         reader = csv.DictReader(file)
    #         for row in reader:
    #             if row['circuit'] == key:
    #                 return row['NumberOfMagnets']
    #         return None
    #
    # def find_circuit_model(self, filename, key):
    #     with open(filename, 'r') as file:
    #         reader = csv.DictReader(file)
    #         for row in reader:
    #             if row['circuit'] == key:
    #                 return row['circuit_type']
    #         return None

