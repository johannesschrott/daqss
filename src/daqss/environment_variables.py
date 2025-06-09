from enum import Enum


class EnvironmentVariables(Enum):
    """For the configuration of DaQSS environment variables, as described in the following, are available.
    For a description of how the environment variables are used and for examples please see the
    [dedicated documentation](environment_variables.md) page."""

    DAQSS_DATABASE = "DAQSS_DATABASE"
    """The name of the database that holds the data of DaQSS."""

    DAQSS_HOST = "DAQSS_HOST"
    """The database host used for connecting to the database that holds the data of DaQSS.
     The value of this environment variable must include the address and port of the database server.

     ??? example
         Example values for this environment variable would be `0.0.0.0:5432` or `myhost.com:5432`. 

    """

    DAQSS_PASSWORD = "DAQSS_PASSWORD"
    """The password used for connecting to the database that holds the data of DaQSS."""

    DAQSS_USERNAME = "DAQSS_USERNAME"
    """The username used for connecting to the database that holds the data of DaQSS."""
