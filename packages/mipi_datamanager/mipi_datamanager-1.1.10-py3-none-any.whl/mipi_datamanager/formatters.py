"""
When performing joins it is common to apply a format to both sides of the join to ensure that the values match correctly.

The [DataManager][mipi_datamanager.DataManager] has a means to apply formatting to specifically declared columns. MiPi

provides some preset formatting tools. The FormatDict stores format functions within the DataManager. MiPi also provides

some preset format function templates. These functions are prefixed with `cast_`, some take parameters to allow you to

customize your format, and all of them will return a callable. All formatters drop NA values.

"""

import warnings
from datetime import datetime
from typing import Callable, final, Self

import numpy as np
import pandas as pd

class FormatDict(dict):
    """
    This class is designed to store format functions within the [DataManager][mipi_datamanager.DataManager].
    It is a child of dictionary and contains an additional method to assign many keys to the same value.

    TODO show example adding one of my callables (cast)


    Examples:
        >>> from mipi_datamanager import DataManager
        >>> from mipi_datamanager.formatters import FormatDict
        >>> import pandas as pd
        >>> format_dict = FormatDict({"a":lambda x: 2*x})
        >>> format_dict.update({["b","c"]:lambda x: 10*x})
        >>> df = pd.DataFrame({'a':[1,2,3], 'b':[4,5,6],'c':[7,8,9],'d':[10,11,12]})
        >>> mipi = DataManager.from_dataframe(df,default_format_func_dict=format_dict)
        >>> mipi.trgt
        pd.DataFrame({'a':[2,4,6], 'b':[40,50,60],'c':[70,80,90],'d':[10,11,12]})

    """
    def update_group(self,columns:list, func:Callable) -> None:

        """
        Updates a group of keys to be assigned to the same value. This is useful when many columns need to use the
        same format function

        Args:
            columns: Columns to assign to the specified function
            func: Function to assign to the specified keys

        Examples:
            >>> my_format_dict = FormatDict({'a':lambda x: x, 'b':lambda x: 2*x})
            >>> my_format_dict.update_group(['c','d'], lambda x: x*x)
            >>> my_format_dict
            {'a':lambda x: x, 'b':lambda x: 2*x,'c':lambda x: x*x, 'd':lambda x: x*x}
        """

        for c in columns:
            self._validate(c,func)
            self[c] = func
    def __setitem__(self,key,value) -> None:
        self._validate(key,value)
        super().__setitem__(key,value)

    def update(self, *args, **kwargs):
        # Handle dictionary or iterable of key-value pairs
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self._validate(key, value)
                    super().__setitem__(key, value)
            elif hasattr(arg, "__iter__"):  # Handle iterable of key-value pairs
                for key, value in arg:
                    self._validate(key, value)
                    super().__setitem__(key, value)
            else:
                raise TypeError(f"Setter expected type 'callable' got: {type(arg)}")

        # Handle keyword arguments
        for key, value in kwargs.items():
            self._validate(key, value)
            super().__setitem__(key, value)


    def _validate(self, key,value):
        '''assert that the single func is callable and the dict is a dict of callables'''
        if not callable(value):
            raise TypeError(f"Setter for key:{key} expected type 'callable' got: {type(value)}")

    def _format_series(self, series):

        if not isinstance(series, pd.Series):
            raise TypeError(f"series must be pd.Series, got {type(series)}")

        key = series.name
        if key in self:
            self._validate(key,self.get(key))
            format_func = self[key]
            return format_func(series)
        else:
            return series


    @final
    def format_incoming_df(self, df, override_formatter: dict|Self = None):  # , on=None, side_on=None, use_index=False):

        if override_formatter is not None:
            if not isinstance(override_formatter, (FormatDict,dict)):
                raise TypeError(f"override_formatter must be FormatDict or None, got {type(override_formatter)}")

        if override_formatter:
            _override = _maybe_convert_to_format_dict(override_formatter)
        else:
            _override = {}

        for c in df.columns:
            if c in _override:
                df[c] = _override._format_series(df[c])
            elif c in self:
                df[c] = self._format_series(df[c])
        return df


def _maybe_convert_to_format_dict(dict_):
    if isinstance(dict_, dict):
        return FormatDict(dict_)
    elif isinstance(dict_, FormatDict):
        return dict_
    elif dict_ is None:
        return FormatDict({})
    else:
        raise ValueError(
            f"default_format_func_dict must be a dict|FormatDict, got {type(dict_)}")

def _drop_na(series):
    if series.isna().any():
        series = series.dropna()
        warnings.warn("Na values were dropped during formatting.")
    return series


def cast(data_type) -> Callable:
    """
    Cast a series as a specific data type, equivelent to pd.Series.astype()
    Args:
        data_type: builtin formatter to apply to the series

    Examples:
        >>>my_series = pd.Series([1.0,"2",3],name="my_ints")
        >>>formatter = cast(int)
        >>>formatter(my_series)
        pd.Series([1,2,3],name="my_ints")


    Returns:

    """

    if not isinstance(data_type, (np.dtype,type)):
        raise TypeError(f"Expected parameter to be of type np.dtype | type, got {type(data_type)}")

    def cast_func(series):
        series = _drop_na(series)
        return series.astype(data_type)

    return cast_func


def cast_int_str(errors:str = "ignore") -> Callable:
    """
    Casts a series as an interger value represented as a string.

    Args:
        errors: how to handle errors. see pandas DataFrame.astype() documentation. {raise, ignore} #TODO why does this say required on dox?

    Returns:

    Examples:
        >>>my_series = pd.Series([1.0,"2",3],name="my_ints")
        >>>formatter = cast_int_str()
        >>>formatter(my_series)
        pd.Series(['1','2','3'],name="my_ints")

    """
    def cast_func(series):
        series = _drop_na(series)
        return series.astype("int64", errors=errors).astype(str, errors=errors)

    return cast_func


def cast_padded_int_str(cell_width:int, errors:str = "ignore") -> Callable:
    """
    Casts a series as an interger value represented as a string. Values are padded on to the left with zeros.

    Args:
        cell_width: Final number of characters (after padding) in each cell of the dataframe.
        errors: how to handle errors. see pandas DataFrame.astype() documentation. {raise, ignore}

    Returns:

    Examples:
        >>>my_series = pd.Series([1.0,"2",3],name="my_ints")
        >>>formatter = cast(3)
        >>>formatter(my_series)
        pd.Series(['001','002','003'],name="my_ints")

    """


    def cast_func(series) -> pd.Series:
        series = _drop_na(series)
        cast_int_str_func = cast_int_str(errors=errors)
        series = cast_int_str_func(series)

        return series.where(~series.str.startswith('-'),
                            '-' + series.str[1:].str.rjust(cell_width, "0")).str.rjust(cell_width, "0")

    return cast_func


def cast_as_datetime():
    def cast_func(series: pd.Series) -> pd.Series:
        _series = _drop_na(series)
        _series = pd.to_datetime(_series)
        return series

    return cast_func


def cast_as_datetime_string(format_code):

    def cast_func(series: pd.Series):
        _series = _drop_na(series)
        _series = pd.to_datetime(_series)
        _series = _series.dt.strftime(format_code)
        return _series

    return cast_func


def cast_as_iso_date_string(date_delim="-", time_delim=":",sep = " "):

    def cast_func(series: pd.Series):
        _series = _drop_na(series)
        format_string = f"%Y{date_delim}%m{date_delim}%d"
        if time_delim:
            format_string += f"{sep}%H{time_delim}%M{time_delim}%S"
        format_func = cast_as_datetime_string(format_string)
        return format_func(series)

    return cast_func


def cast_as_american_date_string(date_delim="/", time_delim=":",sep = " "):
    def cast_func(series: pd.Series) -> pd.Series:
        _series = _drop_na(series)
        format_string = f"%m{date_delim}%d{date_delim}%Y"
        if time_delim:
            format_string += f"{sep}%H{time_delim}%M{time_delim}%S"
        format_func = cast_as_datetime_string(format_string)
        return format_func(series)

    return cast_func
