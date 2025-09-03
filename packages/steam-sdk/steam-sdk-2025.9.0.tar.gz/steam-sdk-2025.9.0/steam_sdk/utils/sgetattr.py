from steam_sdk.utils.rgetattr import rgetattr

def rsetattr(obj, attr, val):
    '''
    from https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties

    Set attribute of an object, accepting dotted attr string
    '''
    # pre, _, post = attr.rpartition('.')
    # return setattr(rgetattr(obj, pre) if pre else obj, post, val)

    attrs = attr.split('.')
    for attribute in attrs[:-1]:
        if isinstance(obj, dict):
            obj = obj[attribute]
        elif isinstance(obj, list):
            obj = obj[int(attribute)]
        else:
            obj = getattr(obj, attribute)
    if isinstance(obj, dict):
        obj[attrs[-1]] = val
    else:
        setattr(obj, attrs[-1], val)