import os
import glob
import pandas as pd
from openpyxl import load_workbook

from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.parsers.ParserLEDET import ParserLEDET

# USE WITH CARE! THIS SCRIPT WILL AUTOMATICALLY EDIT LEDET REFERENCE FILES!

if __name__ == "__main__":
    # Input: reference file
    # reference_magnet = 'SMC'
    # sheet_name = 'Variables'
    # reference_file = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'tests', 'builders', 'references', 'magnets', reference_magnet, f'{reference_magnet}_REFERENCE.xlsx')

    # Input: target folder. All .xlsx files containing the suffix in all subfolders will be edited
    folder_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'tests', 'builders', 'references')
    suffix = '_REFERENCE'  # Specify the suffix you want to search for
    # Find files with the specified suffix, excluding those that start with "~"
    target_files = [
        file for file in glob.glob(os.path.join(folder_path, '**', f'*{suffix}*.xlsx'), recursive=True)
        if not os.path.basename(file).startswith('~')
    ]
    # Print the list of found files
    for file in target_files:
        print(file)
    print(f'Found {len(target_files)} files.')

    # For debugging: overwrite the list of file
    reference_magnet = 'dummy_MBH_2in1_with_multiple_QH'
    target_files = [os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'tests', 'builders', 'references', 'magnets', reference_magnet, f'{reference_magnet}_REFERENCE.xlsx')]

    # Read, edit, re-write each .xlsx file
    for target_file in target_files:
        print(f'Reading file {target_file}.')
        try:
            # Read original file
            builder_ledet = BuilderLEDET(flag_build=False, verbose=False)
            pl = ParserLEDET(builder_ledet)
            pl.readFromExcel(target_file, verbose=False)

            # Edit selected variables
            pl.builder_ledet.Variables.variableToSaveTxt = ['time_vector', 'Ia', 'Ib', 'T_ht', 'dT_dt_ht', 'flagQ_ht', 'flagQ_longitudinal_ht', 'IifX', 'IifY', 'Iis', 'dIifXDt', 'dIifYDt', 'dIisDt', 'Uc', 'U_QH', 'T_s_QH', 'time_vector', 'R_CoilSections', 'U_inductive_dynamic_CoilSections', 'I_CoilSections']
            pl.builder_ledet.Variables.typeVariableToSaveTxt = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1]
            pl.builder_ledet.Variables.variableToInitialize = ['Ia', 'Ib', 'T_ht', 'dT_dt_ht', 'flagQ_ht', 'flagQ_longitudinal_ht', 'IifX', 'IifY', 'Iis', 'dIifXDt', 'dIifYDt', 'dIisDt', 'Uc', 'U_QH', 'T_s_QH']

            # Write the file
            pl.writeLedet2Excel(target_file, verbose=False)
            print(f'File {target_file} was edited.')
        except:
            print(f'WARNING. Problem with file {target_file}, which was NOT edited.')