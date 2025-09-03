import json
import re

import pandas as pd


def rename_select_columns(df: pd.DataFrame, column_rename_dict: dict = None, rename_file: str = None,
                          rename_key: str = None) -> pd.DataFrame:
    """
    changes the name of dataframe columns and filters to columns in the dictionary.
    assigning new value to None includes the column but does not rename it

    optionally you can use an external json file to store the rename dictionary and avoid code clutter.

    Args:
        df: dataframe to modify
        column_rename_dict: dictionary of column values {old_name:new_name}
        rename_file: path to json file which stores rename dictionary
        rename_key: Your JSON file can store multiple rename dictionaries. This is the key to specify the dictionary
            to use.

    Returns: dataframe only containing specified columns

    See Also: [print_columns_dict][mipi_datamanager.DataManager.print_target_column_dict]

    """

    if rename_file is not None:
        if column_rename_dict is not None:
            raise ValueError("Invalid combination of parameters. rename_file and rename_key can only be used in the absence of column_rename_dict")
        with open(rename_file, 'r') as f:
            json_data = json.load(f)
        if rename_key:
            _rename_dict = json_data[rename_key]
        else:
            _rename_dict = json_data
    elif column_rename_dict is not None:
        _rename_dict = column_rename_dict
    else:
        raise ValueError("Invalid combination of parameters.Must supply either a dictionary or rename file")

    _rename_dict = {k: (v if v is not None else k) for (k, v) in _rename_dict.items()}

    df1 = df.copy()
    target_columns = list(_rename_dict.keys())

    invalid_cols = [col for col in target_columns if col not in df1.columns]
    if invalid_cols:
        raise KeyError(f"Columns: ({invalid_cols}) not found in dataframe.")
    df1 = df1[target_columns]
    df1 = df1.rename(columns=_rename_dict)

    return df1


def coalesce(df: pd.DataFrame, columns: list) -> pd.Series:
    """
    Coalesces columns from a dataframe into a single series. This function is the same as SQL's coalesce() function.
    Column values are given priority in the order that they are passed in.

    Args:
        df: dataframe to coalesce
        columns: list of columns to coalesce

    Returns: coalesced series

    """

    if len(columns) < 2:
        raise KeyError("Must enter at least 2 *column arguments")

    series = df[columns[0]].copy()

    for col in columns[1:]:

        if col not in df.columns:
            raise KeyError("One or more *columns does not exist in the dataframe")

        series = series.combine_first(df[col])
        series.name = None

    return series

def columns_to_space_delim(df:pd.DataFrame) -> pd.DataFrame:
    """
    Converts column names to title case. Expects columns to be snake or camel case

    args:
        df: dataframe to convert

    """
    for col in list(df.columns.values):
        old_name = col
        new_name = old_name.replace('_', ' ')
        new_name = re.sub(r"""
            (            # start the group
                # alternative 1
            (?<=[a-z])  # current position is preceded by a lower char
                        # (positive lookbehind: does not consume any char)
            [A-Z]       # an upper char
                        #
            |   # or
                # alternative 2
            (?<!\A)     # current position is not at the beginning of the string
                        # (negative lookbehind: does not consume any char)
            [A-Z]       # an upper char
            (?=[a-z])   # matches if next char is a lower char
                        # lookahead assertion: does not consume any char
            )           # end the group""",
                          r' \1', new_name, flags=re.VERBOSE)
        new_name = new_name.replace('  ', ' ')
        new_name = ' '.join(
            [w.title() if w not in ['CSN', 'MRN', 'DTTM', 'CMS', 'DOB', 'ID', 'ZID', 'OR', 'MAR', 'BMI'] else w for w in
             new_name.split()])
        df = df.rename(columns={old_name: new_name})

    return df

def _remove_duplicates_and_split_value(s, delim):
    split_values = s.split(f'{delim}')
    unique_values = list(set(split_values))
    return f'{delim}'.join(unique_values)


def remove_duplicates_and_split(series: pd.Series, delim:str) -> pd.Series:
    """
    Splits the values of a SQL `stringagg`

    args:
        series: series to split values in
        delim: delimiter used to separate values
    """
    return series.apply(_remove_duplicates_and_split_value, args=(delim,))