from pathlib import Path

from steam_sdk.data.DataAnalysis import DataAnalysis
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.utils.read_settings_file import read_settings_file
from tests.TestHelpers import assert_equal_readable_files
import os

current_path = os.getcwd()
test_folder = os.path.dirname(__file__)
os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
print('\nCurrent folder:        {}'.format(current_path))
print('Test is run from folder: {}'.format(os.getcwd()))


# arrange
cosim_name = 'DUMMY_PSPICE_LEDET'
magnet_name = 'MO_1AP'
absolute_path_analysis_file = os.path.join(os.getcwd(), 'input', 'TestFile_AnalysisSTEAM_PyCoSim_makeModel_RunModel_DUMMY_PSPICE_LEDET.yaml')
data_analysis: DataAnalysis = yaml_to_data(absolute_path_analysis_file, DataAnalysis)
absolute_path_settings_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), data_analysis.GeneralParameters.relative_path_settings)).resolve())
settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder)
expected_PSPICE_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_PyCoSim_folder, cosim_name, 'PSPICE')).resolve())
expected_LEDET_folder = str(Path(os.path.join(os.path.dirname(absolute_path_analysis_file), settings.local_PyCoSim_folder, cosim_name, 'LEDET', '1', magnet_name)).resolve())
ref_folder = os.path.join('references', 'test_AnalysisSTEAM_PyCoSim_makeModel_RunModel_DUMMY_PSPICE_LEDET')

dict_files_to_check = {
    os.path.join(ref_folder, r'1_0_1_0\ExternalStimulus_1_0_1_0.stl'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\ExternalStimulus_1_0_1_0.stl'), 'n_rows_skip': 0},
    os.path.join(ref_folder, r'1_0_1_0\bias_points_saved_1_0_1_0.bsp'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\bias_points_saved_1_0_1_0.bsp'), 'n_rows_skip': 13},
    os.path.join(ref_folder, r'1_0_1_0\coil_resistances_1_0_1_0.stl'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\coil_resistances_1_0_1_0.stl'), 'n_rows_skip': 0},
    os.path.join(ref_folder, r'1_0_1_0\internal_stimulus_1_0_1_0.stl'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_0\internal_stimulus_1_0_1_0.stl'), 'n_rows_skip': 0},
    os.path.join(ref_folder, r'1_0_1_1\MO_1AP_VariableStatus_1_1_1_0.txt'): {'file': os.path.join(expected_LEDET_folder,r'Output\Txt Files\MO_1AP_VariableStatus_1_1_1_0.txt'), 'n_rows_skip': 0},
    os.path.join(ref_folder, r'1_0_1_1\MO_1AP_VariableHistory_1_1_1_0.txt'): {'file': os.path.join(expected_LEDET_folder,r'Output\Txt Files\MO_1AP_VariableHistory_1_1_1_0.txt'), 'n_rows_skip': 0},
    os.path.join(ref_folder, r'1_0_1_1\ExternalStimulus_1_0_1_1.stl'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\ExternalStimulus_1_0_1_1.stl'), 'n_rows_skip': 0},
    os.path.join(ref_folder, r'1_0_1_1\bias_points_saved_1_0_1_1.bsp'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\bias_points_saved_1_0_1_1.bsp'), 'n_rows_skip': 13},
    os.path.join(ref_folder, r'1_0_1_1\coil_resistances_1_0_1_1.stl'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\coil_resistances_1_0_1_1.stl'), 'n_rows_skip': 0},
    os.path.join(ref_folder, r'1_0_1_1\internal_stimulus_1_0_1_1.stl'): {'file': os.path.join(expected_PSPICE_folder,r'1\1_0_1_1\internal_stimulus_1_0_1_1.stl'), 'n_rows_skip': 0},
}

# assert - check output files were generated and match reference ones
for file_ref, dict_out in dict_files_to_check.items():
    file_out = dict_out['file']
    if os.path.isfile(file_out):
        print(f'File {file_out} was correctly generated.')
        try:
            assert_equal_readable_files(file_ref, file_out, n_lines_to_skip_file1=dict_out['n_rows_skip'], n_lines_to_skip_file2=dict_out['n_rows_skip'])
        except:
            print(f'ERROR File {file_out} was not correct.')
    else:
        print(f'ERROR File {file_out} was not generated.')
        if not os.path.isdir(os.path.dirname(file_out)):
            print(f'ERROR Folder {os.path.dirname(file_out)} of {file_out} was not generated.')
