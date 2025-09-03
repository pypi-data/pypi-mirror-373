import os
from pathlib import Path
import shutil

import numpy as np

from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.parsers.ParserLEDET import CompareLEDETParameters
from steam_sdk.parsers.ParserMap2d import parseRoxieMap2d


def _compare_to_reference_LEDET(magnet_name, verbose=False, flag_plot_all=False, magnet_type='multipole'):
    """
        Helper method called by other methods
        Check that BuilderModel object can be initialized, read a model input yaml file, and generate a LEDET model
        This test checks:
         - the content of the generated Excel file against a reference LEDET Excel file
         - the content of the generated csv file against a reference self-mutual inductance csv file
         - the content of the generated map2d file against a reference magnetic-field map map2d file

        magnet_name: can be any magnet name in the library
    """

    # arrange
    max_relative_error = 1e-6  # Maximum accepted relative error for excel, csv and map2d file comparison

    root_folder = root_folder = Path(__file__).parent.parent.parent
    tests_folder = os.path.join(root_folder, 'tests', 'builders')

    file_model_data = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'input', 'modelData_' + magnet_name + '.yaml')
    output_path = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'output')
    input_file_REFERENCE = os.path.join(tests_folder, 'references', 'magnets', magnet_name, magnet_name + '_REFERENCE.xlsx')
    input_file_GENERATED = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'output', magnet_name + '.xlsx')

    if magnet_type not in ['CCT_straight', 'CWS']:  # check also .map2d and selfMutualInductanceMatrix.csv files for non CCT magnets

        csv_file_REFERENCE = os.path.join(tests_folder, 'references', 'magnets', magnet_name, magnet_name + "_selfMutualInductanceMatrix_REFERENCE.csv")
        csv_file_GENERATED = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'output', magnet_name + "_selfMutualInductanceMatrix.csv")

        if magnet_name in ['MED_C_COMB']:
            suffix = '_All_WithIron_NoSelfField'
        else:
            suffix = '_All_WithIron_WithSelfField'
        if magnet_type == 'solenoid':
            suffix = '_All_NoIron_NoSelfField'

        map2d_file_REFERENCE = os.path.join(tests_folder, 'references', 'magnets', magnet_name, magnet_name + suffix + "_REFERENCE.map2d")
        map2d_file_GENERATED = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'output', magnet_name + suffix + ".map2d")

    # act
    BM = BuilderModel(file_model_data=file_model_data, software=['LEDET'], flag_build=True,
                      output_path=output_path, verbose=verbose, flag_plot_all=flag_plot_all,
                      relative_path_settings=Path('../../tests/'))

    # assert 1 - Check that the generated LEDET file has the same input as the reference
    flag_test_passed = CompareLEDETParameters(input_file_GENERATED, input_file_REFERENCE, max_relative_error=max_relative_error, verbose=verbose)

    if magnet_type not in ['CCT_straight', 'CWS']:  # check also .map2d and selfMutualInductanceMatrix.csv files for non CCT magnets

        # assert 2 - Check that the generated csv file differs from the reference by less than max_relative_error
        _compare_two_csv_files(magnet_name, csv_file_REFERENCE, csv_file_GENERATED, max_relative_error=max_relative_error)

        # assert 3a - Check that the generated map2d file differs from the reference by less than max_relative_error
        values_REFERENCE = parseRoxieMap2d(map2d_file_REFERENCE, headerLines=1)
        values_GENERATED = parseRoxieMap2d(map2d_file_GENERATED, headerLines=1)
        np.testing.assert_allclose(values_GENERATED, values_REFERENCE, rtol=max_relative_error, atol=0)
        print("Files {} and {} differ by less than {}%.".format(map2d_file_REFERENCE, map2d_file_GENERATED, max_relative_error * 100))

        # assert 3b - Check that the existing ...E.map2d files are correctly copied
        input_path = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'input')
        number_input_files = len([entry for entry in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, entry))])

        for file in range(number_input_files + 1):
            path_map2d_E = os.path.join(input_path, magnet_name + '_E{}'.format(file) + '.map2d')
            if os.path.isfile(path_map2d_E):
                if magnet_name in ['MED_C_COMB']:
                    suffix = '_E{}'.format(file) + '_WithIron_NoSelfField'
                else:
                    suffix = '_E{}'.format(file) + '_WithIron_WithSelfField'

                if magnet_type == 'solenoid':
                    suffix = '_E{}'.format(file) + 'NoIron_NoSelfField'

                map2d_E_file_REFERENCE = os.path.join(tests_folder, 'references', 'magnets', magnet_name, magnet_name + suffix + "_REFERENCE.map2d")
                map2d_E_file_GENERATED = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'output', magnet_name + suffix + ".map2d")
                values_REFERENCE_E = parseRoxieMap2d(map2d_E_file_REFERENCE, headerLines=1)
                values_GENERATED_E = parseRoxieMap2d(map2d_E_file_GENERATED, headerLines=1)
                np.testing.assert_allclose(values_GENERATED_E, values_REFERENCE_E, rtol=max_relative_error, atol=0)
                print("Files {} and {} differ by less than {}%.".format(map2d_E_file_REFERENCE, map2d_E_file_GENERATED, max_relative_error * 100))

    return flag_test_passed

def _compare_two_csv_files(magnet_name, path_generated=None, path_reference=None,
                               max_relative_error: float = 0):
        """
            Helper method called by other methods to compare csv files
            max_relative_error: Maximum accepted relative error [-]
        """

        # arrange
        if not path_generated:
            path_generated = os.path.join('output', magnet_name, magnet_name + "_selfMutualInductanceMatrix.csv")
        if not path_reference:
            path_reference = os.path.join('references', 'magnets', magnet_name, magnet_name + "_selfMutualInductanceMatrix_REFERENCE.csv")

        data_generated = np.genfromtxt(path_generated, dtype=float, delimiter=',', skip_header=1)
        data_reference = np.genfromtxt(path_reference, dtype=float, delimiter=',', skip_header=1)

        # Check that the number of elements in the generated matrix is the same as in the reference file
        if data_generated.size != data_reference.size:
            raise Exception('Generated csv file does not have the correct size.')

        relative_differences = np.abs(
            data_generated - data_reference) / data_reference  # Matrix with absolute values of relative differences between the two matrices
        max_relative_difference = np.max(np.max(relative_differences))  # Maximum relative difference in the matrix
        assert(abs(max_relative_difference)<max_relative_error)  # Check that the maximum relative difference is below
        print("Files {} and {} differ by less than {}%.".format(path_generated, path_reference, max_relative_difference * 100))


if __name__ == "__main__":
    FLAG_RUN_TEST, FLAG_OVERWRITE_REFERENCE = True, False

    # List all model magnets in the test model library
    root_folder = root_folder = Path(__file__).parent.parent.parent
    tests_folder = os.path.join(root_folder, 'tests', 'builders')
    subfolders = [f.path for f in os.scandir(os.path.join(tests_folder, 'model_library', 'magnets')) if f.is_dir()]
    all_magnet_names = [os.path.basename(subfolder) for subfolder in subfolders]
    print("All magnet models available in the test model library:")
    print(all_magnet_names)

    magnet_names = ['MCBV_1AP']

    magnet_names_to_check = ['MBH_1in1', # Parameter iContactAlongHeight_From has a length of 104 in file A and 108 in file B.      Parameter iContactAlongHeight_To has a length of 104 in file A and 108 in file B.
                             'MBH_4in1', # nT[elPairs_GroupTogether[p][0] - 1] != nT[elPairs_GroupTogether[p][1] - 1]: IndexError: list index out of range
                             'MCBX_HV', # el_order_half_turns, M_m
                             'MCBXH', # el_order_half_turns
                             'MCBXV', # el_order_half_turns
                             'MCBYV_1AP', # el_order_half_turns
                             'MCBH_1AP', # nT[elPairs_GroupTogether[p][0] - 1] != nT[elPairs_GroupTogether[p][1] - 1]: IndexError: list index out of range
                             'MCBV_1AP', # el_order_half_turns
                             'MCBCH_1AP', # el_order_half_turns
                             'MU', # rearrange_half_turns_ribbon     raise ValueError("Mixed Ribbon and Rutherford cables are not supported!") ValueError: Mixed Ribbon and Rutherford cables are not supported!
                             'HTS1', # addThermalConnections    iContactAlongHeight_From_to_add.append(p[0]) IndexError: tuple index out of range
                             ]
    print(f'magnet_names_to_check: {sorted(magnet_names_to_check)}')

    magnet_names_to_overwrite = []

    magnet_names_that_were_edited = ['MBRB', 'MQXF_V2', 'FERMI_20T', 'SMC', 'MS_1AP'] + ['MBRD', 'MBXF', 'MB_2COILS', 'MED_C_COMB', 'MO_1AP', 'MO', 'MS_1AP', 'ERMC_V1',
                    'MQTLH_1AP', 'MQTLI_1AP', 'MQS_1AP', 'MBRC', 'HEPDipo_4COILS', 'MCD', 'RMM_V1', 'MCBYH_1AP', 'MCS', 'MBX', 'MBRB', 'MQXF_V2', 'FERMI_20T', 'SMC', 'MS_1AP'] + ['MQSX', 'MO_1AP', 'MBRS', 'CFD_600A', 'MQMC_2in1', 'MQM_2in1', 'MQML_2in1', 'MQ_1AP', 'MQXB', 'MQY_2in1', 'MCO',
                    'MCDO', 'MSS_1AP', 'dummy_MBH_2in1_with_multiple_QH', 'CCT_COSIM_1', 'MLEC', 'MCBCV_1AP', 'MCBRD', 'MQXA', 'MBH_2in1', 'MQT_1AP']

    # magnet_names = all_magnet_names

    magnet_names_not_edited = list(set(all_magnet_names) - set(magnet_names_that_were_edited) - set(magnet_names_to_check))
    print(f"magnet_names_not_edited: {magnet_names_not_edited}")

    # magnet_names = magnet_names_not_edited

    if FLAG_RUN_TEST:
        list_results = []
        for magnet_name in magnet_names:
            print('Magnet: {}'.format(magnet_name))
            flag_test_passed = _compare_to_reference_LEDET(magnet_name, verbose=False)
            if not flag_test_passed:
                list_results.append(magnet_name)
        print(list_results)

    # Substitute the reference files with the output files - THIS IS A VERY DANGEROUS THING TO DO -
    if FLAG_OVERWRITE_REFERENCE:
        print('*** Substitute the reference files with the output files *** THIS IS A VERY DANGEROUS THING TO DO ***')
        for magnet_name in magnet_names_to_overwrite:
            input_file_REFERENCE = os.path.join(tests_folder, 'references', 'magnets', magnet_name, magnet_name + '_REFERENCE.xlsx')
            input_file_GENERATED = os.path.join(tests_folder, 'model_library', 'magnets', magnet_name, 'output', magnet_name + '.xlsx')

            shutil.copyfile(input_file_GENERATED, input_file_REFERENCE)
            print(f'File {input_file_GENERATED} copied to file {input_file_REFERENCE}.')