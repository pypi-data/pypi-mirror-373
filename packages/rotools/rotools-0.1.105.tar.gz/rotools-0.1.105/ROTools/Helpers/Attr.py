def _split_name(name):
    if isinstance(name, str):
        return name.split(".")

    if not isinstance(name, list):
        raise Exception("Param error")

    return name

def getattr_ex(_obj, name, default=None):
    name = _split_name(name)

    for item in name:
        if _obj is None:
            return default
        _obj = getattr(_obj, item, None)
    return _obj



def setattr_ex(_obj, name, value, parent_class=object):
    name = _split_name(name)

    for item in name[:-1]:
        _next = getattr(_obj, item, None)
        if _next is None:
            _next = parent_class()
            setattr(_obj, item, _next)
        _obj = _next
    setattr(_obj, name[-1], value)


def hasattr_ex(_obj, name):
    name = _split_name(name)

    for i, item in enumerate(name):
        is_last = i == len(name) - 1
        if hasattr(_obj, item) is False:
            return False
        _obj = getattr(_obj, item, None)
        if _obj is None and not is_last:
            return False
    return True


def delattr_ex(_obj, name):
    name = _split_name(name)

    for i, item in enumerate(name):
        is_last = i == len(name) - 1
        if is_last:
            delattr(_obj, item)
            return
        _obj = getattr(_obj, item, None)
        if _obj is None:
            return



