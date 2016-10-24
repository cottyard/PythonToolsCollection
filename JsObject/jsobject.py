# a python object that thinks it's a js object

def map_dict(func, dict):
    return {k: func(v) for k, v in dict.items()}


class JsObject:
    def __init__(self, json={}):
        self.from_json(json)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        if name not in self._storage:
            raise AttributeError(
                'JsObject "%s" has no attribute "%s"' % (str(self), name))
        return self._storage[name]

    def __setattr__(self, name, value):
        if name in ('_storage', '_datatype'):
            self.__dict__[name] = value
        else:
            self._storage[name] = value

    def __getitem__(self, index):
        return self._storage[index]

    def __setitem__(self, index, value):
        setattr(self, index, value)

    def is_convertible_json(self, data):
        """ whether or not some json data can be converted to a JsObject
        """
        return isinstance(data, (dict, list))

    def from_json(self, json):
        self._storage = {}

        def construct(data):
            return JsObject(data) if self.is_convertible_json(data) else data

        if isinstance(json, dict):
            self._datatype = dict
            for k in json:
                self._storage[k] = construct(json[k])
        elif isinstance(json, list):
            self._datatype = list
            for i in range(0, len(json)):
                self._storage[i] = construct(json[i])
        else:
            raise TypeError('not a json object')

    def to_json(self):
        def construct(jsobj_or_json):
            if not isinstance(jsobj_or_json, JsObject):
                return jsobj_or_json
            else:
                return jsobj_or_json.to_json()

        json_dict = map_dict(construct, self._storage)

        if self.datatype() is dict:
            return json_dict
        else:
            return list(json_dict.values())

    def as_tuple(self):
        return tuple(self._storage.values())

    def as_list(self):
        return list(self._storage.values())

    def as_dict(self):
        return dict(self._storage)

    def datatype(self):
        return self._datatype

    def has_attr(self, name):
        return name in self._storage

    def remove_attr(self, name):
        del self._storage[name]

    def attrs(self):
        return self._storage.keys()

    def values(self):
        return self._storage.values()

    def __iter__(self):
        return iter(self._storage)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{%s}" % ", ".join(
            ("%s: %s" % item for item in self._storage.items()))
