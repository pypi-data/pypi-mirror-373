import datetime as dt
from sqlalchemy import create_engine

class Odbc:
    """
    Creates an Odbc connection object that can be used in any MiPi function that queries a database. This function
    automatically handles setup and taredown of the connection even if there is an error.

    Args:
        dsn: The DSN name used to configure the connection
    """

    def __init__(self, dsn:str = None, driver = None, server = None, database = None, uid = None, pwd = None, trusted_connection = "yes", dialect = "mssql"):

        self.dsn = dsn
        self.driver = driver
        self.server = server
        self.database = database
        self.uid = uid
        self.pwd = pwd
        self.trusted_connection = trusted_connection
        self.dialect = dialect

        self.name = self.dsn or self.database


    @property
    def connection_string(self):
        params = {self.dsn:"?odbc_connect=DSN",
                  self.driver:"DRIVER",
                  self.server:"SERVER",
                  self.database:"DATABASE",
                  self.uid:"UID",
                  self.pwd:"PWD",
                  self.trusted_connection:"Trusted_Connection"}
        con_str = f"mssql+pyodbc:///"
        for param,key in params.items():
            if param:
                con_str += f"{key}={param};"

        return con_str

    def __enter__(self):
        self.engine = create_engine(self.connection_string)
        self.con = self.engine.connect()
        self.start = dt.datetime.now()
        print(f"\nConnection Established: {self.name} @ {self.start}")
        return self.con

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()
        end = dt.datetime.now()
        print(f"Connection Terminated:  {self.name} @ {end}")
        print(f"Connection Open For:    {end - self.start}")
