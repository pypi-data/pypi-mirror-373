import numpy as np
import pandas as pd


def clean_NaN_from_signal(signal: np.array, method: str = 'ffill'):
    '''
    Helper method to fill the NaN values of a np.array with different strategies. For explanation of the methods, please see
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html
    :param signal: np.array of signal
    :param method: Policy to replace NaN values
    :return: np.array
    '''
    if method not in ['bfill', 'pad', 'ffill']:
        raise Exception(f'Method not understood. {method} is not in bfill, pad, ffill')
    df = pd.DataFrame(signal)
    df = df.fillna(method=method)
    return df.to_numpy().flatten()