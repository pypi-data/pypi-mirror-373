"""
Users Guide
~~~~~~~~~~~
Read setup file from the user's local. Users can save a `mipi_setup.py` file to their local machine or environment.
Many of the `manager` objects in this package have constructors with large number of complex arguments. The setup file
provides a means for users to universally define arguments for all manager object constructors.

Create a Setup File
~~~~~~~~~~~~~~~~~~~
The SetupFileLoader will look in the following locations for a file named `mipi_setup.py`: {Current Working Directory,
Environment Variable ("MIPI_SETUP_PATH"), Path(sys.prefix, "Lib", "site-packages"),
path passed as SetupFileLoader(filepath = "path/to/mipi_setup.py"))}

Within mipi_setup.py set any constructor argument as `set_{argument_name}` it will be picked up relevant constructors
marked as `uses setup`. This python file is executed upon import, so you can add intermediate logic before setting
arguments.


Developer Guide
~~~~~~~~~~~~~~~
Each manager object has its own `Setup` class. The setup class contains each of variables for the manager's respective
constructor. The setup class by default will look into the `Loader` class to find the variables from the setup file.
values in the setup class can be overwritten or extended using in the `Setup.__init__`. Each manager's setup
class must inherit from the `_Setup` base class. Specify which variables to read from the setup file by declaring
the `SetupField` for each. Specify override functionality in the __init__ statement using the methods exposed by
`_FieldProxy`.

"""

from abc import ABC, abstractmethod
import sys
import os
import importlib.util
from dataclasses import make_dataclass
from pathlib import Path

from pandas.core.interchange.from_dataframe import protocol_df_chunk_to_pandas

from .common import ensure_list
from .jinja import JinjaRepo
from ..formatters import FormatDict, _maybe_convert_to_format_dict

from types import ModuleType, SimpleNamespace
from typing import Sequence, Protocol, Dict, List, Optional, Any


class SetupLoader(Protocol):
    """Load a setup file for mipi objects."""

    def load(self, attrs: Optional[List[str]] = None) -> Dict[str, Any]:
        ...


class _SetupLoader(ABC):
    """Load a setup file for mipi objects."""

    @abstractmethod
    def load(self, attrs: list = None) -> dict:
        """Return the configuration values as a dictionary."""
        raise NotImplementedError


class SetupFileLoader(_SetupLoader):
    """Load the setup from a mipi_setup.py file
    Checks each of the candidate paths and returns the specified values as a dictionary.
    """

    def __init__(self, filepath=None):
        self.filepath = filepath

    @staticmethod
    def _extract_dict_from_mod(mod: ModuleType, attrs: Sequence[str] = None) -> dict:
        if attrs is not None:
            return {a: getattr(mod, f"set_{a}", None) for a in attrs}
        else:
            return dict(mod.__dict__)

    def load(self, attrs=None) -> dict:
        if self.filepath is not None:
            if not os.path.isfile(self.filepath):
                raise FileNotFoundError(f"{self.filepath} was not found.")
            mod = self._import_module(self.filepath)
            return self._extract_dict_from_mod(mod, attrs)
        else:
            for root in self._candidate_roots_generator():
                _maybe_path = Path(root) / "mipi_setup.py"
                if _maybe_path.is_file():
                    mod = self._import_module(_maybe_path)
                    return self._extract_dict_from_mod(mod, attrs)
            raise FileNotFoundError(f"couldn't find mipi_setup.py in search list."
                                    f"See documentation for details on system search path or provide an argument for `setup_path`")

    def _candidate_roots_generator(self):
        yield os.getcwd()

        if os.environ.get("MIPI_SETUP_PATH"):
            yield os.environ.get("MIPI_SETUP_PATH")

        yield Path(sys.prefix, "Lib", "site-packages")

    @staticmethod
    def _import_module(path):
        spec = importlib.util.spec_from_file_location("mipi_setup", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


class SetupNullLoader(_SetupLoader):
    """Load a blank dictionary, for constructors which do NOT use mipi_setup.py"""

    def load(self, attrs=None) -> dict:
        return dict()


class _FieldProxy:
    """Wrapper for the value contained in `SettingField`. Exposes methods to the SettingField attribute, used for
    functionally modifying variables"""

    def __init__(self, value):
        self.value = value

    def override(self, value: Any):
        """override the value in `mipi_setup.py` with a new value"""
        return value

    def append_list_attr(self, value: List[Any]) -> List[Any]:
        """add new values to a list attr"""
        val_list = ensure_list(value)
        res = self.value + val_list
        return res

    def extend_override_dict_attr(self, extend_dict: dict | FormatDict, override_dict: dict | FormatDict):
        """
        Extend or override a dictionary attribute. Required for resolving 2 operations into a single attr.
        At least one of the arguments must be None.

        Args:
            extend_dict: Extend the dictionary attribute, Add additional key value pairs
            override_dict: Totally override the dictionary attribute with a new one.

        Returns:

        """
        if not isinstance(self.value, dict):
            raise TypeError(f"method only available for instance type dict")
        if not isinstance(extend_dict, dict) and not isinstance(override_dict, dict):
            raise TypeError(f"method only available for pramater type dict")
        if override_dict:
            if extend_dict:
                raise ValueError("Invalid parameter combination. Cant override and extend dictionary")
            return _maybe_convert_to_format_dict(override_dict)
        else:
            _dict = self.value
            if _dict is None:
                _dict = FormatDict({})
            if extend_dict is not None:
                _dict.update(extend_dict)
            return _maybe_convert_to_format_dict(_dict)


class _SettingField:
    """
    Descriptor for mipi settings. Defaults to values in mipi_setup.py. and exposes methods in _FieldProxy for override
    """

    def __init__(self, default=None):
        self.default = default

    def __set_name__(self, owner, name):
        # private key where *each instance* will store its own value
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, owner):
        if obj is None:  # accessed on the class
            return self

        if self.private_name in obj.__dict__:
            raw = obj.__dict__[self.private_name]
        else:
            raw = obj._setup.get(self.public_name, self.default)

        return _FieldProxy(raw)

    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)


class _SetupMeta(type):
    """
    Creates an attribute `_fields` containing a list of all SettingFields in the namespace
    """

    def __new__(cls, name, bases, attrs):
        _fields = [k for k, v in attrs.items() if isinstance(v, _SettingField)]
        attrs.update({"_fields": _fields})

        return type.__new__(cls, name, bases, attrs)



class _Setup(metaclass=_SetupMeta):
    """
    Base Class to create a setup object from mipi_setup.py. Must be "exported" before being read by the manager object.
    Inherit from this object, add SettingField for each attribute to be captured from the setup file. Declare attr
    modification logic in the __init__ after calling super().__init__()
    """

    def __init__(self, loader: SetupLoader):
        self._setup = loader.load(self._fields)

    def export_as_dict(self):
        """Export the final resolved setup parameters as a dictionary."""
        result = {}
        for name, attr in self.__class__.__dict__.items():
            if isinstance(attr, _SettingField):
                result[name] = getattr(self, name).value
        return result

    def export_as_object(self):
        """Export the final resolved setup parameters as a dataclass of type `Setup`."""
        result = []
        for name, attr in self.__class__.__dict__.items():
            if isinstance(attr, _SettingField):
                result.append(
                    (name, getattr(self, name).value, type(getattr(self, name).value))
                )
        cls = make_dataclass("Setup", result)
        return cls(**self.export_as_dict())  # TODO remove duplicated loop


class SetupDM(_Setup):
    """
    Setup Object for datamanager class. Provide a loader to determine where `mipi_setup.py` default values are loaded
    from. Then modify those defaults if needed.

    """

    jinja_repo_source = _SettingField()
    store_all_dfs = _SettingField()
    store_base_df = _SettingField()
    default_format_func_dict = _SettingField(default=FormatDict({}))
    insert_table_type = _SettingField()
    insert_table_name = _SettingField()
    dialect = _SettingField()

    def __init__(self,
                 loader: SetupLoader,
                 override_jinja_repo_source: JinjaRepo = None,
                 override_store_all_dfs: bool = None,
                 override_store_base_df: bool = None,
                 override_default_format_func_dict: dict | FormatDict = None,
                 extend_default_format_func_dict: dict | FormatDict = None,
                 override_insert_table_type: str = None,
                 override_insert_table_name: str = None,
                 override_dialect: str = None
                 ):

        super().__init__(loader)

        if override_jinja_repo_source is not None:
            self.jinja_repo_source = self.jinja_repo_source.override(override_jinja_repo_source)

        if override_store_all_dfs is not None:
            self.store_all_dfs = self.store_all_dfs.override(override_store_all_dfs)

        if override_store_base_df is not None:
            self.store_base_df = self.store_base_df.override(override_store_base_df)

        if override_insert_table_type is not None:
            self.insert_table_type = self.insert_table_type.override(override_insert_table_type)

        if override_insert_table_name is not None:
            self.insert_table_name = self.insert_table_name.override(override_insert_table_name)

        if override_dialect is not None:
            self.dialect = self.dialect.override(override_dialect)

        if override_default_format_func_dict is not None or extend_default_format_func_dict is not None:
            self.default_format_func_dict = self.default_format_func_dict.extend_override_dict_attr(
                extend_default_format_func_dict,
                override_default_format_func_dict
            )

class SetupFS(_Setup):
    """
    Setup Object for datamanager class. Provide a loader to determine where `mipi_setup.py` default values are loaded
    from. Then modify those defaults if needed.

    """

    search_directories = _SettingField()
    search_extensions = _SettingField()
    copy_destinations = _SettingField()

    def __init__(self,
                 loader: SetupLoader,
                 append_search_directories: List[str] | str = None,
                 append_search_extensions: List[str] | str = None,
                 append_copy_destinations: List[str] | str = None,
                 ):

        super().__init__(loader)

        if append_search_directories is not None:
            self.search_directories = self.search_directories.override(append_search_directories)

        if append_search_directories is not None:
            self.search_extensions = self.search_extensions.override(append_search_extensions)

        if append_copy_destinations is not None:
            self.copy_destinations = self.copy_destinations.override(append_copy_destinations)
