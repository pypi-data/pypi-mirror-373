"""
## Current Version: 1.0.0


## Behold the simplicity MiPi!

**Mipi** allows you to build a custom data set, from multiple sources, with just a few lines of code!

```python
from mipi_datamanager import DataManager
from mipi_datamanager.connection import Odbc
import pandas as pd

'''
Setup Section
'''

# Define connections to be used in queries
con1 = Odbc(dsn="my_dsn")

# Create a base population of records to be inserted into subsequent queries
mipi = DataManager.from_sql("path/to/sql_script.sql",con1)

'''
Join in additional data using "dimension scripts"
'''

# Example: Query the records of the base population and add a new dimension using string formatting
mipi.join_from_format_sql("path/to/jinja_sql_script.sql",con1,"join_key","left")

# Example: Query the records of the base population and add a new dimension using Jinja
mipi.join_from_jinja("path/to/jinja_sql_script.sql",con1,"join_key2")

# Example: Add a dimension using a pre configured repository
mipi.join_from_jinja_repo("inner/sql_repo/path")

# Example: Filter the data using an excel file
mipi.join_from_excel("path/to/excel_file.xlsx","join_key","inner")

# Example: Filter the data using a dataframe
df = pd.DataFrame()
mipi.join_from_dataframe(df,"join_key","inner")


# Extract the final dataframe
df_final = mipi.trgt

```


## Elevator Pitch
**The problem with SQL:** Although it is wonderfully simple, it is not modular which makes it difficult to adapt a
query several use cases. You will often end up with a mess of sql scripts that are similar, and largely use the same chunks of code.

**The MiPi Solution:** MiPi is built for the organized analyst who wants to invest in creating a library of
interchangeable SQL templates scripts. MiPi features a "DataManager" (DM) object, which adds a
level of abstraction to a pandas dataframe. The MiPi workflow involves setting a "Base Population" as your starting dataframe.
You can then use your library of modular sql scripts to add additional data a la carte to curate your final "Target Population" dataframe.
Below is an example work flow to curate a 2 related data sets from several data sources.

## Example Workflow
```mermaid
graph TD
    subgraph Set a base population
    A[DM.from_sql]
    end
    subgraph Refine the Target Population

    A --> B[DM.join_from_format_sql <br> *join in columns]
    B --> C[DM.join_from_excel <br> *inner join to filter]
    C --> D[DM.join_from_format_sql]
    end
    subgraph Create a child DM
    C -.-> E[DM2 = DM.clone <br> *create new DM]
    E --> F[DM2.join_from_jinja]
    end
    subgraph Extract Populations
    D --> I[df1 = DM.trgt]
    F --> G[df2 = DM2.trgt]
    end

```



### Consented Operations

Each data addition is a breeze. The DM's convent methods, do all the back end work,
all you have to do is specify what data to add! Below is a list of operations performed automatically by the DM.

- Resolve script templates so that their results all have matching granularity/keys.
- Handle parameters in script templates, such as start and end date.
- Open and close your connections even in the event of errors
- Run your query
- Store a history of all (resolved) SQL scripts, and optional data frame history.
- Join the results of the subsequent query into your main data frame
- Resolve any duplicate column names with meaningful suffix names

### Resolving query templates

The DM keeps track of the records in your "Target Population" (TP) which is the main working dataframe.
It is able to generate a sql temp table containing these records. This temp table is inserted into any subsequent SQL
queries. Each dimension script will only fetch relevant records allowing, which makes queries dynamic and efficent


### Example dimension join

Below is an example dataframe that will represent the Target Population within the MiPi Datamanager:

!!! TODO
    better example which illustrates the importance of templating.

| Primary Key | Value    |
|-------------|----------|
| 1           | A        |
| 2           | B        |
| 3           | C        |

We want to want to add the commonly used "Value 2" using a modular dimension script, but only for the records shown above.
The join method shown below generates a query, runs it, and joins the result all in one step!

`mipi.join_from_sql("path/to/jinja_sql_script.sql",con1,"join_key","left")`

The DM creates a temp table from your target population, and inserts it into the template script. The following is an
example of a fully resolved script that the datamanager might generate.
```sql
-- temp table inserted by datamanager
CREATE TEMPORARY TABLE #MiPiTempTable (PrimaryKey);
INSERT INTO #MiPiTempTable Values (1)
INSERT INTO #MiPiTempTable Values (2)
INSERT INTO #MiPiTempTable Values (3)

-- modular sql script which returns add on dimensions.
SELECT tmp.PrimaryKey,Value2
FROM #MiPiTempTable as tmp
LEFT JOIN foreign_table ft
    ON tmp.PrimaryKey = ft.Value2;

```

The DM will then merge the results of this query into your working target population to achieve the following table.
Not that all DM operations are performed inplace.

| Primary Key | Value    | Value2 |
|-------------|----------|--------|
| 1           | A        | D      |
| 2           | B        | E      |
| 3           | C        | F      |


## Script Setup:

SQL scripts need to follow a specific format so that MiPi can resolve them. Don't worry, it is easy to setup!
There are 2 types of scripts that MiPi can run:

**Population scripts:** define the target population and their records will be
used for all subsequent queries. Population scripts can be structured like a regular SQL script and can optionally use
parameters, like start and end date. These scripts pair to the data managers constructor methods. These methods will
always be prefixed with "from_". For example `mipi = DataManager.from_sql(...)`


**Dimension scripts:** explain the target population.
They run a subsequent query using the target populations join key and return additional columns for the same records.
Dimension scripts can also optionally use parameters. However every dimension script REQUIRES a special pamemeter
which will accept a temp table to define the records to pull back. These scripts will always be prefixed with "join_from_".
For example `mipi.join_from_format_sql(...)`.


### Format SQL

String formatting uses "{}" place holders to add additional values. "Format SQL" scripts always assume the first
place holder will accept the temp table. Optionally additional parameters can be passed into `format_parameters_list`
in their desired order.

The following join method pairs to the following format sql script

```python
mipi.join_from_sql("my_query.sql",con1,"join_key","left",
                    format_parameters_list = ["param_val1", "param_val2"])
```

```tsql
{}

SELECT tmp.PrimaryKey,Value2
FROM #MiPiTempTable as tmp
LEFT JOIN foreign_table ft
    ON tmp.PrimaryKey = ft.Value2;
WHERE param = {}
AND   param2 = {}

```

This method calling this script would resolve to the following.

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



### Jinja
[Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) is a popular library for string templating. Jinja takes this a
step further but adding using a dictionary and named place holder tags. In addition to readability, jinja introduces
advanced logic within the actual sql script. view the [offical Jinja Documentation](https://jinja.palletsprojects.com/en/3.1.x/)
for details. This method expects that the sql script will have a tag `MiPiTempTable`, but this does not need to be defined
your dictionary becasue it is generated by the DM.

The above example translates to jinja as follows.


```python

jinja_parameters_dict = {"param1":"param_val1",
                         "param2":"param_val2"}

mipi.join_jinja_sql("my_query.sql",con1,"join_key","left",
                    jinja_parameters_dict = jinja_parameters_dict)
```

```tsql
{{MiPiTempTable}}

SELECT tmp.PrimaryKey,Value2
FROM #MiPiTempTable as tmp
LEFT JOIN foreign_table ft
    ON tmp.PrimaryKey = ft.Value2;
WHERE param1 = {{ param1 }}
AND   param2 = {{ param2 }}

```




## User Guide
---

View the following for more information on advanced features and user API's!


* [Installation](home/install.md): Installation and environment setup.
* [Contribute](home/contribute.md): Help make the next version of MiPi. Seeking contributors now!
* [DataManager](api/data_manager.md): Details on all DataManager Methods.

Coming Soon:

* JinjaRepo: Setup a formal repository of Jinja scripts using with preset configurations.
* RepoConfigBuilder: A local GUI app to make managing your repo a breeze.

"""