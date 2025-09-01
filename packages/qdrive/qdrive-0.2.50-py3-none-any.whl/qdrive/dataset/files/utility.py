def is_iterable(object):
    if isinstance(object, (dict, list, tuple)):
        return True
    return False

def is_scalar(object):
    if isinstance(object, (str, int, float, bool)):
        return True
    return False