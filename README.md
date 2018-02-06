# pyns - Nested Python Namespaces
[![Build Status](https://travis-ci.org/torxes/py-namespace.svg?branch=master)](https://travis-ci.org/torxes/py-namespace)

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
```
