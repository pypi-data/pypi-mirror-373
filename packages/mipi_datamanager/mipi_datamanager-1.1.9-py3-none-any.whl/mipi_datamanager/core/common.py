from typing import Any, Sequence
from pathlib import Path

def read_text_file(file: str | Path, encoding ="utf-8") -> str:
    with open(file, "r",encoding = encoding) as f:
        contents = f.read()
    return contents


def _maybe_add_lists(list_of_lists):
    if not isinstance(list_of_lists, list):
        _list_of_lists = [list_of_lists]

    final_list = []
    for list_i in list_of_lists:
        final_list += list_i

    return final_list


def _maybe_convert_tuple_to_list(val: list | tuple):
    if isinstance(val, tuple):
        return list(val)
    elif isinstance(val, list):
        return val
    else:
        raise TypeError(f'Expected tuple or list, got {type(val)}')


def ensure_list(val: Any) -> list:
    """
    Wrap a single value in a list, or convert a list-like object into a list if it isnt one
    """
    if isinstance(val, list):
        return val
    if isinstance(val, Sequence) and not isinstance(val, (str, bytes)):
        return list(val)
    return [val]


def dict_to_string(dictionary: dict):
    """

    creates a clean string representation of a dictionary

    Args:
        dictionary: any dictionary
        block_pad: int: number of lines to pad top and bottom of output

    Returns: Clean string representation of the dictionary

    """

    max_key_length = max(len(str(key)) for key in dictionary.keys())
    max_value_length = max(len(str(value)) for value in dictionary.values())

    output = ""
    for i, (key, value) in enumerate(dictionary.items()):
        if i != 0:
            output += ","
        output += f"{str(key):<{max_key_length}} : {str(value):>{max_value_length}}\n"

    return output

def _maybe_rename_values(value: str|list, rename:dict):
    if rename is None:
        _rename = {}
    else:
        _rename = rename

    if isinstance(value, str):
        if value in _rename:
            return rename[value]
        else:
            return value
    elif isinstance(value, list):
        return [_rename[i] if i in _rename else i for i in value]
    else:
        raise TypeError(f"expected type string or list got {type(value)}")

def _columns_to_dict(df):
    return {f"'{col}'": None for col in df.columns.tolist()}

def _dict_to_string(dictionary: dict):
    """

    creates a clean string representation of a dictionary

    Args:
        dictionary: any dictionary
        block_pad: int: number of lines to pad top and bottom of output

    Returns: Clean string representation of the dictionary

    """
    if not isinstance(dictionary, dict):
        raise TypeError(f"expected dict got {type(dictionary)}")

    if len(dictionary) == 0:
        raise ValueError("Dictionary is empty")

    max_key_length = max(len(str(key)) for key in dictionary.keys())
    max_value_length = max(len(str(value)) for value in dictionary.values())

    output = ""
    for i, (key, value) in enumerate(dictionary.items()):
        if i != 0:
            output += ","
        output += f"{str(key):<{max_key_length}} : {str(value):>{max_value_length}}\n"

    return output

class IndexedDict(dict):
    """
    A dictionary object that allows you to access items by their key index.
    The key index is the suffix of the key.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.keys():
            self._validate_key(key)

    def _validate_key(self, key):
        if not isinstance(key, str):
            raise TypeError('Key must be a string')

        suffix = key.split("_")[-1]
        prefix = key.split("_")[0]

        if not suffix.isnumeric() or "_" not in key or len(prefix) == 0:
            raise ValueError('Key must have a string name followed by an underscored numeric suffix "{keyname}_{index_number}"')

        if suffix in [k.split("_")[-1] for k in self.keys() if k != key]:
            raise ValueError('A key with that suffix already exists')


    def __setitem__(self, key, value):
        self._validate_key(key)
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if isinstance(key, str):
            return super().__getitem__(key)
        if isinstance(key, int):
            ks = [k for k in self.keys() if k.endswith(str(key))]
            assert len(ks) == 1, f"Assertion filed, multiple Keys exist for index{key}"
            k = ks[0]
            return super().__getitem__(k)
    def update(self, other, **kwargs):
        if isinstance(other, dict):
            for key in other.keys():
                self._validate_key(key)
        for key in kwargs.keys():
            self._validate_key(key)
        super().update(other, **kwargs)
    def get(self, key, default=None):
        if isinstance(key, str):
            return super().get(key, default)
        if isinstance(key, int):
            ks = [k for k in self.keys() if k.endswith(str(key))]
            if len(ks) == 1:
                return super().__getitem__(ks[0])
            return default

class EnsureList:
    def __set_name__(self, owner: type, name: str):
        # called once, per attribute, at class creation time
        self.private_name = f"_{name}"

    def __get__(self, instance, owner: type):
        if instance is None:
            return self
        # if not yet set, default to empty list
        return getattr(instance, self.private_name, [])

    def __set__(self, instance, value: Any):
        if value is None:
            set_val = []
        else:
            set_val = ensure_list(value)
        setattr(instance, self.private_name, set_val)

