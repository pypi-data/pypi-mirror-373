"""
A 'dimension' script is intended to match the records/granularity of a population. An 'insert statement' is the term
for sql statement which injects the records of a populaiton into the dimension script. This is usually done using a
temp table. The MiPi datamanager does this automatically, however the functions below create them outside of the DM.
All of these functions create insert statements from a dataframe.

!!! note
    The temp table name must correspond to the SQL template. For example, if using the default, the script template
    can join from MiPiTempTable to access its values.

"""


from jinja2 import Template
import pandas as pd


class _GenerateInserts:
    def __init__(self, df:pd.DataFrame, table_name:str, insert_type:str):
        self.df = df.drop_duplicates().dropna(how='all')
        self.table_name = table_name
        self.insert_type = insert_type

    def _get_col_dtypes(self, convert_dtypes = True):
        if convert_dtypes:
            _df = self.df.convert_dtypes() #TODO that all types are formatted correctly

        dtype_mapping = {
            'int64': 'INT',
            'float64': 'FLOAT',
            'object': 'NVARCHAR(MAX)',
            'bool': 'BIT',
            'datetime64[ns]': 'DATETIME',
        }

        return [(col, dtype_mapping.get(str(self.df[col].dtype), 'NVARCHAR(MAX)')) for col in self.df.columns]

    def _get_join_key_values(self):
        # Step 3: Prepare rows for insertion
        rows = []
        for _, row in self.df.iterrows():
            formatted_row = []
            for val in row:
                if pd.isna(val):
                    formatted_row.append('NULL')
                elif isinstance(val, str):
                    formatted_row.append(f"'{val}'")
                else:
                    formatted_row.append(str(val))
            rows.append(formatted_row)
        return rows

    def _get_sql_template(self):

        # Base template for insert statements
        insert_template = """{% for row in rows -%}
INSERT INTO {{ temp_table_name }} ({{ columns | map(attribute=0) | join(', ') }}) VALUES ({{ row | join(', ') }});
{% endfor %}
"""

        # Optional table creation template
        if self.insert_type == "table":
            create_table_template = """SET NOCOUNT ON;
CREATE TABLE {{ temp_table_name }} (
    {% for column, dtype in columns -%}
    {{ column }} {{ dtype }}{% if not loop.last %},{% endif %}
    {% endfor %});

"""
            # Combine create table and insert templates, with create table first
            sql_template = create_table_template + insert_template
        elif "records" in self.insert_type:
            # Use only the insert statements if type is not "table"
            sql_template = insert_template
        else:
            raise ValueError("Insert type must be either 'table' or 'records'")

        return sql_template  # Return the combined template

    def _render_sql_template(self):
        sql_template = self._get_sql_template()
        template = Template(sql_template)
        rendered_sql = template.render(temp_table_name=self.table_name, columns=self._get_col_dtypes(), rows=self._get_join_key_values())

        return rendered_sql

def generate_insert_table(df:pd.DataFrame, insert_table_name:str="#MiPiTempTable") -> str:

    """
    Creates a SQL string that can be inserted into SQL script templates.

    The SQL string defines a (temp) table using the columns in the provided dataframe.
    It then inserts each record value into the temp table that was just created.

    Args:
        df: dataframe to use as the source
        insert_table_name: Name of the temp table to insert values into, must correspond to the SQL template. The
            table name prefix determines the type of table

            - `#` temp table
            - `@` variable table
            - `[no-prefix]` standard table

    """

    inserter = _GenerateInserts(df, insert_table_name, "table")
    return inserter._render_sql_template()


def generate_insert_records(df: pd.DataFrame, insert_table_name: str = "#MiPiTempTable") -> str:
    """
    Creates a SQL string that can be inserted into SQL script templates.

    This function does not create a temp table. It writes a statement that inserts the record values from the dataframe
    into a pre-existing table.


    Args:
        df: dataframe to use as the source
        insert_table_name: Name of the temp table to insert values into, must correspond to the SQL template. The
            table name prefix determines the type of table

            - `#` temp table
            - `@` variable table
            - `[no-prefix]` standard table

    """
    inserter = _GenerateInserts(df, insert_table_name, "records")
    return inserter._render_sql_template()



def generate_insert_records2(df: pd.DataFrame) -> str:
    """
    Creates a SQL string that can be inserted into SQL script templates.
    This is a preset function to reduce arguments.


    This function does not create a temp table. It writes a statement that inserts the record values from the dataframe
    into a pre-existing table variable table preceded with `@`

    Args:
        df: dataframe to use as the source

    """
    inserter = _GenerateInserts(df, "@" + "_".join(df.columns), "records")
    return inserter._render_sql_template()

