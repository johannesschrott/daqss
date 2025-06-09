# Source Code Documentation of the Environment Variables

For the configuration
of [the Docker compose installation variant of the database part](../set-up.md#database-part)
of DaQSS and for the configuration of the connection from
the [Python Package](../set-up.md#python-package) to the database part, environment variables
are used.

## Description

DaQSS relies on four environment variables, of which two must be set in order to be able to use the system:

* `DAQSS_DATABASE`: The name of the database that contains the tables that hold the data of DaQSS. This variable is only
  used by the Python package and should only be set when a manual setup of the PostgreSQL database has been performed.
  Defaults to `daqss` if not provided.
* `DAQSS_HOST`: The database host that holds the data of DaQSS.
  The value of this environment variable must include the address and port of the database server. This variable is only
  used by the Python package and should only be set when a manual setup of the PostgreSQL database has been performed or
  when the Docker Compose setup was performed on any other host than `localhost`. Defaults to `localhost` if not
  provided.

??? example "Example values"

    E.g., `0.0.0.0:5432` or `myhost.com:5432`. 

* `DAQSS_PASSWORD`:
  The password used for connecting to the database that holds the data of DaQSS. This variable must always be
  provided when using DaQSS. In case the Docker Compose database setup is used, the value of this variable is the
  password that can be used to connect to the database.

* `DAQSS_USERNAME`:
  The username used for connecting to the database that holds the data of DaQSS. This variable must always be
  provided when using DaQSS. In case the Docker Compose database setup is used, the value of this variable is the
  username that can be used to connect to the database.

## Example

The environment files could be either set globally to be part of a terminal environment, e.g., by running commands like
`export VARIABLE=value` on Linux, or locally by placing an `.env` file in the directory where DaQSS is used.

An `.env` file can look like the one shown below:

``` text title=".env"
DAQSS_USERNAME="johannes"
DAQSS_PASSWORD="mysupersecretpassword"
```