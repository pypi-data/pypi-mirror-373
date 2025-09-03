import functools


def rgetattr(obj, attr, *args):
    '''
    from https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties

    Get attribute of an object, accepting dotted attr string
    '''

    def _getattr(obj, attr):
        if isinstance(obj, list):
            return obj[int(attr)]
        elif isinstance(obj, dict):
            return obj[attr]
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))
