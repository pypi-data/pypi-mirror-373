import os
from typing import List, Union

import numpy as np
import pandas as pd

from steam_sdk.parsers.ParserCsd import get_signals_from_csd
from steam_sdk.parsers.ParserCsv import get_signals_from_csv
from steam_sdk.parsers.ParserMat import get_signals_from_mat_to_dict
from steam_sdk.parsers.ParserPSPICE import read_time_stimulus_file


def get_signals_from_file(full_name_file: str, list_signals: Union[str, List[str]] = [], dict_variable_types: dict = {}):
    '''
    Reads a file and returns a dictionary with the selected signals.
    Supported file types: .csd, .csv, .mat
    The function will deduce the file type from the file extension.
    In the case of a .csv file, the function supports:
    - column-by-column reading (file must contain a one-row header with comma-separated names)
    - matrix reading (file must contain a one-row header that does not contain any commas. In this case, argument list_signals is ignored)
    - scalar reading (file must contain a one-row header that does not contain any commas, and have only one element. In this case, argument list_signals is ignored)
    :param full_name_file: full path to the file
    :param list_signals: list of signals to read
    :param dict_variable_types: Optional variable to define the type of variable to read from a .mat file (the values in the dictionary can be "0D", "1D", or "2D")
    :type dict_variable_types: dict
    :return: dictionary with the selected signals
    '''

    # If only one signal is passed as an argument, make it a list
    if type(list_signals) == str:
        list_signals = [list_signals]
    list_signals = [x.replace(' ', '') for x in list_signals]  # eliminate whitespaces from the signal names

    # If the file is a mat file, read it and convert the csv file to the output csv sim folder
    _, file_type = os.path.splitext(full_name_file)

    if file_type == '.csd':
        # Read the signals as a dataframe
        df_signals = get_signals_from_csd(full_name_file, list_signals)
        # Assign them to a dict where each key is an array represented as a column vector
        dict_signals = {}
        for column in df_signals.columns:
            dict_signals[column] = df_signals[column].values
        return dict_signals
    elif file_type == '.csv' or file_type == '.txt':
        # Check whether the file should be read column by column or as a single variable
        with open(full_name_file, 'r') as file:
            if ',' in file.readline():
                flag_column_file = True
            else:
                flag_column_file = False

        if flag_column_file == True:
            # Read this file column by column, where each column is a different variable
            # Read the signals as a dataframe
            df_signals = get_signals_from_csv(full_name_file, list_signals)
            # Assign them to a dict where each key is an array represented as a column vector
            dict_signals = {}
            for column in df_signals.columns:
                dict_signals[column] = df_signals[column].values
            return dict_signals
        else:
            # Read this file as a csv containing only one variable
            np_signal = pd.read_csv(full_name_file, delimiter=',', engine='python', skiprows=1, header=None).to_numpy()
            if np_signal.shape == [1, 1]:
                # If the file contains only one value, return a scalar
                return np_signal[0, 0]
            else:
                # Otherwise, return a np.array (typically a matrix)
                return np_signal
    elif file_type == '.mat':
        # Read the signals as a dict
        dict_signals = get_signals_from_mat_to_dict(full_name_file, list_signals, bool_transpose=True, dict_variable_types=dict_variable_types)
        return dict_signals
    elif file_type == '.stl':
        # Read the signals as a dict where each key is a signal with subkeys 'time' and 'value'
        # Note that this structure differs from that of the other file types
        temp_dict = read_time_stimulus_file(path_file=full_name_file, name_time_signal='time', name_value_signal='value')
        # Assign signals to a dict where each key is an array represented as a column vector (this will raise an exception is a selected signal is not present)
        if len(list_signals) == 0:
            list_signals = temp_dict.keys()
        dict_signals = {key: temp_dict[key] for key in list_signals if not key == 'time'}  # Note: signal 'time' is ignored
        return dict_signals
    else:
        raise Exception(f'File type {file_type} not supported.')
