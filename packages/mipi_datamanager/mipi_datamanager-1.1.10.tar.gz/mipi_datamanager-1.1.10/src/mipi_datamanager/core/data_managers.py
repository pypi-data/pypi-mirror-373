import importlib.util
import sys
import warnings, os, json
from collections import ChainMap
from dataclasses import dataclass
from typing import Callable, overload, final, Self
from pathlib import Path
from pandas.errors import MergeError
import pandas as pd
from jinja2 import Template

from mipi_datamanager.core.common import _maybe_rename_values, read_text_file
from mipi_datamanager.formatters import FormatDict
from mipi_datamanager import query, connection, generate_inserts
from mipi_datamanager.core import common as com
from mipi_datamanager.core import meta
from mipi_datamanager.core.read_setup import SetupDM, SetupFileLoader, SetupNullLoader
from mipi_datamanager.types import JoinLiterals, Mask
from mipi_datamanager.errors import ConfigError
from mipi_datamanager.core.jinja import JinjaLibrary, JinjaRepo


def _get_df_and_sql_from_jinja_template(jenv, script_path, connection,
                                        jinja_parameters_dict):  # TODO these are redundant
    df = jenv.execute_file(script_path, connection, jinja_parameters_dict)
    sql = jenv.resolve_file(script_path, jinja_parameters_dict)
    del jenv
    return df, sql


def _get_df_and_sql_from_jinja_repo(jinja_repo_source, inner_path, connection, jinja_parameters_dict):
    jenv = JinjaRepo(jinja_repo_source.root_dir)
    return _get_df_and_sql_from_jinja_template(jenv, inner_path, connection, jinja_parameters_dict)


def _get_df_and_sql_from_jinja(script_path, connection, jinja_parameters_dict):
    path = Path(script_path)
    jenv = JinjaLibrary(path.parent)
    return _get_df_and_sql_from_jinja_template(jenv, path.name, connection, jinja_parameters_dict)


def _get_df_and_sql_from_sql(script_path, format_parameters_list, connection):
    df = query.execute_sql_file(script_path, connection, format_parameters_list)
    sql = query.read_sql_file(script_path, format_parameters_list)
    return df, sql


def _maybe_get_frame_name(frame_name, script_path):
    return frame_name or Path(script_path).stem


def _get_config_from_master(inner_path, jinja_repo_source):
    _inner_path = Path(inner_path)
    with open(os.path.join(jinja_repo_source.root_dir, "master_config.json"), 'r') as f:
        master_config = json.load(f)
    return master_config[str(_inner_path.parent).replace("\\", "/")][str(_inner_path.name)]



class DataManager:
    """
    Queries, stores, and combines data from a library of SQL scripts and other data sources. This class serves as a
    workspace to additively build a data set. Data primarily added from modular SQL templates. This class can build
    subsequent queries from those templates. This class also tracks useful information about the data and its sources.

    An object of this class is always build from a a "Base Population" using a constructor prefixed with `from_`.
    Additional data can be added to the "Target Population" using join methods, which are all prefixed with `join_from_`.
    Additional data will always be added to the working "Target Population".
    Data joined from SQL will match the granularity of the current Target Population.

    TODO:
        Clarify interactions between on, left_on, and right_on, especially in cases where they are None.
        Add further details on how format_func_dict modifies the columns during joins.
        For SQL-related joins, explain how format_parameters_list interacts with SQL placeholders in more detail.

        mipi_setup.py
    """

    def __init__(self, frame: meta._Frame, setup: SetupDM):

        self.setup = setup.export_as_object()
        self._user_added_func_dict = self.setup.default_format_func_dict.copy() if self.setup.default_format_func_dict is not None else {}

        assert isinstance(frame, meta._Frame)
        self._frames = com.IndexedDict()

        # copy to target population, mutable, formatting done in meta.frame
        self._target_population = frame.df_query.copy()
        self._target_population = self.setup.default_format_func_dict.format_incoming_df(
            self._target_population)  # default_formatter_chain.format_incoming_df(self._target_population)
        frame._set_target(self._target_population)

        self._column_sources = dict()  # stores frame_index of columns. used to add frame number as join suffix for duped cols
        self._set_column_source_from_frame(frame, 0)

        if self.setup.store_base_df is False and self.setup.store_all_dfs is False:
            del frame.df_query
            del frame.df_target
        self._store_frame(frame, 0)

    @classmethod
    def from_jinja_repo(cls, inner_path: str,
                        jinja_parameters_dict: dict = None,
                        frame_name=None,
                        jinja_repo_source: JinjaRepo = None,
                        store_base_df: bool = False,
                        store_all_dfs: bool = False,
                        dialect: str = "mssql",
                        insert_table_type="full",
                        insert_table_name="MiPiTempTable",
                        default_format_func_dict: FormatDict | dict = None) -> Self:

        """
        Creates a MiPi DataManager from a Jinja script stored in a MiPi Repository.
        This is the most concise way to create a DataManager from frequently used scripts.
        All scripts in the repo are tied to the appropriate connection, frame name, and documentation.

        !!! info
            Please see the [JinjaRepo documentation][mipi_datamanager.core.jinja.JinjaRepo] for example usage and setup.

        Args:
            inner_path: Path from the root of the JinjaRepo to the jinja sql script.
            jinja_repo_source: Object that defines a repo. Points the repo directory and contains the Repo's connections.
            jinja_parameters_dict: Keyword parameters to pass into jinja tags.
            store_all_dfs: If `True`, each `DM.Frame` stores a full DataFrame for both the `df_query` and `df_target`.
                This is useful for troubleshooting as it provides detailed snapshots of each frame during creation,
                but this can be memory-intensive. Supersedes store_base_df.
            store_base_df: If `True`, the base frame only `DM.Frame[0]` stores a full DataFrame for both the `df_query` and `df_target`.
            default_format_func_dict: A dictionary where the keys are column names and the values are callable. Each
                Callable must take a series input and return the formatted series. The formatting is applied every time
                the respective column enters the DM see [Format Tools](/api/data_manager/#format-tools) for more information.
            dialect: SQL dialect being used in the database, this determines the temp table syntax.
                Currently only 'mysql' is available but more to come

        Returns
            DataManager: A datamanager object

        """
        _setup = SetupDM(SetupNullLoader(),
                          override_jinja_repo_source = jinja_repo_source,
                          override_store_all_dfs = store_all_dfs,
                          override_store_base_df = store_base_df,
                          override_default_format_func_dict = default_format_func_dict,
                          override_insert_table_type = insert_table_type,
                          override_insert_table_name = insert_table_name,
                          override_dialect = dialect
                         )
        _jinja_repo_source = _setup.export_as_object().jinja_repo_source #TODO make DRY
        config = _get_config_from_master(inner_path, _jinja_repo_source)

        if not config["meta"]["population"]:
            raise ConfigError(f'expected population status is True script got: {config["meta"]['population']}')

        con = _jinja_repo_source.conn_dict[config['meta']['connection']]
        df, sql = _get_df_and_sql_from_jinja_repo(_jinja_repo_source, inner_path, con, jinja_parameters_dict)

        _frame_name = frame_name or config["meta"]["name"]
        frame = meta._Frame(_frame_name, "JinjaRepo", df, sql=sql)

        return cls(frame, _setup)

    @classmethod
    def from_jinja_repo_preset(cls, inner_path: str,
                               jinja_parameters_dict: dict = None,
                               override_jinja_repo_source: JinjaRepo = None,
                               override_store_all_dfs: bool = None, override_store_base_df: bool = None,
                               override_dialect: str = None,
                               override_insert_table_type=None,
                               override_insert_table_name=None,
                               override_default_format_func_dict: FormatDict | dict = None,
                               extend_default_format_func_dict: FormatDict | dict = None,
                               setup_path:str=None) -> Self:

        """
        Behaves the same as [from_jinja_repo][mipi_datamanager.DataManager.from_jinja_repo] except that the optional
        arguments can be globally configured using a [mipi_setup.py file][mipi_datamanager.core.docs.setup].
        The settings of the `mipi_setup.py` file can be overwritten using optionals.

        Args:
            extend_default_format_func_dict: Add values to the dictionary in `mipi_setup.py` without overwriting
            setup_path: Specify a path to `mipi_setup.py`. This takes precedence over environment paths.

        Returns:

        See Also:
            - [from_jinja_repo][mipi_datamanager.DataManager.from_jinja_repo]
            - [mipi_setup.py file][mipi_datamanager.core.docs.setup]
        """
        _setup = SetupDM(SetupFileLoader(filepath = setup_path),
                          override_jinja_repo_source = override_jinja_repo_source,
                          override_store_all_dfs = override_store_all_dfs,
                          override_store_base_df = override_store_base_df,
                          override_default_format_func_dict = override_default_format_func_dict,
                          extend_default_format_func_dict = extend_default_format_func_dict,
                          override_insert_table_type = override_insert_table_type,
                          override_insert_table_name = override_insert_table_name,
                          override_dialect = override_dialect
                         )
        _jinja_repo_source = _setup.export_as_object().jinja_repo_source

        config = _get_config_from_master(inner_path, _jinja_repo_source)

        if not config["meta"]["population"]:
            raise ConfigError(f'expected population status is True script got: {config["meta"]['population']}')

        con = _jinja_repo_source.conn_dict[config['meta']['connection']]
        df, sql = _get_df_and_sql_from_jinja_repo(_jinja_repo_source, inner_path, con, jinja_parameters_dict)
        frame = meta._Frame(config["meta"]["name"], "JinjaRepo", df, sql=sql)

        return cls(frame, _setup)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, frame_name: str = None,
                       jinja_repo_source: JinjaRepo = None,
                       store_all_dfs: bool = False, store_base_df: bool = False,
                       dialect: str = "mssql",
                       insert_table_type="full",
                       insert_table_name="MiPiTempTable",
                       default_format_func_dict: FormatDict | dict = None) -> Self:
        """
        Creates a MiPi DataManager(DM) from a pandas dataframe.

        Args:
            df: Pandas dataframe to set as the base population
            frame_name: Name of the frame that is stored in the DM. If None, defaults to `unnamed-dataframe`
            jinja_repo_source: Object that defines a repo. Points the repo directory and contains the Repo's connections.
            store_all_dfs: If `True`, each `DM.Frame` stores a full DataFrame for both the `df_query` and `df_target`.
                This is useful for troubleshooting as it provides detailed snapshots of each frame during creation,
                but this can be memory-intensive. Supersedes store_base_df.
            store_base_df: If `True`, the base frame only `DM.Frame[0]` stores a full DataFrame for both the `df_query` and `df_target`.
            default_format_func_dict: A dictionary where the keys are column names and the values are callable. Each
                Callable must take a series input and return the formatted series. The formatting is applied every time
                the respective column enters the DM see [Format Tools](/api/data_manager/#format-tools) for more information.
            dialect: SQL dialect being used in the database, this determines the temp table syntax.
                Currently only 'mysql' is available but more to come

        Returns: DataManager: A datamanager object


        !!! example
            ```python
            from mipi_datamanager import DataManager
            import pandas as pd

            data = {
                'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'Age': [25, 30, 35, 40, 45],
                'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Boston'],
                'Salary': [80000, 90000, 100000, 110000, 120000]
            }

            # Creating a DataFrame
            df = pd.DataFrame(data)

            mipi = DataManager.from_dataframe(df)
            ```

        """
        _frame_name = frame_name or "unnamed-dataframe"

        _setup = SetupDM(SetupNullLoader(),
                          override_jinja_repo_source= jinja_repo_source,
                          override_store_all_dfs = store_all_dfs,
                          override_store_base_df = store_base_df,
                          override_default_format_func_dict = default_format_func_dict,
                          override_insert_table_type = insert_table_type,
                          override_insert_table_name = insert_table_name,
                          override_dialect = dialect
                         )

        frame = meta._Frame(_frame_name, "Data Frame", df, None, None)
        return cls(frame, _setup)

    @classmethod
    def from_dataframe_preset(cls, df: pd.DataFrame, frame_name: str = None,
                              override_jinja_repo_source: JinjaRepo = None,
                              override_store_all_dfs: bool = None, override_store_base_df: bool = None,
                              override_dialect: str = None,
                              override_insert_table_type=None,
                              override_insert_table_name=None,
                              override_default_format_func_dict: FormatDict | dict = None,
                              extend_default_format_func_dict: FormatDict | dict = None,
                              setup_path:str=None) -> Self:
        """
        Behaves the same as [from_dataframe][mipi_datamanager.DataManager.from_dataframe] except that the optional
        arguments can be globally configured using a [mipi_setup.py file][mipi_datamanager.core.docs.setup].
        The settings of the `mipi_setup.py` file can be overwritten using optionals.

        Args:
            extend_default_format_func_dict: Add values to the dictionary in `mipi_setup.py` without overwriting
            setup_path: Specify a path to `mipi_setup.py`. This takes precedence over environment paths.

        Returns:

        See Also:
            - [from_jinja_repo][mipi_datamanager.DataManager.from_jinja_repo]
            - [mipi_setup.py file](home/mipi_setup_py.md
        """
        _frame_name = frame_name or "unnamed-dataframe"

        _setup = SetupDM(SetupFileLoader(filepath = setup_path),
                         override_jinja_repo_source = override_jinja_repo_source,
                          override_store_all_dfs = override_store_all_dfs,
                          override_store_base_df = override_store_base_df,
                          override_default_format_func_dict = override_default_format_func_dict,
                          extend_default_format_func_dict = extend_default_format_func_dict,
                          override_insert_table_type = override_insert_table_type,
                          override_insert_table_name = override_insert_table_name,
                          override_dialect = override_dialect
                         )

        frame = meta._Frame(_frame_name, "Data Frame", df, None, None)
        return cls(frame, _setup)

    @classmethod
    def from_sql(cls, file_path: str, connection: connection.Odbc, format_parameters_list: list = None,
                 frame_name: str = None,
                 jinja_repo_source: JinjaRepo = None,
                 store_all_dfs: bool = False, store_base_df: bool = False,
                 dialect: str = "mssql",
                 insert_table_type="full",
                 insert_table_name="MiPiTempTable",
                 default_format_func_dict: FormatDict | dict = None, ) -> Self:

        """
        Creates a MiPi DataManager(DM) from the results of a SQL script. The SQL script can have '{}' placeholders which
        will be resolved using string formatting. The values of `format_parameters_list` will be passed into the
        placeholders in order.

        !!! info "Script Setup"
            The SQL script uses python string formatting syntax. You can place optional placeholders '{}' in your
            script to accept the parameters of 'format_parameters_list'.

        Args:
            file_path: The absolute or relative path to the SQL script.
            connection: MiPi Connection Object
            format_parameters_list: A list of values to be placed into string format placeholders "{}".
                Values will be entered into placeholders in the order of the list.
                This is equivalent to using python string formatting ie. `"{} {}".format(["hello","world"])`
            frame_name: Name that the frame is stored as in the DM.
                If `None` the frame name will default to the name of the SQL script file.
            jinja_repo_source: Object that defines a repo. Points the repo directory and contains the Repo's connections.
            store_all_dfs: If `True`, each `DM.Frame` stores a full DataFrame for both the `df_query` and `df_target`.
                This is useful for troubleshooting as it provides detailed snapshots of each frame during creation,
                but this can be memory-intensive. Supersedes store_base_df.
            store_base_df: If `True`, the base frame only `DM.Frame[0]` stores a full DataFrame for both the `df_query` and `df_target`.
            default_format_func_dict: A dictionary where the keys are column names and the values are callable. Each
                Callable must take a series input and return the formatted series. The formatting is applied every time
                the respective column enters the DM see [Format Tools](/api/data_manager/#format-tools) for more information.
            dialect: SQL dialect being used in the database, this determines the temp table syntax.
                Currently only 'mysql' is available but more to come

        !!! example
            Main Python Script
            ```python
            from mipi_datamanager import DataManager
            from mipi_datamanager.odbc import Odbc

            con = Odbc(dsn = "my_dsn")

            mipi = DataManager.from_sql("path/to/sql_script.sql",con,
                                          format_parameters_list = ["2023-01-01","2024-01-01"])
            ```
            <details>
            <summary>Click to expand the accompanying SQL example</summary>
            Script Template
            ```tsql
            SELECT PrimaryKey, Value
            LEFT Table1 tbl
            where tbl.date IS BETWEEN '{}' AND '{}'

            ```
            Resolved Query
            ```tsql
            SELECT PrimaryKey, Value
            LEFT Table1 tbl
            where tbl.date IS BETWEEN '2023-01-01' AND '2024-01-01'
            ```
            </details>

        Returns: DataManager: A datamanager object

        """

        _frame_name = _maybe_get_frame_name(frame_name, file_path)
        df, sql = _get_df_and_sql_from_sql(file_path, format_parameters_list, connection)

        built_from = "Format SQL" if format_parameters_list else "SQL"

        frame = meta._Frame(_frame_name, built_from, df, sql=sql)

        _setup = SetupDM(SetupNullLoader(),
                          override_jinja_repo_source = jinja_repo_source,
                          override_store_all_dfs = store_all_dfs,
                          override_store_base_df = store_base_df,
                          override_default_format_func_dict = default_format_func_dict,
                          override_insert_table_type = insert_table_type,
                          override_insert_table_name = insert_table_name,
                          override_dialect = dialect
                         )

        return cls(frame, _setup)

    @classmethod
    def from_sql_preset(cls, file_path: str, connection: connection.Odbc, format_parameters_list: list = None,
                        frame_name: str = None,
                        override_jinja_repo_source: JinjaRepo = None,
                        override_store_all_dfs: bool = None, override_store_base_df: bool = None,
                        override_dialect: str = None,
                        override_insert_table_type=None,
                        override_insert_table_name=None,
                        override_default_format_func_dict: FormatDict | dict = None,
                        extend_default_format_func_dict: FormatDict | dict = None,
                        setup_path:str=None) -> Self:

        """
        Behaves the same as [from_sql][mipi_datamanager.DataManager.from_sql] except that the optional
        arguments can be globally configured using a [mipi_setup.py file][mipi_datamanager.core.docs.setup].
        The settings of the `mipi_setup.py` file can be overwritten using optionals.

        Args:
            extend_default_format_func_dict: Add values to the dictionary in `mipi_setup.py` without overwriting
            setup_path: Specify a path to `mipi_setup.py`. This takes precedence over environment paths.

        Returns:

        See Also:
            - [from_jinja_repo][mipi_datamanager.DataManager.from_jinja_repo]
            - [mipi_setup.py file](home/mipi_setup_py.md
        """

        _frame_name = _maybe_get_frame_name(frame_name, file_path)
        df, sql = _get_df_and_sql_from_sql(file_path, format_parameters_list, connection)

        built_from = "Format SQL" if format_parameters_list else "SQL"

        frame = meta._Frame(_frame_name, built_from, df, sql=sql)

        _setup = SetupDM(SetupFileLoader(filepath = setup_path),
                         override_jinja_repo_source = override_jinja_repo_source,
                          override_store_all_dfs = override_store_all_dfs,
                          override_store_base_df = override_store_base_df,
                          override_default_format_func_dict = override_default_format_func_dict,
                          extend_default_format_func_dict = extend_default_format_func_dict,
                          override_insert_table_type = override_insert_table_type,
                          override_insert_table_name = override_insert_table_name,
                          override_dialect = override_dialect
                         )

        return cls(frame, _setup)

    @classmethod
    def from_jinja(cls, file_path: str, connection: connection.Odbc,
                   jinja_parameters_dict: dict = None,
                   frame_name: str = None,
                   jinja_repo_source: JinjaRepo = None,
                   store_all_dfs: bool = False, store_base_df: bool = False,
                   dialect: str = "mssql",
                   insert_table_type="full",
                   insert_table_name="MiPiTempTable",
                   default_format_func_dict: FormatDict | dict = None):
        """

        Creates a MiPi DataManager(DM) from a Jinja script Script. Jinja Scripts use named keyword tags {{ key }} and
        can include jinja logic. For details on Jinja syntax view the [official documentation](https://jinja.palletsprojects.com/en/3.1.x/).

        !!! info "Script Setup"
            The SQL script uses Jinja syntax, see [Jinja2 official documentation](https://jinja.palletsprojects.com/en/3.1.x/)
            You can place optional jinja tags '{{...}}' to accept the keyword pairs of 'jinja_parameters_dict'.

        Args:
            file_path: The absolute or relative path to the Jinja SQL script.
            connection: MiPi Connection Object
            jinja_parameters_dict: Keyword parameters to pass into jinja tags.
            frame_name: Name that the frame is stored as in the DM.
                If `None` the frame name will default to the name of the SQL script file.
            jinja_repo_source: Object that defines a repo. The repo stores each script and its meta data.
            store_all_dfs: If `True`, each `DM.Frame` stores a full DataFrame for both the `df_query` and `df_target`.
                This is useful for troubleshooting as it provides detailed snapshots of each frame during creation,
                but this can be memory-intensive. Supersedes store_base_df.
            store_base_df: If `True`, the base frame only `DM.Frame[0]` stores a full DataFrame for both the `df_query` and `df_target`.
            default_format_func_dict: A dictionary where the keys are column names and the values are callable. Each
                Callable must take a series input and return the formatted series. The formatting is applied every time
                the respective column enters the DM see [Format Tools](/api/data_manager/#format-tools) for more information.
            dialect: SQL dialect being used in the database, this determines the temp table syntax.
                Currently only 'mysql' is available but more to come

        !!! example

            Main Python Script:
            ```python
            from mipi_datamanager import DataManager
            from mipi_datamanager.odbc import Odbc

            con = Odbc(dsn = "my_dsn")

            jinja_parameters_dict = {"date_start":"2023-01-01",
                                     "date_end":"2024-01-01"}

            mipi = DataManager.from_jinja("path/to/sql_script.sql",con,
                                          jinja_parameters_dict = jinja_parameters_dict)
            ```

            <details>
            <summary>Click to expand the accompanying SQL example</summary>
            Jinja Script Template:
            ```tsql
            SELECT PrimaryKey, Value
            LEFT Table1 tbl
            where tbl.date IS BETWEEN '{{ date_start }}' AND '{{ date_end }}'

            ```

            Resolves to:
            ```tsql
            SELECT PrimaryKey, Value
            LEFT Table1 tbl
            where tbl.date IS BETWEEN '2023-01-01' AND '2024-01-01'
            ```
            </details>

        Returns: DataManager: A datamanager object

        """

        _frame_name = _maybe_get_frame_name(frame_name, file_path)

        df, sql = _get_df_and_sql_from_jinja(file_path, connection, jinja_parameters_dict)

        frame = meta._Frame(_frame_name, "Jinja", df, sql=sql)

        _setup = SetupDM(SetupNullLoader(),
                         override_jinja_repo_source = jinja_repo_source,
                          override_store_all_dfs = store_all_dfs,
                          override_store_base_df = store_base_df,
                          override_default_format_func_dict = default_format_func_dict,
                          override_insert_table_type = insert_table_type,
                          override_insert_table_name = insert_table_name,
                          override_dialect = dialect
                         )

        return cls(frame, _setup)

    @classmethod
    def from_jinja_preset(cls, file_path: str, connection: connection.Odbc,
                          jinja_parameters_dict: dict = None,
                          frame_name: str = None,
                          override_jinja_repo_source: JinjaRepo = None,
                          override_store_all_dfs: bool = None, override_store_base_df: bool = None,
                          override_dialect: str = None,
                          override_insert_table_type=None,
                          override_insert_table_name=None,
                          override_default_format_func_dict: FormatDict | dict = None,
                          extend_default_format_func_dict: FormatDict | dict = None,
                          setup_path:str=None):

        """
        Behaves the same as [from_jinja][mipi_datamanager.DataManager.from_jinja] except that the optional
        arguments can be globally configured using a [mipi_setup.py file][mipi_datamanager.core.docs.setup].
        The settings of the `mipi_setup.py` file can be overwritten using optionals.

        Args:
            extend_default_format_func_dict: Add values to the dictionary in `mipi_setup.py` without overwriting
            setup_path: Specify a path to `mipi_setup.py`. This takes precedence over environment paths.

        Returns:

        See Also:
            - [from_jinja_repo][mipi_datamanager.DataManager.from_jinja_repo]
            - [mipi_setup.py file](home/mipi_setup_py.md
        """

        _frame_name = _maybe_get_frame_name(frame_name, file_path)

        df, sql = _get_df_and_sql_from_jinja(file_path, connection, jinja_parameters_dict)

        frame = meta._Frame(_frame_name, "Jinja", df, sql=sql)

        _setup = SetupDM(SetupFileLoader(filepath = setup_path),
                         override_jinja_repo_source = override_jinja_repo_source,
                          override_store_all_dfs = override_store_all_dfs,
                          override_store_base_df = override_store_base_df,
                          override_default_format_func_dict = override_default_format_func_dict,
                          extend_default_format_func_dict = extend_default_format_func_dict,
                          override_insert_table_type = override_insert_table_type,
                          override_insert_table_name = override_insert_table_name,
                          override_dialect = override_dialect
                         )

        return cls(frame, _setup)

    @classmethod
    def from_excel(cls, file_path: str, excel_sheet: str | int | None = None,
                   frame_name: str = None,
                   jinja_repo_source: JinjaRepo = None,
                   store_all_dfs: bool = False, store_base_df: bool = False,
                   dialect: str = "mssql",
                   insert_table_type="full",
                   insert_table_name="MiPiTempTable",
                   default_format_func_dict: FormatDict | dict = None) -> Self:
        """

        Creates a MiPi DataManager(DM) from a microsoft Excel file.

        Args:
            file_path: Absolute or relative path to the Microsoft Excel file.
            frame_name: Name that the frame is stored as in the DM.
                If `None` the frame name will default to the name of the Excel file.
            jinja_repo_source: Object that defines a repo. Points the repo directory and contains the Repo's connections.
            store_all_dfs: If `True`, each `DM.Frame` stores a full DataFrame for both the `df_query` and `df_target`.
                This is useful for troubleshooting as it provides detailed snapshots of each frame during creation,
                but this can be memory-intensive. Supersedes store_base_df.
            store_base_df: If `True`, the base frame only `DM.Frame[0]` stores a full DataFrame for both the `df_query` and `df_target`.
            default_format_func_dict: A dictionary where the keys are column names and the values are callable. Each
                Callable must take a series input and return the formatted series. The formatting is applied every time
                the respective column enters the DM see [Format Tools](/api/data_manager/#format-tools) for more information.
            excel_sheet: sheet name(str) or sheet index(int)
            dialect: SQL dialect being used in the database, this determines the temp table syntax.
                Currently only 'mysql' is available but more to come
        !!! example
            Main Python Script
            ```python
            from mipi_datamanager import DataManager

            mipi = DataManager.from_excel("path/to/excel_file.xlsx")
            ```

        Returns: DataManager: A datamanager object

        """
        _frame_name = _maybe_get_frame_name(frame_name, file_path)
        df = pd.read_excel(file_path, sheet_name=excel_sheet or 0)
        frame = meta._Frame(_frame_name, "Excel", df)

        _setup = SetupDM(SetupNullLoader(),
                         override_jinja_repo_source = jinja_repo_source,
                          override_store_all_dfs = store_all_dfs,
                          override_store_base_df = store_base_df,
                          override_default_format_func_dict = default_format_func_dict,
                          override_insert_table_type = insert_table_type,
                          override_insert_table_name = insert_table_name,
                          override_dialect = dialect
                         )

        return cls(frame, _setup)

    @classmethod
    def from_excel_preset(cls, file_path: str, excel_sheet: str | int | None = None, frame_name: str = None,
                          override_jinja_repo_source: JinjaRepo = None,
                          override_store_all_dfs: bool = None, override_store_base_df: bool = None,
                          override_dialect: str = None,
                          override_insert_table_type=None,
                          override_insert_table_name=None,
                          override_default_format_func_dict: FormatDict | dict = None,
                          extend_default_format_func_dict: FormatDict | dict = None,
                          setup_path:str=None) -> Self:
        """
        Behaves the same as [from_excel][mipi_datamanager.DataManager.from_excel] except that the optional
        arguments can be globally configured using a [mipi_setup.py file][mipi_datamanager.core.docs.setup].
        The settings of the `mipi_setup.py` file can be overwritten using optionals.

        Args:
            extend_default_format_func_dict: Add values to the dictionary in `mipi_setup.py` without overwriting
            setup_path: Specify a path to `mipi_setup.py`. This takes precedence over environment paths.

        Returns:

        See Also:
            - [from_jinja_repo][mipi_datamanager.DataManager.from_jinja_repo]
            - [mipi_setup.py file](home/mipi_setup_py.md
        """
        _frame_name = _maybe_get_frame_name(frame_name, file_path)
        df = pd.read_excel(file_path, sheet_name=excel_sheet or 0)
        frame = meta._Frame(_frame_name, "Excel", df)

        _setup = SetupDM(SetupFileLoader(filepath = setup_path),
                         override_jinja_repo_source = override_jinja_repo_source,
                          override_store_all_dfs = override_store_all_dfs,
                          override_store_base_df = override_store_base_df,
                          override_default_format_func_dict = override_default_format_func_dict,
                          extend_default_format_func_dict = extend_default_format_func_dict,
                          override_insert_table_type = override_insert_table_type,
                          override_insert_table_name = override_insert_table_name,
                          override_dialect = override_dialect
                         )

        return cls(frame, _setup)

    def _store_frame(self, frame: meta._Frame, idx) -> None:
        """ to store a frame including its index"""
        alias = f"{frame.name}_{idx}"
        self._frames[alias] = frame

    ##############################################################################################
    # Target Data Joins
    ##############################################################################################

    def join_from_jinja_repo(self, inner_path: str, how: JoinLiterals = "left", frame_name=None,
                             jinja_parameters_dict: dict = None,
                             format_func_dict: FormatDict | dict = None, left_on: str | tuple = None,
                             left_index: bool = False):

        """
        This function joins the result of a jinja repo script to a DataManager object. Note that the `connection` and
        `right_on` have already been predefined by the repo's config.

        !!! warning
            This function is only available in if you defined a `JinjaRepo` while instantiating the DataManager object.

        !!! info "Script Setup"
            Please see the [JinjaRepo documentation][mipi_datamanager.core.jinja.JinjaRepo] for example usage and setup.


        Args:
            inner_path: Path from the root of the JinjaRepo to the jinja sql script.
            how: {'left', 'right', 'inner', 'outer', 'cross'} Type of join to perform
            jinja_parameters_dict: Keyword parameters to pass into jinja tags.
            format_func_dict: A dictionary where the keys are column names and the values are callable
                that format the series when that column enters the DM. see [Format Tools](/api/data_manager/#format-tools) for more information.
                Only applies to this frame.
            left_on: Column(s) within the target population dataframe to join on. If a tuple is passed both keys will be used for the merge
            left_index: Use the target population index as the join key.

        Returns:

        """

        if jinja_parameters_dict is None:
            _jinja_parameters_dict = {}
        else:
            _jinja_parameters_dict = jinja_parameters_dict

        config = _get_config_from_master(inner_path, self.setup.jinja_repo_source)  # TODO replace with JinjaRepo.pull

        if config["meta"]["population"]:
            raise ConfigError(f'expected population status is False script got: {config["meta"]['population']}')

        right_on = config["meta"]["join_key"]

        if left_on:
            if isinstance(left_on, str):
                rename_dict = {left_on: right_on}
            else:
                rename_dict = {k: v for k, v in zip(left_on, right_on)}
        else:
            rename_dict = None

        con = self.setup.jinja_repo_source.conn_dict[config['meta']['connection']]

        sql = self.resolve_dimension_jinja_repo_template(inner_path, right_on, jinja_parameters_dict,
                                                         rename_columns_dict=rename_dict)
        df = query.execute_sql_string(sql, con)

        _frame_name = frame_name or config["meta"]["name"]
        frame = meta._Frame(_frame_name, "JinjaRepo", df, sql=sql)

        self._join_from_frame(frame, right_on, how, format_func_dict, None, None, False,
                              False)

    def join_from_dataframe(self, df: pd.DataFrame, on: str | tuple = None, how: JoinLiterals = "left",
                            frame_name: str = None,
                            format_func_dict: FormatDict | dict = None,
                            left_on: str | tuple = None, right_on: str | tuple = None,
                            left_index: bool = False, right_index: bool = False):
        """

        Joins a dataframe into the DataManager's (DM) target population.

        !!! warning
            Note that unlike the sql methods, the dataframe might have different granularity/records than the target populatoin.
            Take care when choosing join types. Inner joins are particular useful for filtering.

        Args:
            df: Dataframe to join.
            on: Column to join on. Must exist in both the target data frame and incoming dataframe.
                If a tuple is passed both keys will be used for the merge
            how: {'left', 'right', 'inner', 'outer', 'cross'} Type of join to perform
            frame_name: Name that the frame is stored as in the DM.
                If `None` the frame name will default to `unnamed-dataframe`.
            format_func_dict: A dictionary where the keys are column names and the values are callable
                that format the series when that column enters the DM. see [Format Tools](/api/data_manager/#format-tools) for more information.
                Only applies to this frame.
            left_on: Column(s) name within the target population to join on. If a tuple is passed both keys will be used for the merge
            right_on: Column(s) name within the result of the query to join on.If a tuple is passed both keys will be used for the merge
            left_index: Use Target population index as join key
            right_index: Use Result of the query's index to join on.

        !!! example
            Main Python Script
            ```
            #Set the base population
            data = {
                'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'Age': [25, 30, 35, 40, 45],
                'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Boston'],
                'Salary': [80000, 90000, 100000, 110000, 120000]
            }
            df = pd.DataFrame(data)
            mipi = DataManager.from_dataframe(df)


            #Left Join in another column
            data_job = {
                'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'Job': ['Actor', 'Teacher', 'Mechanic', 'lawyer', 'Engineer']
            }
            df_job = pd.DataFrame(data)
            mipi.join_from_dataframe(df_job,on = "Name",how = "left")

            #Filter using inner join
            data_include = {
                'Name': [ 'Bob', 'Charlie'],
            }
            df_include = pd.DataFrame(data)
            mipi.join_from_dataframe(df_include,on = "Name",how = "inner")
            ```
            <details>
            <summary>Click to expand the accompanying output example</summary>
            This would result in the following dataframe

            | Name    | Age | City        | Salary | Job      |
            |---------|-----|-------------|--------|----------|
            | Bob     | 30  | Los Angeles | 90000  | Teacher  |
            | Charlie | 35  | Mechanic    | 100000 | Mechanic |
            </details>

        Returns:

        """

        _frame_name = frame_name or "unnamed-dataframe"
        frame = meta._Frame(_frame_name, "Data Frame", df.copy(), None, None)
        self._join_from_frame(frame, on, how, format_func_dict, left_on, right_on, left_index,
                              right_index)

    def join_from_excel(self, file_path: str, on: str = None, how: JoinLiterals = "left",
                        excel_sheet: str | int = None, frame_name: str = None,
                        format_func_dict: FormatDict | dict = None,
                        left_on: str | tuple = None, right_on: str | tuple = None,
                        left_index: bool = False, right_index: bool = False):
        """

        A method of the DataManager (DM) that reads an excel file and joins it to the target population.
        !!! warning
            Note that unlike the sql methods, the dataframe might have different granularity/records than the target populatoin.
            Take care when choosing join types. Inner joins are particular useful for filtering.

        Args:
            file_path: Absolute or relative path to the Microsoft Excel file.
            on: Column to join on. Must exist in both the target data frame and result of the Jinja SQL script.
                If a tuple is passed both keys will be used for the merge
            how: {'left', 'right', 'inner', 'outer', 'cross'} Type of join to perform
            frame_name: Name that the frame is stored as in the DM.
                If `None` the frame name will default to the name of the SQL script file.
            excel_sheet: sheet name(str) or sheet index(int)
            format_func_dict: A dictionary where the keys are column names and the values are callable
                that format the series when that column enters the DM. see [Format Tools](/api/data_manager/#format-tools) for more information.
                Only applies to this frame.
            left_on: Column(s) name within the target population to join on. If a tuple is passed both keys will be used for the merge
            right_on: Column(s) name within the result of the query to join on. If a tuple is passed both keys will be used for the merge
            left_index: Use Target population index as join key
            right_index: Use Result of the query's index to join on.

    !!! example
        Main Python Script
        ```python
        from mipi_datamanager import DataManager

        mipi = DataManager.from_excel("path/to/excel_file.xlsx")
        #user left join to add columns
        mipi.join_from_dataframe("path/to/excel_file2.xlsx", on = "JoinColumn", how= "left")
        #use inner join to filter
        mipi.join_from_dataframe("path/to/excel_file3.xlsx", on = "JoinColumn", how= "inner")
        ```

        Returns:

        """
        _frame_name = _maybe_get_frame_name(frame_name, file_path)
        df = pd.read_excel(file_path, sheet_name=excel_sheet or 0)
        frame = meta._Frame(_frame_name, "Excel", df, None, None)
        self._join_from_frame(frame, on, how, format_func_dict, left_on, right_on, left_index,
                              right_index)

    def join_from_format_sql(self, file_path: str, connection: connection.Odbc, on: str | tuple = None,
                             how: JoinLiterals = "left",
                             format_parameters_list: list = None,
                             frame_name: str = None, format_func_dict: FormatDict | dict = None,
                             left_on: str | tuple = None, right_on: str | tuple = None,
                             left_index: bool = False, right_index: bool = False):
        """

        Inserts the records contained in the target population into a format SQL script template, this creates a script
        whose records match the target population. Then runs the script and Joins the results into the DataManager's target population.

        !!! info "Script Setup"
            This script must be setup to accept a temp table from the data manager. The SQL script uses python string formatting syntax.
            You can place optional placeholders '{}' in your script to accept the parameters of 'format_parameters_list'.
            This script assumes that the first placeholder '{}' is where the temp table will be inserted. The following
            placeholders will be used for format parameters.

        Args:
            file_path: The absolute or relative path to the SQL script.
            connection: MiPi Connection Object
            on: Column to join on. Must exist in both the target data frame and result of the SQL script.
                If a tuple is passed both keys will be used for the merge
            how: {'left', 'right', 'inner', 'outer', 'cross'} Type of join to perform
            format_parameters_list: A list of values to be placed into string format placeholders "{}".
                Values will be entered into placeholders in the order of the list.
                This is equivalent to using python string formatting ie. `"{} {}".format(["hello","world"])`
            frame_name: Name that the frame is stored as in the DM.
                If `None` the frame name will default to the name of the SQL script file.
            format_func_dict: A dictionary where the keys are column names and the values are callable
                that format the series when that column enters the DM. see [Format Tools](/api/data_manager/#format-tools) for more information.
                Only applies to this frame.
            left_on: Column(s) name within the target population to join on. If a tuple is passed both keys will be used for the merge
            right_on: Column(s) name within the result of the query to join on. If a tuple is passed both keys will be used for the merge
            left_index: Use Target population index as join key
            right_index: Use Result of the query's index to join on.

        !!! example
            Main Python Script
            ```python
            from mipi_datamanager import DataManager
            from mipi_datamanager.odbc import Odbc

            con = Odbc(dsn = "my_dsn")

            mipi = DataManager.from_jinja("path/to/sql_script.sql",con)

            jinja_parameters_dict = {
              "param1":"val1",
              "param2":"val2"
            }

            mipi.join_from_jinja("path/to/sql_script.sql",con,
                                 jinja_parameters_dict=jinja_parameters_dict)
            ```
            <details>
            <summary>Click to expand a SQL Example</summary>
            SQL Template
            ```tsql
            {}

            SELECT tmp.PrimaryKey,Value2
            FROM #MiPiTempTable as tmp
            LEFT JOIN foreign_table ft
                ON tmp.PrimaryKey = ft.Value2;
            WHERE param1 = {}
            AND   param2 = {}

            ```

            Resolved Query
            ```tsql
            CREATE TEMPORARY TABLE #MiPiTempTable (PrimaryKey);
            INSERT INTO #MiPiTempTable Values (1)
            INSERT INTO #MiPiTempTable Values (2)
            INSERT INTO #MiPiTempTable Values (3)

            SELECT tmp.PrimaryKey,Value2
            FROM #MiPiTempTable as tmp
            LEFT JOIN foreign_table ft
                ON tmp.PrimaryKey = ft.Value2;
            WHERE param1 = param_val1
            AND   param2 = param_val2
            ```
            </details>
        """

        _frame_name = _maybe_get_frame_name(frame_name, file_path)

        _on, _rename_dict = self._get_join_sides(on, left_on, right_on, left_index, right_index)

        sql = self.resolve_dimension_format_sql_file(file_path, _on, format_parameters_list,
                                                     rename_columns_dict=_rename_dict)
        df = query.execute_sql_string(sql, connection)

        frame = meta._Frame(_frame_name, "Format SQL", df, sql=sql)
        self._join_from_frame(frame, on, how, format_func_dict, left_on, right_on, left_index,
                              right_index)

    def join_from_jinja(self, file_path: str, connection: connection.Odbc, on: str | tuple = None,
                        how: JoinLiterals = "left",
                        jinja_parameters_dict: dict = None,
                        frame_name: str = None, format_func_dict: dict = None,
                        left_on: str | tuple = None, right_on: str | tuple = None,
                        left_index: bool = False, right_index: bool = False):

        """

        Inserts the records contained in the target population into a Jinja SQL script template, this creates a script
        whose records match the target population. Then runs the script and Joins the results into the DataManager's target population.

        !!! info "Script Setup"
            This script must be setup to accept a temp table from the data manager. The SQL script uses Jinja syntax, see [Jinja2 official documentation](https://jinja.palletsprojects.com/en/3.1.x/)
            You can place optional jinja tags '{{...}}' to accept the keyword pairs of 'jinja_parameters_dict'.
            This script is expected to have a tag for the temp table "{{MiPiTempTable}}"

        Args:
            file_path: The absolute or relative path to the Jinja SQL script.
            connection: MiPi Connection Object
            on: Column to join on. Must exist in both the target data frame and result of the Jinja SQL script.
                If a tuple is passed both keys will be used for the merge
            how: {'left', 'right', 'inner', 'outer', 'cross'} Type of join to perform
            jinja_parameters_dict: Keyword parameters to pass into jinja tags.
            frame_name: Name that the frame is stored as in the DM.
                If `None` the frame name will default to the name of the SQL script file.
            format_func_dict: A dictionary where the keys are column names and the values are callable
                that format the series when that column enters the DM. see [Format Tools](/api/data_manager/#format-tools) for more information.
                Only applies to this frame.
            left_on: Column name within the target population to join on.
            right_on: Column name within the result of the query to join on.
            left_index: Use Target population index as join key
            right_index: Use Result of the query's index to join on.

        !!! example
            Main Python Script
            ```python
            from mipi_datamanager import DataManager
            from mipi_datamanager.odbc import Odbc

            con = Odbc(dsn = "my_dsn")

            mipi = DataManager.from_jinja("path/to/sql_script.sql",con)

            jinja_parameters_dict = {
              "param1":"val1",
              "param2":"val2"
            }

            mipi.join_from_jinja("path/to/sql_script.sql",con,
                                 jinja_parameters_dict=jinja_parameters_dict)
            ```
            <details>
            <summary>Click to expand a detailed Example</summary>
            Jinja SQL Template
            ```tsql
            {{MiPiTempTable}}

            SELECT tmp.PrimaryKey,Value2
            FROM #MiPiTempTable as tmp
            LEFT JOIN foreign_table ft
                ON tmp.PrimaryKey = ft.Value2;
            WHERE param1 = {{ param1 }}
            AND   param2 = {{ param2 }}
            ```

            Resolved Query
            ```tsql
            CREATE TEMPORARY TABLE #MiPiTempTable (PrimaryKey);
            INSERT INTO #MiPiTempTable Values (1)
            INSERT INTO #MiPiTempTable Values (2)
            INSERT INTO #MiPiTempTable Values (3)

            SELECT tmp.PrimaryKey,Value2
            FROM #MiPiTempTable as tmp
            LEFT JOIN foreign_table ft
                ON tmp.PrimaryKey = ft.Value2;
            WHERE param1 = param_val1
            AND   param2 = param_val2
            ```
            </details>

        """

        _frame_name = _maybe_get_frame_name(frame_name, file_path)

        _on, _rename_dict = self._get_join_sides(on, left_on, right_on, left_index, right_index)

        sql = self.resolve_dimension_jinja_file(file_path, _on, jinja_parameters_dict=jinja_parameters_dict,
                                                rename_columns_dict=_rename_dict)
        df = query.execute_sql_string(sql, connection)

        frame = meta._Frame(_frame_name, "Jinja", df, sql=sql)
        self._join_from_frame(frame, on, how, format_func_dict, left_on, right_on, left_index,
                              right_index)

    def _get_join_sides(self, on, left_on, right_on, left_index, right_index):
        if on:
            _on = on
            _rename_dict = None
        elif left_on:
            _on = right_on
            if isinstance(left_on, str):
                _rename_dict = {left_on: right_on}
            else:
                _rename_dict = {k: v for k, v in zip(left_on, right_on)}
        # elif left_index: #TODO add index
        #     _on =
        #     if isinstance(left_on, str):
        #         rename_dict = {left_on: right_on}
        #     else:
        #         rename_dict = {k: v for k, v in zip(left_on, right_on)}
        else:
            raise MergeError("Must define either 'on' or 'left/right")

        return _on, _rename_dict

    def _join_from_frame(self, frame: meta._Frame, on: str, how: JoinLiterals,
                         format_func_dict, left_on, right_on, left_index, right_index):
        """Joins a frame into target population. used by used join functions"""

        if format_func_dict is None:
            format_func_dict = {}

        if format_func_dict:
            frame.df_query = self.setup.default_format_func_dict.format_incoming_df(frame.df_query,
                                                                                    override_formatter=format_func_dict)
        else:
            frame.df_query = self.setup.default_format_func_dict.format_incoming_df(frame.df_query)

        self._target_population = self._target_population.merge(frame.df_query, how=how, on=on, left_on=left_on,
                                                                right_on=right_on, left_index=left_index,
                                                                right_index=right_index)
        frame_idx = len(self._frames)
        frame._set_target(self._target_population)
        self._set_column_source_from_frame(frame, frame_idx)

        if not self.setup.store_all_dfs:
            del frame.df_query
            del frame.df_target

        self._store_frame(frame, frame_idx)

    def _set_column_source_from_frame(self, frame, idx) -> None:
        """
        appends the source column dictionary
        self.source_columns[column_name] = frame_index
        also renames duplicated columns x,y -> '~frame'
        rename also changes the source column dictionary, however it keeps the original value which contains no suffix\
        this identifies any future use of that column as a dupe.
        """

        # loop current frames query
        for column in frame.query_columns:

            # add new column to source dict
            if column not in self._column_sources:
                # no dupe -> assign to source columnm
                self._column_sources[column] = idx

            # for duplicate columns: add to source list and rename suffixes
            if ((f"{column}_x" in self._target_population.columns)
                    and (f"{column}_y" in self._target_population.columns)):
                warnings.warn(
                    f"\nColumn {column} was duplicated during a join.\nThe duplicated column suffixes were renamed in accordance with their origin frame.\ncoalesce duplicate columns with mipi.",
                    stacklevel=2)

                # col origonal source
                old_idx = self._column_sources[column]

                # assign rename vals for join suffixes x,y -> '~frame'
                x_old_target_column_name = f"{column}_x"
                y_old_target_column_name = f"{column}_y"
                x_new_target_column_name = f"{column}~{self._frames[old_idx].name}_{old_idx}"
                y_new_target_column_name = f"{column}~{frame.name}_{idx}"

                # rename target
                self._target_population = self._target_population.rename(
                    columns={x_old_target_column_name: x_new_target_column_name,
                             y_old_target_column_name: y_new_target_column_name})

                # rename source dict to deal with future dupes
                self._column_sources[x_new_target_column_name] = old_idx
                self._column_sources[y_new_target_column_name] = idx

            # third+ dupe will already exist in column key and will be added to the target without a suffix, needs rename
            if (column in self._column_sources
                    and any(f"{column}~{frame.name}" in col for col in self._column_sources)
                    and column in self._target_population.columns):
                self._column_sources[f"{column}~{frame.name}_{idx}"] = idx
                self._target_population = self._target_population.rename(
                    columns={column: f"{column}~{frame.name}_{idx}"})

    ##############################################################################################
    # Target Data Transformations
    ##############################################################################################

    def set_jinja_repo_source(self, jinja_repo_source: JinjaRepo) -> None:

        """
        Defines the jinja repo for this object. This allows queries from the repo. The repo can not be overwritten,
        you need to create a new object instead.

        Args:
            jinja_repo_source: Object that defines a repo. Points the repo directory and contains the Repo's connections.



        Returns:

        """

        if self.setup.jinja_repo_source:
            raise AttributeError(
                f"Mipi object {repr(self)} has already been set. Create a new mipi object, or clone this one to set a different sql repo source")
        else:
            self.setup.jinja_repo_source = jinja_repo_source

    def filter(self, mask: Mask):
        """Filters the target population using a boolean mask.
        A mask is a pandas series which contain boolean values.
        The a true value represents an index which will be included in the final dataframe.

        !!! example
            ```
            >>>from mipi_datamanager import DataManager
            >>>df = pd.DataFrame({
                'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'Age': [25, 30, 35, 40, 45],
                'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Boston'],
                'Salary': [80000, 90000, 100000, 110000, 120000]
                })
            >>>mipi = DataManager.from_dataframe(df)
            >>>mask = mipi.trgt["Age"] <= 30
            >>>mask
            pd.series(True,True,False,False,False)

            >>>mipi.filter(mask)
            >>>mipi.target_population

            | Name    | Age | City        | Salary | Job      |
            |---------|-----|-------------|--------|----------|
            | Bob     | 30  | Los Angeles | 90000  | Teacher  |
            | Charlie | 35  | Mechanic    | 100000 | Mechanic |

            ```
        """
        self._target_population = self._target_population[mask]

    def clone(self, base_name: str = None,
              change_jinja_repo_source: JinjaRepo = None,
              change_store_all_dfs: bool | None = None, change_store_base_df: bool | None = None,
              add_to_default_format_func_dict: dict = None,
              change_insert_table_type: str | None = None,
              change_dialect: str | None = None,
              change_insert_table_name: str | None = None,
              rename_columns_dict: dict = None) -> Self:
        """
        Creates a new DataManager object from the target population of the current object. The new object will
        contain a single frame representing the previous target population. The object will maintain the original's
        attributes unless they are explicitly changed.

        Args:
            base_name: Name of the base frame. Default "Clone from repr{self}"
            change_jinja_repo_source:
            change_store_all_dfs:
            change_store_base_df:
            add_to_default_format_func_dict: Add new values to the default format func dict but keep the old ones
            change_insert_table_type:
            change_dialect:
            change_insert_table_name:
            rename_columns_dict: Rename columns within the new data. Renaming will be done BEFORE formatting is applied.

        Returns: A new DataManager object.

        """

        df = self.trgt.copy()

        _jinja_repo_source = change_jinja_repo_source or self.setup.jinja_repo_source
        _store_all_dfs = change_store_all_dfs or self.setup.store_all_dfs
        _store_base_df = change_store_base_df or self.setup.store_base_df
        _insert_table_type = change_insert_table_type or self.setup.insert_table_type
        _insert_table_name = change_insert_table_name or self.setup.insert_table_name
        _dialect = change_dialect or self.setup.dialect

        # rename columns to declare new PKs
        if rename_columns_dict is not None:
            df = df.rename(columns=rename_columns_dict)

        base_name = base_name or f"Clone from: {repr(self)}"  # TODO update REPR to be descriptive without refrencing memory address, it breaks code when users try to hard code to this frame

        assert isinstance(add_to_default_format_func_dict, (dict, type(None))), "Format Dict must be type dict"
        if add_to_default_format_func_dict is not None:
            if self._user_added_func_dict is not None:
                new_format_dict = self._user_added_func_dict
            else:
                new_format_dict = dict()
            for k, v in add_to_default_format_func_dict.items():
                new_format_dict.update({k: v})
        else:
            new_format_dict = self._user_added_func_dict

        frame = meta._Frame(base_name, "Clone", df, None, None)

        cls = self.__class__

        _setup = SetupDM(SetupNullLoader(),
                         override_jinja_repo_source=_jinja_repo_source,
                         override_store_all_dfs=_store_all_dfs,override_store_base_df=_store_base_df,
                         override_default_format_func_dict=new_format_dict,
                         override_insert_table_name=_insert_table_name,
                         override_insert_table_type=_insert_table_type,
                         override_dialect=_dialect
                         )

        mipi2 = cls(frame, _setup)

        return mipi2

    def generate_inserts(self, key: str|list[str], frame: str | int = None,
                         rename_columns_dict: dict | None = None) -> str:  # TODO add override to insert type
        """
        Generate inserts from the mipi object. Inserts will be generated in accordance with the object's
        `insert_table_type`.

        Args:
            key: Column(s) to use to generate the inserts
            frame: Frame to use to generate inserts. If none, the target population will be used.
            rename_columns_dict: Dictionary to rename columns in the insert output only.

        Returns:

        """
        if self.setup.insert_table_type == "full":
            return self._get_temp_table_full(key, frame=frame, rename_columns_dict=rename_columns_dict)
        elif self.setup.insert_table_type == "records2":
            return self._get_temp_table_records2(key, frame=frame, rename_columns_dict=rename_columns_dict)
        else:
            raise ValueError("invalid insert table type")

    def _get_temp_table_full(self, key: str | list | tuple, frame=None, rename_columns_dict: dict | None = None):
        """Get the most current list of inserts where 'on' is the insert key"""

        df = frame.df_query if frame is not None else self.trgt
        if rename_columns_dict:
            df = df.rename(columns=rename_columns_dict)
            _key = _maybe_rename_values(key, rename_columns_dict)
        else:
            _key = key
        if self.setup.dialect == 'mssql':
            if isinstance(key, str):
                return generate_inserts.generate_insert_table(df[[_key]])
            elif isinstance(key, (tuple, list)):
                key = com._maybe_convert_tuple_to_list(key)
                return generate_inserts.generate_insert_table(df[_key])

    def _get_temp_table_records2(self, key, frame=None, rename_columns_dict: dict | None = None):
        """Get the most current list of inserts where 'on' is the insert key"""

        df = frame.df_query if frame is not None else self.trgt
        frame_name = frame.name if frame is not None else "Target Dataframe"

        if rename_columns_dict:
            df = df.rename(columns=rename_columns_dict)
            _key = _maybe_rename_values(key, rename_columns_dict)
        else:
            _key = key

        def handle_insert_errors(_key, frame_name):
            if _key not in df.columns:
                raise KeyError(f"({_key}) does not exist in frame: {frame_name})")
            # if key not in self.join_keys_available and self.default_join_format_function is None:
            #     raise KeyError(f"({key}) You must either define this column in the format dictonary, or define a default_join_format_function)")

        if isinstance(_key, str):
            handle_insert_errors(_key, frame_name)
            return generate_inserts.generate_insert_records2(df[[_key]])


        elif isinstance(_key, (tuple, list)):
            for k in _key:
                handle_insert_errors(k, frame_name)
            return generate_inserts.generate_insert_records2(df[list(_key)])

    def resolve_dimension_format_sql_string(self, sql: str, key: str, format_parameters_list:list=None, frame:str|int=None,
                                            rename_columns_dict: dict | None = None) -> str:
        """
        Resolves a dimension script from a format SQL string

        Args:
            sql: SQL string template
            key: Column(s) within dataframe to insert into the template.
            format_parameters_list: A list of values to be placed into string format placeholders "{}".
                Values will be entered into placeholders in the order of the list.
                This is equivalent to using python string formatting ie. `"{} {}".format(["hello","world"])`
            frame: Frame of mipi to use for the inserts. If `None` target_population will be used.
            rename_columns_dict: Rename columns before they are inserted into the template.


        Returns:
            Rendered SQL script.

        """
        inserts = self.generate_inserts(key, frame=frame, rename_columns_dict=rename_columns_dict)
        if format_parameters_list:
            _format_parameters_list = [inserts] + format_parameters_list
        else:
            _format_parameters_list = [inserts]

        sql = sql.format(*_format_parameters_list)
        return sql

    def resolve_dimension_format_sql_file(self, file_path: str, key: str, format_parameters_list:list=None, frame:str|int=None,
                                          rename_columns_dict: dict | None = None) -> str:
        """
        Resolves a dimension script from a format SQL file.

        Args:
            file_path: Path to SQL script
            key: Column(s) within dataframe to insert into the template.
            format_parameters_list: A list of values to be placed into string format placeholders "{}".
                Values will be entered into placeholders in the order of the list.
                This is equivalent to using python string formatting ie. `"{} {}".format(["hello","world"])`
            frame: Frame of mipi to use for the inserts. If `None` target_population will be used.
            rename_columns_dict: Rename columns before they are inserted into the template.

        Returns:
            Rendered SQL script.

        """
        sql = read_text_file(file_path)
        return self.resolve_dimension_format_sql_string(sql, key, format_parameters_list, frame=frame,
                                                        rename_columns_dict=rename_columns_dict)

    def _get_sql_from_jinja_template(self, jenv, script_path, jinja_parameters_dict):
        sql = jenv.resolve_file(script_path, jinja_parameters_dict)
        del jenv
        return sql

    def _maybe_get_jinja_insert_dict(self, key, jinja_parameters_dict=None, frame=None, rename_columns_dict=None):

        if self.setup.insert_table_type == "records2":
            _insert_table_name = key
        elif self.setup.insert_table_type == "full":
            _insert_table_name = "MiPiTempTable"
        else:
            raise ValueError(f"Invalid 'insert_table_type`: {self.setup.insert_table_type} can not generate inserts.")

        if jinja_parameters_dict:
            jinja_parameters_dict[_insert_table_name] = self.generate_inserts(key, frame=frame,
                                                                              rename_columns_dict=rename_columns_dict)
        else:
            jinja_parameters_dict = {
                _insert_table_name: self.generate_inserts(key, frame=frame, rename_columns_dict=rename_columns_dict)}
        return jinja_parameters_dict

    def resolve_dimension_jinja_repo_template(self, inner_path: str, key: str | list | tuple,
                                              jinja_parameters_dict: dict, frame: str | int = None,
                                              rename_columns_dict: dict | None = None) -> str:
        """
        Resolves a dimension script from a jinja repository.

        Args:
            inner_path: Path from the root of the jinja repo to the script template.
            key: Column(s) within dataframe to insert into the template.
            jinja_parameters_dict: Keyword parameters to pass into jinja tags.
            frame: Frame of mipi to use for the inserts. If `None` target_population will be used.
            rename_columns_dict: Rename columns before they are inserted into the template.

        Returns:
            Rendered SQL script.

        """
        jenv = JinjaRepo(self.setup.jinja_repo_source.root_dir)
        jinja_parameters_dict = self._maybe_get_jinja_insert_dict(key, jinja_parameters_dict, frame,
                                                                  rename_columns_dict)
        sql = self._get_sql_from_jinja_template(jenv, inner_path, jinja_parameters_dict)
        return sql

    def resolve_dimension_jinja_file(self, script_path: str, key: str | list | tuple, jinja_parameters_dict: dict,
                                     frame: str | int = None,
                                     rename_columns_dict: dict | None = None) -> str:
        """
        Resolves a dimension script from a jinja script.

        Args:
            script_path: Absolute or relative path to the jinja script
            key: Column(s) within dataframe to insert into the template.
            jinja_parameters_dict: Keyword parameters to pass into jinja tags.
            frame: Frame of mipi to use for the inserts. If `None` target_population will be used.
            rename_columns_dict: Rename columns before they are inserted into the template.

        Returns:
            Rendered SQL script.

        """
        path = Path(script_path)
        jenv = JinjaLibrary(path.parent)
        jinja_parameters_dict = self._maybe_get_jinja_insert_dict(key, jinja_parameters_dict, frame,
                                                                  rename_columns_dict)
        sql = self._get_sql_from_jinja_template(jenv, path.name, jinja_parameters_dict)

        return sql

    def resolve_dimension_jinja_string(self, script: str, key: str | list | tuple, jinja_parameters_dict: dict,
                                       frame: int | str = None,
                                       rename_columns_dict: dict | None = None) -> str:
        """
        Resolves a dimension script from a jinja string.

        Args:
            script: Jinja SQL template string
            key: Column(s) within dataframe to insert into the template.
            jinja_parameters_dict: Keyword parameters to pass into jinja tags.
            frame: Frame of mipi to use for the inserts. If `None` target_population will be used.
            rename_columns_dict: Rename columns before they are inserted into the template.

        Returns:
            Rendered SQL script.
        """
        template = Template(script)
        jinja_parameters_dict = self._maybe_get_jinja_insert_dict(key, jinja_parameters_dict, frame,
                                                                  rename_columns_dict)
        return template.render(jinja_parameters_dict)

    @property
    def base_population(self) -> pd.DataFrame:

        """
        The dataframe used to create the DataManager Object. This attribute is only stored if
        `store_base_df = True` or if `store_all_dfs = True` during initialization.
        The meta data for this dataframe is represented in the zeroth Frame in `DataManager.frames`.
        Initially this dataframe defines the granularity and records that are used
        in subsequent queries.

        Returns: self._frames[0].df_query

        Raises:
            AttributeError: If `store_base_df` or `store_all_dfs` is False, indicating that the base population
                was not saved to the object.

        """

        if self.setup.store_base_df or self.setup.store_all_dfs:
            return self._frames[0].df_query  # first frame
        else:
            raise AttributeError(
                "base_population is not available because store_base_df and store_all_dfs are False.")

    @property
    def target_population(self) -> pd.DataFrame:
        """
        This is the "working dataframe" where all changes are applied. Initially it is equal to the `base_population`.
        The meta data for this dataframe is always represented by the maximum in `DataManager.frames`
        This property is writable, but it is recommended to extract the dataframe from the object before editing it.

        Returns: The final dataframe with all operations applied to it.

        See Also:
            [rename_select_columns][mipi_datamanager.wrangle.rename_select_columns]: Your final data set will have extra columns with generalized names.
        """
        return self._target_population

    # @target_population.setter
    # def target_population(self, target_population):
    #     self._target_population = target_population

    @property
    def trgt(self):
        """
        This is a read only abbreviated property of the `target_population` dataframe. It is useful for creating
        creating boolean masks.

        Examples:
             >>> dm = DataManager.from_sql(...)
             >>> mask = dm.trgt["column1"] == "my value"
             mask = pd.Series(True,False,True,True)

        Returns: self.target_population

        """
        return self._target_population

    def print_target_columns(self):
        """
        Returns: List of all columns currently in the target population dataframe
        """
        print(self._target_population.columns.tolist())

    def print_target_column_dict(self):
        """
        A string representation of a dictionary of the columns in the target population dataframe.
        Useful when combined with [rename_selected_columns][mipi_datamanager.wrangle.rename_select_columns]
        """

        col_dict = com._columns_to_dict(self.trgt)
        col_dict_str = com._dict_to_string(col_dict)
        col_dict_str = "columns.rename_select_columns(\n{" + col_dict_str + "})"
        print(col_dict_str)

    @property
    def duplicated_columns(self) -> list:
        """

        List of all columns in the target dataframe that contain a "~" character. When duplicate columns
        are created due to a MiPi join, both duplicate columns will be renamed with a tilde followed by their origin frame.
        This property indicates all values which have been duplicated but have not been renamed or removed.

        Returns: A list of all columns containing a tilde.

        See Also:
            - [coalesce][mipi_datamanager.wrangle.coalesce]: to remove duplicate columns
            - [rename_select_columns][mipi_datamanager.wrangle.rename_select_columns]: to select and rename your prefered column
        """
        return [col for col in self._target_population.columns if "~" in col]  # TODO check, this is not robust

    @property
    def frames(self) -> com.IndexedDict:
        """
        A dictionary where each entry is a [frame][mipi_datamanager.core.meta._Frame]. A frame represents a snapshot of
        current DataManager its dataframes. Frames are stored in an "indexed dictionary".
        Every frame is suffixed by its index, starting at 0 with the initial base population. Frames can be accessed
        by their integer index or by their full name.

        Examples:
            >>> DataManager.frames["my_base_frame_0"]
            >>> DataManager.frames[0]
        """

        return self._frames
