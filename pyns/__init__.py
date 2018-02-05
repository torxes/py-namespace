import yaml
import json
import six
import os

from six import StringIO

class JSONEncoder(json.JSONEncoder):
    """
    JSON encoder for `Namespace`.
    """
    def default(self, obj):
        if isinstance(obj, Namespace):
            return obj.raw_dict

        return super(JSONEncoder, self).default(obj)

class NoDefaultType(object):
    pass

class Namespace(object):
    """
    Generic dict like container that allows access via attribute
    access and supported nested containers.
    """

    def __init__(self, data=None, default=NoDefaultType()):
        """
        @param data: Dictionary-like object to initialize namespace
        @param default: Default value to be returned if looked up name is not
                        found (either by item or by attribute access). Default
                        is the special marker `NoDefault` which causes an
                        AttributeError to be raised if a key/name does not
                        exist.
                        If default might also be callable in which case it is
                        invoked upon failing key/name lookup.
        """
        def is_yaml_file(filename):
            return os.path.splitext(data)[1] in ('.yml', '.yaml')

        self.__data = {}
        self.__default = default

        if isinstance(data, six.string_types) and is_yaml_file(data):
            self.load_yaml(data)
        elif data:
            for key, value in six.iteritems(data):
                self[key] = value

    def get(self, name, default=None):
        return self.__data.get(name, default)

    def __getvalue(self, name):
        try:
            return self.__data[name]
        except KeyError:
            if isinstance(self.__default, NoDefaultType):
                raise

            if callable(self.__default):
                return self.__default(name)
            else:
                return self.__default

    def __getattr__(self, name):
        try:
            if name in ['_Namespace__data', '_Namespace__default']:
                return self.__dict__[name]
            else:
               return self.__getvalue(name)
        except KeyError:
            msg = "'%s' object hast no attribute '%s'" % \
                    (self.__class__.__name__, name)
            raise AttributeError(msg)

    def __make_nested(self, value):
        if isinstance(value, dict):
            return Namespace(value)
        elif isinstance(value, (list, tuple)):
            return type(value)((self.__make_nested(i) for i in value))
        else:
            return value

    def __setattr__(self, name, value):
        if name in ['_Namespace__data', '_Namespace__default']:
            self.__dict__[name] = value
        else:
            self.__data[name] = self.__make_nested(value)

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def __contains__(self, key):
        return key in self.__data

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __str__(self):
        cls_name = self.__class__.__name__
        return '%s(%s)' % (
            cls_name, json.dumps(self.__data, indent=2, cls=JSONEncoder)
        )

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '%s(%s)' % (cls_name, json.dumps(self.__data, cls=JSONEncoder))

    def __reduce__(self):
        return (self.__class__, (self.raw_dict, self.__default))

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    @property
    def raw_dict(self):
        """
        Namespace as native dictionary object.
        """
        def make_dict(value, depth):
            if depth and id(value) == id(self):
                raise RuntimeError('Recursion in namespace detected')
            elif isinstance(value, Namespace):
                return { key: make_dict(value[key], depth+1) for key in value }
            elif isinstance(value, (list, tuple)):
                return type(value)((make_dict(i, depth+1) for i in value))
            else:
                return value

        return make_dict(self, 0)

    @property
    def raw_json(self):
        """
        Namespace in JSON.
        """
        return json.dumps(self.__data, cls=JSONEncoder)

    @property
    def raw_yaml(self):
        """
        Namespace in yaml format.
        """
        s = StringIO()
        self.write_yaml(s)
        return s.getvalue()

    def write_yaml(self, fileobj, default_flow_style=False):
        """
        Store namespace in yaml file.

        :param fileobj: File-like object in which data is written.
        """
        yaml.safe_dump(self.raw_dict, fileobj, default_flow_style=default_flow_style)
        fileobj.flush()

    def load_yaml(self, fileobj):
        """
        Load namespace data from file.

        :param fileobj: Filename or file-like object to load data from.
        """
        if isinstance(fileobj, six.string_types):
            with open(fileobj, 'r') as f:
                self._load_yaml(f)
        else:
            self._load_yaml(fileobj)

    def _load_yaml(self, fileobj):
        obj = yaml.load(fileobj)
        data = {}
        for key in obj:
            data[key] = self.__make_nested(obj[key])
        self.__data = data
