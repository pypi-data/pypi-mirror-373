from steam_sdk.utils.rgetattr import rgetattr


def rhasattr(obj, attr):
    '''
    Check if an attribute is present in an object, accepting dotted attr string
    '''
    
    split_attr = attr.split('.')
    
    if len(split_attr) == 1:
        result = hasattr(obj, attr)
        return result
    else:
        new_obj = rgetattr(obj, split_attr[0])
        new_attr = '.'.join(split_attr[1:])
        return rhasattr(new_obj, new_attr)
