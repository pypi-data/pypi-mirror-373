from pathlib import Path
from typing import Dict
import pandas as pd
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


def custom_function_test_1(dict_inputs: Dict):
    '''
    THIS FUNCTION IS ONLY USED FOR THE test_AnalysisSTEAM.test_AnalysisSTEAM_runCustomPyFunction test
    Test function for the AnalysisSTEAM step of type RunCustomPyFunction
    The function writes a csv file with concatenated outputs 
    '''
    
    test_input_1 = dict_inputs['test_input_1']
    test_input_2 = dict_inputs['test_input_2']
    test_input_3 = dict_inputs['test_input_3']
    test_input_4 = dict_inputs['test_input_4']
    test_input_5 = dict_inputs['test_input_5']
    path_output_file = dict_inputs['path_output_file']
    
    df_to_write = pd.DataFrame()
    df_to_write['test_input_1'] = pd.Series(test_input_1)
    df_to_write['test_input_2'] = pd.Series(test_input_2)
    df_to_write['test_input_3'] = pd.Series(test_input_3)
    df_to_write['test_input_4'] = pd.Series(test_input_4)
    df_to_write['test_input_5'] = pd.Series(test_input_5)

    # Write the dataframe in a .csv file
    make_folder_if_not_existing(Path(path_output_file).parent.absolute())
    df_to_write.to_csv(path_or_buf=path_output_file, sep=',', mode='w', header=True)