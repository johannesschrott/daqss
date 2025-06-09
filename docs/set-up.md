# Set up DaQSS

DaQSS consists of two parts: [(1) a database part](#database-part)
and [(2) a Python package called `daqss`](#python-package) that enables an integration
into Python-based data processes.
In the following, the setup process is described for each part.

## Database Part

There are two ways of how to set up the database part. Both ways have in common, that the files
from <https://johannes.schrott.onl/daqss/db_setup.zip> are needed.

On the one hand,
it is possible to manually set up a PostgreSQL database using the SQL scripts provided in the `database_setup`
directory of the project. On the other hand, a [Docker Compose](https://docs.docker.com/compose/) file that
automatically configures, populates, and runs a PostgreSQL database in a container is provided.

While the manual setup provides more potential for the configuration of the database, e.g., creating multiple users with
different permission, using the Docker Compose file is the easiest and quickest way to setup a working installation
of DaQSS. This way for setup provides only limited configuration options that can be set by using
[environment variables](technical/environment_variables.md).
The following table compares the system requirements and the setups steps that need to be taken for either way of
database
setup:

|                             | (1) Manual setup                                                                                                                                                                                                                                        | (2) Docker Compose                                                                                                                          |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| **Required software**       | PostgreSQL 17                                                                                                                                                                                                                                           | Docker Compose _or_ Podman Compose                                                                                                          |
| **Setup steps to be taken** | <ol><li>Installation and initial configuration of the PostgreSQL database</li><li>Create and populate the database and the tables required for DaQSS using the provided SQL scripts.</li><li>Create users, set fine-granular permissions etc.</li></ol> | <ol><li>[Define environment variables](technical/environment_variables.md)</li><li>Run `docker compose up` or `podman-compose up`</li></ol> |

## Python Package

Although the database part of DaQSS alone could already be useful, its full potential can only be unleashed together
with the Python package, which enables access to the database part of DaQSS directly from Python.

In order to install the package,
Python must be installed having a version of at least 3.12.
Following this, the command `pip install https://johannes.schrott.onl/daqss/python.zip` must be
run to install the current version of the package together with
its [dependencies](technical/dependencies.md) into the current Python environment.
Before being able to use the installed Python pacakge, it must be ensured that
the [environment variables](technical/environment_variables.md) required for the Python package are set.
This could be achieved, e.g., by placing an [.env file](technical/environment_variables.md#example) in the working
directory from which the Python package will be used.

*[SQL]: Structured Query Language