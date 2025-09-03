# dictflat

A Python library to flatten a dictionary with nested dictionnaries and lists

## Use cases

Transform a dictionary structure into a new organization ready to be inserted into a relational database.

## Installation

```bash
poetry add dictflat
```

## Quick start

```python
>>> from dictflat import DictFlat
>>> import json
>>> r = DictFlat(
    root_key="root"
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        },
        "Phone_Numbers": [
            {"type": "home", "number": "555-1234"},
            {"type": "work", "number": "555-5678"},
        ],
    }
)
>>> print("%s" % json.dumps(r, indent=2))
{
  "root": [
    {
      "__id": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "name": "John",
      "pers_id": 12
    }
  ],
  "root.birth": [
    {
      "__id": "e72d549a-89f5-4208-99c0-4ce3493cbf9e",
      "__ref__root": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "date": "10/06/1976 01:10:35"
    }
  ],
  "root.birth.address": [
    {
      "__id": "cc489c03-82ca-4b6e-a620-32c9c4be236c",
      "__ref__root.birth": "e72d549a-89f5-4208-99c0-4ce3493cbf9e",
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA"
    }
  ],
  "root.Phone_Numbers": [
    {
      "__id": "ba1560de-9c4c-4886-b4ca-684e0a7e5df0",
      "__ref__root": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "type": "home",
      "number": "555-1234"
    },
    {
      "__id": "f1032025-6c7d-4341-8e6a-f0dce2374388",
      "__ref__root": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "type": "work",
      "number": "555-5678"
    }
  ]
}
```

The result is always a dictionary where each key is a reference to the original dictionary.

* In this example, the original root document is identified by the token “`root`” (the root key) and the "`address`" sub-dictionary is identified by “`root.address`”.

Each dictionary value is always a list. See below for more examples with more than one element in lists.

Each sub-dictionnary have:

* an unique field named "`__id`" (like a primary key)
* except for root, a "`__ref__root`" who contains the "`__id`" value of parent dictionnary;
  * the "`root`" token in "`__ref__root`" field name is directly a reference to the global result dictionnary.

## Documentation

All examples explained in documentation come from [module tests](https://github.com/ArnaudValmary/py_dictflat/blob/main/tests/test_dictflat).

1. [Basic usages](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/01_basic_usages.md)
1. [Nested dictionnaries](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/02_nested_dictionnaries.md)
1. [Generate IDs](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/03_generate_ids.md)
1. [Change values](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/04_change_values.md)
1. [Drop fields](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/05_drop_fields.md)
1. [Rename fields](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/06_rename_fields.md)
1. [Lists](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/07_lists.md)
1. [Squash dictionnaries](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/08_squash_dictionnaries.md)
1. [Simple keys](https://github.com/ArnaudValmary/py_dictflat/blob/main/doc/09_simple_keys.md)
