import pytest
import json
import pickle

from collections import defaultdict

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from pyns import Namespace, JSONEncoder


@pytest.fixture(params=[dict, lambda d: defaultdict(None, d)])
def flat_data(request):
    return request.param({
        'key1': 'value1',
        'key2': ['1', '2', '3']
    })


nested_data_dict = {
    'key1': 'value1',
    'key2': {
        'key2_1': 'value2_1',
    },
    'key3': [{'key3_1': 'value3_1'}]
}


@pytest.fixture(params=[dict, lambda d: defaultdict(None, d)])
def nested_data(request):
    return request.param(nested_data_dict)


def test_namespace_is_string_representable(nested_data):
    ns_str = str(Namespace(nested_data))

    for key in nested_data:
        assert str(key) in ns_str


def test_namespace_is_representable(nested_data):
    ns_repr = repr(Namespace(nested_data))

    for key in nested_data:
        assert str(key) in ns_repr


def test_namespace_supports_contains_check():
    ns = Namespace({'foo': 42})

    assert 'foo' in ns
    assert 'bar' not in ns


def test_namespace_supports_key_iteration():
    data = {'key1': 1, 'key2': 2}
    ns = Namespace(data)

    for key in ns:
        assert key in data


def test_namespace_supports_len():
    data = {'key1': 1, 'key2': 2}
    ns = Namespace(data)

    assert len(ns) == len(data)


def test_value_is_correctly_return_by_attribute_access():
    nn = Namespace()
    nn.foo = 42

    assert nn.foo == 42


def test_value_is_correctly_return_by_item_access():
    nn = Namespace()
    nn.foo = 42

    assert nn['foo'] == 42


def test_value_from_initial_dict_is_correctly_stored(flat_data):
    nn = Namespace(flat_data)

    assert nn.key1 == 'value1'


def test_nested_dictionary_accessible_via_chain_attribute_access(nested_data):
    nn = Namespace(nested_data)

    assert nn.key1 == 'value1'
    assert nn.key2.key2_1 == 'value2_1'


def test_nested_dictionary_accessible_via_chaining_item_access(nested_data):
    nn = Namespace(nested_data)

    assert nn['key1'] == 'value1'
    assert nn['key2']['key2_1'] == 'value2_1'


def test_iterating_over_namespace_yields_key_names(nested_data):
    nn = Namespace(nested_data)

    for key in nn:
        assert key in nested_data


def test_assign_dictionary_is_accessible_via_attribute_lookup():
    nn = Namespace()
    nn.nested = {'foo': 'bar'}

    assert nn.nested.foo == 'bar'


def test_init_converts_dict_nested_in_list_to_nested_namespace(nested_data):
    nn = Namespace(nested_data)

    assert isinstance(nn.key3[0], Namespace)
    assert nn.key3[0].key3_1 == 'value3_1'


def test_attribute_assignment_converts_dict_nested_in_list_to_nested_namespace(nested_data):
    nn = Namespace()

    nn.item = [{'key1': 'value1'}]

    assert isinstance(nn.item[0], Namespace)
    assert nn.item[0].key1 == 'value1'


def test_namespace_is_json_encodable(nested_data):
    ns = Namespace(nested_data)

    json_data = json.dumps(nested_data, sort_keys=True)
    json_ns = json.dumps(ns, sort_keys=True, cls=JSONEncoder)

    assert json_data == json_ns


def test_raw_dict_returns_nested_dict(nested_data):
    data = Namespace(nested_data).raw_dict

    assert type(data) is dict
    assert type(data['key2']) is dict
    assert type(data['key3'][0]) is dict


def test_write_yaml_dumps_to_fileobj(nested_data):
    expected = '''\
key1: value1
key2:
  key2_1: value2_1
key3:
- key3_1: value3_1'''
    ns = Namespace(nested_data)
    fileobj = StringIO()

    ns.write_yaml(fileobj)

    print('\n'.join('%s|' % l for l in fileobj.getvalue().split('\n')))
    assert fileobj.getvalue().strip() == expected


def test_write_and_load_yaml_results_same_data(tmpdir):
    src = Namespace(nested_data_dict)
    dest = Namespace()

    fn = str(tmpdir.join('file.yaml'))
    with open(fn, 'w') as f:
        src.write_yaml(f)

    with open(fn, 'r') as f:
        dest.load_yaml(f)

    assert src.raw_dict == dest.raw_dict


def test_load_yaml_from_filename(tmpdir):
    src = Namespace(nested_data_dict)
    dest = Namespace()

    fn = str(tmpdir.join('file.yaml'))
    with open(fn, 'w') as f:
        src.write_yaml(f)

    dest.load_yaml(fn)

    assert src.raw_dict == dest.raw_dict


def test_init_with_yaml_filename_loads_data_from_file(tmpdir):
    src = Namespace(nested_data_dict)

    fn = str(tmpdir.join('file.yaml'))
    with open(fn, 'w') as f:
        src.write_yaml(f)

    dest = Namespace(fn)

    assert src.raw_dict == dest.raw_dict


def test_access_to_nonexistant_attribute_raises_attribute_error():
    ns = Namespace()
    with pytest.raises(AttributeError):
        x = ns.key


def test_raw_json_returns_json_representation():
    ns = Namespace({'key1': 'value1', 'key2': {'value2': 42}})

    assert json.loads(ns.raw_json)


def test_json_encoder_returns_dict_for_namespace():
    ns = Namespace()
    encoder = JSONEncoder()

    assert type(encoder.default(ns)) is dict


def test_json_encoder_returns_throws_for_unknown_objects():
    class Obj(object):
        pass

    encoder = JSONEncoder()
    with pytest.raises(TypeError, match='is not JSON serializable'):
        encoder.default(Obj())


def test_returns_default_value_if_key_does_not_exists():
    ns = Namespace(default=42)

    assert ns.foo == 42


def test_invoke_default_handler_if_key_does_not_exists():
    ns = Namespace(default=lambda name: 42)

    assert ns.foo == 42


def test_get_method_returns_value_for_key():
    ns = Namespace({'foo': 'bar'})

    assert ns.get('foo') == 'bar'


def test_get_method_returns_none_if_key_does_not_exist():
    ns = Namespace()

    assert ns.get('foo') is None


def test_get_method_returns_default_value_if_key_does_not_exist():
    ns = Namespace()

    assert ns.get('foo', 'bar') == 'bar'


def test_raw_dict_detects_recursion_and_raises_error():
    ns = Namespace()
    ns.foo = ns

    with pytest.raises(RuntimeError):
        ns.raw_dict


def test_namespace_is_pickleable(nested_data):
    ns = Namespace(nested_data)

    pns = pickle.loads(pickle.dumps(ns))

    assert pns.raw_dict == ns.raw_dict


def test_non_existent_keys_with_separator_leads_to_new_nested_value():
    ns = Namespace(key_sep='.')

    ns['foo.bar'] = 'value'

    assert ns.foo.bar == 'value'


def test_existent_keys_with_separator_updates_nested_value():
    ns = Namespace({'foo': {'bar': 'oldvalue' }}, key_sep='.')

    ns['foo.bar'] = 'value'

    assert ns.foo.bar == 'value'


def test_keys():
    dct = {'key1': 0, 'key2': 1}
    ns = Namespace(dct)

    assert sorted(ns.keys()) == sorted(dct.keys())


def test_values():
    dct = {'key1': 0, 'key2': 1}
    ns = Namespace(dct)

    assert sorted(ns.values()) == sorted(dct.values())


def test_items():
    dct = {'key1': 0, 'key2': 1}
    ns = Namespace(dct)

    for key, value in ns.items():
        assert dct[key] == value


def test_init_namespace_from_other_transfers_default_and_keysep():
    dct = {'key1': 0, 'key2': 1}
    other = Namespace(dct, default=42, key_sep='@')

    ns = Namespace(other)

    assert ns._Namespace__default == 42
    assert ns._Namespace__key_sep == '@'
    assert ns.raw_dict == dct
