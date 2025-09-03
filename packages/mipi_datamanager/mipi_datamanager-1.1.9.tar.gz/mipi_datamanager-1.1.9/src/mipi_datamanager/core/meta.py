import pandas as pd
from collections import namedtuple
from mipi_datamanager.types import BuildLiterals

Dim = namedtuple("dimension", ["rows", "columns"])

class _Frame:
    """
    Any time data enters the data enters the DataManager (using a construct or join method), a new Frame is created.
    Each Frame within represents a snapshot of the Target Population DataFrame at the point when a given data set was
    introduced. The unmodified data entering is called the "query data" because it is usually the result of a query.
    While the result after it is joined to the target population is the "target data".
    Frames are easy to explore and provide a means to track the history of what entered the dataframe.
    A frame contains the following attributes.

    Attributes:
        name: A frame name is a representation of the contents of the data. By default, the frame name will always be
            the name of the file used to generate the data. However this can be overwritten to be more meaningful.
        built_from: This is information about the data source used to generate the frame. This corresponds to the
            DataManager method used. {"JinjaRepo", "Jinja", "SQL", "Format SQL", "Data Frame", "Excel"}
        sql: If the frame was build from a version of SQL ("JinjaRepo", "Jinja", "SQL") the fully rendered SQL will be saved here.
            This is useful when debugging. This script is can be executed independently, and includes a temp table of your target
            records.
        query_shape: returns `df.shape` of the dataframe returned by the query. This is useful for debugging
            granularity issues, especially if `deep_frames = False`.
        query_columns: returns `df.columns` of the dataframe returned by the query. This is useful for debugging
            column issues, especially if `deep_frames = False`.
        df_query: pd.DataFrame that resulted from the query before being joined to target.
        df_target: pd.DataFrame the target dataframe including the join and all prior joins.

    """

    def __init__(self, name: str,
                 built_from: BuildLiterals,
                 df_query: pd.DataFrame,
                 df_target: pd.DataFrame | None = None,
                 sql: str | None = None,
                 store_deep: bool = True):

        self.store_deep: bool = store_deep
        self.df_query: pd.DataFrame = df_query
        self.df_target: pd.DataFrame = df_target
        self.name: str = name
        self.built_from: str = built_from
        self.sql: str = sql

        self.query_shape: tuple = self._get_dimension(df_query)
        self.query_columns: list = self._get_columns(df_query)

        if df_target:
            self._set_target(df_target)

    def _set_target(self, df_target: pd.DataFrame):
        """Set target for the frame as the current state of the data objects target population"""

        if self.store_deep:
            self.df_target = df_target

        self.target_dimension = self._get_dimension(df_target)
        self.target_columns = self._get_columns(df_target)

    @staticmethod
    def _get_dimension(df: pd.DataFrame) -> Dim:
        return Dim(df.shape[0], df.shape[1])

    @staticmethod
    def _get_columns(df: pd.DataFrame) -> list:
        return list(df.columns)
