The [Python Package of DaQSS](../set-up.md#python-package)
requires [Python, Version 3.12 or higher](https://www.python.org/downloads/release/python-3120/), and depends on the
following Python packages that are
automatically installed when installing DaQSS:

* [`dill`](https://dill.readthedocs.io/en/latest/): Dill provides serialization functionalities. In DaQSS, it is used
  to (de)serialize the Python implementation of DQ metrics.
* [`dotenv`](https://github.com/theskumar/python-dotenv): The dotenv package provides the functionality to use
  environment variables defined in `.env` files.
* [`pandas`](https://pandas.pydata.org/): The Pandas package provides data structures and functions for working with
  tabular data. In DaQSS, DQ results to be stored and to be retrieved are contained in
  a [Pandas DataFrame][pandas.DataFrame].
* [`psycopg2`](https://www.psycopg.org/): Pyscopg is a database adapter that enables Python to connect to PostgreSQL
  databases.
* [`sqlalchemy`](https://www.sqlalchemy.org/): SQLAlchemy describes itself as "the Python SQL toolkit and Object
  Relational Mapper". In DaQSS, classes from the package are used as an abstraction layer for connecting to, inserting
  into, and querying a PostgreSQL database.

For the generation of this documentation [MkDocs](https://mkdocs.org) is used.
The dependencies required for the generation can be installed by running
`pip install "daqss[docs] @ git+https://github.com/johannesschrott/daqss.git"`.