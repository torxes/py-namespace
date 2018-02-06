# pyns - Nested Python Namespaces
[![Build Status](https://travis-ci.org/torxes/py-namespace.svg?branch=master)](https://travis-ci.org/torxes/py-namespace)

**Key Features:**
- Attribute and subscript-like 
- Load from and save to YAML files
- JSON representation
- Picklable

Install
-------

Install from GitHub:
```
$ pip install git+https://github.com/torxes/py-namespace.git
```

Install from source:
```
$ git clone https://github.com/torxes/py-namespace.git
$ cd py-namespace
$ python setup.py install
``` 

Getting Started
---------------

```pycon
>>> from pyns import Namespace
>>> ns = Namespace({'name': 'John Doe', 'address': 'Doe Lane 42'})
>>> print(ns)
Namespace({
  "address": "Doe Lane 42",
  "name": "John Doe"
})
>>> ns['name']
'John Doe'
>>> ns.name
'John Doe'
```

Nested namespace
```pycon
>>> ns = Namespace({'address': { 'street': 'Doe Lane 1', 'city': 'Doetown'}})
>>> print(ns)
Namespace({
  "address": {
    "street": "Doe Lane 1",
    "city": "Doetown"
  }
})
>>> ns.address.street = 'New Street 2'
>>> ns.address.street
'New Street 2'
```

YAML support
```pycon
>>> ns = Namespace('data.yml')
>>> ns.name = 'value'
>>> ns.write_yaml('data.yml')
```
