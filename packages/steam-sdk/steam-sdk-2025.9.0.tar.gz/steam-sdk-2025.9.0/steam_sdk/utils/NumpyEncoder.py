import numpy as np
import json


class NumpyEncoder(json.JSONEncoder):
    '''
        ** Helper class for dumping np.arrays in json files **
    '''

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)