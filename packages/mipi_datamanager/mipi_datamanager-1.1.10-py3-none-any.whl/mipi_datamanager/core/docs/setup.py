"""
MiPi's universal setup feature allows you to globally define the settings of your DataManager, so you do not have
to define them every time you use it. The Universal Setup uses a file called: `mipi_setup.py` which sets default values
when instantiating a datamanager. The DataManager constructors suffixed with `_preset` will reference your `mipi_setup.py`.

## Create a setup file

The setup file can be used as shown below to set the following attributes

```python

# Import mipi structures
from mipi_datamanager.formatters import FormatDict, cast_padded_int_str,cast_int_str
from mipi_datamanager import JinjaRepo, connection


# declare the variable you want to use by preceeding it with "set_"
set_jinja_repo = JinjaRepo(root_dir="path/to/repo",
                           conn_dict={"con1":connection.Odbc(dsn="MY_DSN1"),
                                      "con2":connection.Odbc(dsn="MY_DSN2")
                                      })

# declare format dict with callables that will used any time the column enters the dataframe
set_format_dict = FormatDict({"ID": lambda x:x,
                              "ID2": lambda x:x})

#only the final instance of the variable will be kept so you can add more
set_format_dict.update({"ID3": lambda x:x})

#you can use use any of mipi's format functionality here
set_format_dict.update_group(["ID4","ID5"],cast_padded_int_str(4))


#additonal available defaults
set_insert_table_type = "full"
set_insert_table_name = "MiPiTempTable"
set_store_all_dfs = False
set_store_base_df = False
set_dialect = "mssql"

```


## Link your file to MiPi

When a setup constructor is called, Mipi will look in the following places for a setup file. It will give precedance to
the first locations on this list

1. A setup file defined in the constructor using `mipi_setup = path/to/mipi_setup.py`
2. Current Working Directory
3. Directory where executing file is located
4. Location assigned by environment variable `MIPI_SETUP_PATH`
5. Virtual Environment directory (location where mipi is installed, site-packages)
"""