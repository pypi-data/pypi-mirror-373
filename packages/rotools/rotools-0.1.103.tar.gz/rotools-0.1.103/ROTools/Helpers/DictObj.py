import copy
from datetime import datetime, date

from ROTools.Helpers.Attr import setattr_ex, hasattr_ex, getattr_ex, delattr_ex
from ROTools.Helpers.DumpBase import DumpBase


def _gen_fields_list(obj, current_path=None):
    if not isinstance(obj, DictObj):
        return [(current_path, obj)]
    result = []
    for key, value in obj.items():
        next_path = ".".join([a for a in (current_path, key) if a is not None])

        if isinstance(value, DictObj):
            result.extend(_gen_fields_list(value, current_path=next_path))
        else:
            result.append((next_path, value))
    return result

def _convert_to_dict(obj):
    if isinstance(obj, DictObj):
        return obj.to_dict()

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, date):
        return obj.isoformat()

    if isinstance(obj, list) or isinstance(obj, tuple):
        return [_convert_to_dict(a) for a in obj]

    return obj


class DictObj(DumpBase):
    def __init__(self, d=None):
        if d is None:
            return
        if isinstance(d, DictObj):
            for k, v in d.__dict__.items():
                self.__dict__[k] = copy.deepcopy(v)
            return

        if isinstance(d, dict):
            self._build_dict(d)
            return

        raise Exception("Flow")

    def _build_dict(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [DictObj(x) if isinstance(x, dict) else x for x in b])
                continue
            setattr(self, a, DictObj(b) if isinstance(b, dict) else b)

    def get(self, path, default=None):
        return getattr_ex(self, path, default)

    def set(self, path, value):
        setattr_ex(self, path, value, parent_class=DictObj)

    def rem(self, path):
        return delattr_ex(self, path)

    def has(self, path):
        return hasattr_ex(self, path)

    def set_default(self, path, value):
        if not hasattr(self, path):
             setattr_ex(self, path, value, parent_class=DictObj)

    def set_values(self, values, only_if_exists=True):
        for path, nev_value in values:
            if only_if_exists and not hasattr_ex(self, path):
                continue
            self.set(path, nev_value)

    def to_dict(self):
        result = {}
        for k, v in self.__dict__.items():
            result[k] = _convert_to_dict(v)
        return result

    def fields_list(self):
        return _gen_fields_list(self)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def clone(self):
        import copy
        return copy.deepcopy(self)
