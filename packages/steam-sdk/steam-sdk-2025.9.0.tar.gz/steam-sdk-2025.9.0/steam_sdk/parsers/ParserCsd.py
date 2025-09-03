import pandas as pd
from steam_sdk.parsers.CSD_Reader import CSD_read

def get_signals_from_csd(full_name_file: str, list_signals):
    '''
    Reads a csd file and returns a dataframe with the selected signals
    :param full_name_file: full path to the csv file
    :param list_signals: list of signals to read
    :return: dataframe with the selected signals
    '''

    if type(list_signals) == str: list_signals = [list_signals]           # If only one signal is passed as an argument, make it a list
    csd=CSD_read(full_name_file).data_dict
    csd['time'] = csd['Time']
    del csd['Time']
    # print(csd)
    all_signals_df = pd.DataFrame.from_dict(csd) # read file into a dataframe
    # print(all_signals_df)
    all_signals_df.columns = all_signals_df.columns.str.replace(' ', '')  # eliminate whitespaces from the column names
    list_signals = [x.replace(' ', '') for x in list_signals]             # eliminate whitespaces from the signal names
    return all_signals_df[list_signals]
