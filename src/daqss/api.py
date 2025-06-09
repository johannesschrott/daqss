import os
from collections import namedtuple
from typing import Callable
from datetime import datetime, timezone
import dill
import logging

import pandas
import sqlalchemy.engine.base

from daqss import EnvironmentVariables
from daqss import LevelOfDataGranularity

try:
    import pretty_errors
except ModuleNotFoundError:
    pass

from dotenv import load_dotenv
from sqlalchemy import Engine, Row, create_engine, text, ResultProxy
from sqlalchemy.exc import IntegrityError

DQResult = namedtuple("DQResult", ["name", "ordering"])
"""A [named tuple][collections.namedtuple] 
that contains the `name` and the `ordering` of a level of data granularity."""


class DaQSS:
    """Instances of the class DaQSS hold the connection to the PostgreSQL database and provide functions
     that enable a convenient access to the system. As described for the initializer,
    the connection to the database is configured using environment variables."""

    def __init__(self) -> None:
        """Initializes a new DaQSS instance that can connect to a DaQSS database.
         The connection settings must be customized using
          [environment variables][src.daqss.environment_variables.EnvironmentVariables]:

         **Mandatory environment variables:**

            - [`DAQSS_USERNAME`][src.daqss.environment_variables.EnvironmentVariables.DAQSS_USERNAME]
            - [`DAQSS_PASSWORD`][src.daqss.environment_variables.EnvironmentVariables.DAQSS_PASSWORD]

         **Optional environment variables:**

            - [`DAQSS_HOST`][src.daqss.environment_variables.EnvironmentVariables.DAQSS_HOST] - default value: `localhost:5432`
            - [`DAQSS_DATABASE`][src.daqss.environment_variables.EnvironmentVariables.DAQSS_DATABASE] - default value: `daqss`

        """
        load_dotenv()

        username: str | None = os.getenv(EnvironmentVariables.DAQSS_USERNAME.value)
        if username is None:
            logging.error("No username provided.")

        password: str | None = os.getenv(EnvironmentVariables.DAQSS_PASSWORD.value)
        if password is None:
            logging.error("No password provided.")

        host: str = os.getenv(EnvironmentVariables.DAQSS_HOST.value, "localhost:5432")
        database: str = os.getenv(EnvironmentVariables.DAQSS_DATABASE.value, "daqss")

        connection_string: str = f"postgresql+psycopg2://{username}:{password}@{host}/{database}"

        self._engine: Engine = create_engine(connection_string)
        """The [Engine][sqlalchemy._engine.Engine] object is used for connecting to the DaQSS
         database when the methods provided by this class are used."""

    def connect(self) -> sqlalchemy.engine.base.Connection:
        """Returns the SQLAlchemy [Connection][sqlalchemy.engine.base.Connection] to directly
        query the system using SQL.

        Returns:
            The connection with DaQSS that can be used to query it using SQL."""
        return self._engine.connect()

    def retrieve_aggregation_constraint_formula_by_name(self, name: str) -> str:
        """Retrieves the formula of an aggregation constraint suitable for usage with CobADQ by its name.

        Args:
            name (str): The name of the aggregation constraint to be retrieved.

        Returns:
            A string that contains the formula of an aggregation constraint for usage with CobADQ.
        """
        with self._engine.connect() as connection:
            query_result: ResultProxy = connection.execute(
                text(
                    """SELECT aggregation_constraint_formula 
                    FROM aggregation_constraint 
                    WHERE aggregation_constraint_name = :name""",
                    {"name": name})
            )

            formula: str = query_result.fetchone()[0]
            return formula

    def retrieve_aggregation_function_expression_by_name(self, name: str) -> str:
        """Retrieves the expression of an aggregation function by its name suitable for usage with CobADQ.

        Args:
            name (str): The name of the aggregation function to be retrieved.

        Returns:
            A string that contains the expression an aggregation function for usage with CobADQ.
        """
        with self._engine.connect() as connection:
            query_result: ResultProxy = connection.execute(
                text(
                    """SELECT aggregation_function_expression 
                    FROM aggregation_function 
                    WHERE aggregation_function_name = :name""",
                    {"name": name})
            )

            expression: str = query_result.fetchone()[0]
            return expression

    def retrieve_aggregation_process_by_name_as_aggregation_specification(self, name: str) -> str:
        """Retrieves the specification of an aggregation process by its name, directly to be used with CobADQ.

        Args:
            name (str): The name of the aggregation process to be retrieved.

        Returns:
            A string that contains the specification of an aggregation directly for usage with CobADQ.
        """
        with self._engine.connect() as connection:
            query_result: ResultProxy = connection.execute(
                text(
                    "SELECT '('||aggregation_constraint.aggregation_constraint_formula||'," +
                    "'||aggregation_function.aggregation_function_expression||')'" +
                    "FROM aggregation_process_is_based_on, aggregation_function, aggregation_constraint " +
                    "WHERE aggregation_process_is_based_on.aggregation_process_name = :process_name " +
                    "AND aggregation_process_is_based_on.aggregation_function_name = " +
                    "    aggregation_function.aggregation_function_name " +
                    "AND aggregation_process_is_based_on.aggregation_constraint_name = " +
                    "    aggregation_constraint.aggregation_constraint_name"
                ),
                {"process_name": name}
            )

            expression: str = "{" + ",".join(map(lambda row: row[0], query_result.fetchall())) + "}"
            if len(expression) == 2:
                logging.error("No aggregation specification could be retrieved for the given aggregation process name.")
            else:
                return expression

    def retrieve_dq_metric_implementation_by_name(self, name) -> Callable:
        """Retrieves the implementation of a metric in the form of a Python callable by its name.

                Args:
                    name (str): The name of the metric implementation to be retrieved.

                Returns:
                    The metric implementation in form of a callable.
                """
        with self._engine.connect() as connection:
            query_result: ResultProxy = connection.execute(
                text(
                    "SELECT python_implementation " +
                    "FROM dq_metric " +
                    "WHERE metric_name = :name"),
                {"name": name}
            )

            byte_string: str | None = query_result.first()[0]
            if byte_string is None:
                logging.error(f"There is no implementation for a DQ metric with the name \"{name}\".")
            else:
                return dill.loads(byte_string)

    def retrieve_levels_of_data_granularity(self) -> list[LevelOfDataGranularity]:
        """Connects to the DaQSS database and retrieves the levels of data granularity known to DaQSS
        in the form of a list that contains instances of the
        [named tuple][src.daqss.level_of_data_granularity.LevelOfDataGranularity].

        Returns:
            A list of the levels of data granularity containing their names and ordering in a
            [named tuple][src.daqss.level_of_data_granularity.LevelOfDataGranularity].\
                \
                Example result:\
                `[("value", 0), ("row", 1)]`
            """
        with self._engine.connect() as connection:
            query_result: ResultProxy = connection.execute(
                text("""SELECT level_name, ordering FROM levels_of_data_granularity ORDER BY ordering ASC""")
            )

            result: list[LevelOfDataGranularity] = [LevelOfDataGranularity(name=row[0], ordering=row[1])
                                                    for row in query_result]

            return result

    def store_aggregation_constraint(self, name: str, description: str, constraint: str,
                                     level_of_data_granularity: LevelOfDataGranularity):
        """Stores an aggregation constraint in the database part of DaQSS.

         If storing fails, a warning is logged.

        Args:
            name: A name under which the aggregation constraint can be uniquely identified.
            description: The description of what leads to fulfillment of the aggregation constraint.
            constraint: The aggregation constraint encoded in CobADQs custom language
            level_of_data_granularity: The level of data granularity at which the constraint can be applied.
        """

        try:
            with self._engine.connect() as connection:
                connection.execute(text(
                    "INSERT INTO aggregation_constraint (aggregation_constraint_name, aggregation_constraint_description, "
                    "aggregation_constraint_formula, covers_level_of_data_granularity) " +
                    "VALUES (:name, :description, :constraint, :lodg)"),
                    {"name": name, "description": description,
                     "constraint": constraint, "lodg": level_of_data_granularity.name})
                connection.commit()
        except IntegrityError:
            logging.warning(
                f"The aggregation constraint with the name \"{name}\" cannot " +
                f"be stored, since an aggregation constraint with the same name already exists.")

    def store_aggregation_function(self, name: str, description: str, expression: str,
                                   source_level_of_data_granularity: LevelOfDataGranularity,
                                   target_level_of_data_granularity: LevelOfDataGranularity):
        """Stores an aggregation function in the database part of DaQSS.

        If storing fails, a warning is logged.

               Args:
                   name: A name under which the aggregation function can be uniquely identified.
                   description: The description of how the aggregation function works.
                   expression: The expression of the aggregation function encoded in CobADQs custom language.
                   source_level_of_data_granularity: The level of data granularity of the values to aggregate.
                   target_level_of_data_granularity: The level of data granularity of the aggregation result.
               """
        try:
            with self._engine.connect() as connection:
                connection.execute(text(
                    "INSERT INTO aggregation_function (aggregation_function_name, aggregation_function_description, "
                    "aggregation_function_expression, source_level_of_data_granularity, " +
                    "target_level_of_data_granularity) VALUES (:name, :description, :expression, :s_lodg, :t_lodg)"),
                    {"name": name, "description": description,
                     "expression": expression, "s_lodg": source_level_of_data_granularity.name,
                     "t_lodg": target_level_of_data_granularity.name})
                connection.commit()
        except IntegrityError:
            logging.warning(
                f"The aggregation function with the name \"{name}\" cannot " +
                f"be stored, since an aggregation function with the same name already exists.")

    def store_aggregation_process(self, name: str, description: str, query_for_dq_results: str,
                                  constraints_and_functions: list[tuple[str, str]], dimensions: list[str]):
        """Stores an aggregation process in the database part of DaQSS.

        If storing fails, a warning is logged.

        Args:
            name: A name under which the aggregation process can be uniquely identified.
            description: The description of the aggregation process works.
            query_for_dq_results: The query that returns the values to aggregate.
            dimensions: A list of names of DQ dimensions to which the aggregation process is associated.
            constraints_and_functions: A list of tuples that contain the names of the constraints and
                aggregation functions used within the aggregation process.
               """
        try:
            with self._engine.connect() as connection:
                connection.execute(text(
                    "INSERT INTO aggregation_process (aggregation_process_name, aggregation_process_description, "
                    "aggregation_query_for_values) VALUES (:name, :description, :query)"
                ),
                    {"name": name, "description": description,
                     "query": query_for_dq_results})
                for pair in constraints_and_functions:
                    connection.execute(text(
                        "INSERT INTO aggregation_process_is_based_on (aggregation_process_name, " +
                        "aggregation_constraint_name, aggregation_function_name) " +
                        "VALUES (:name, :constraint, :function)"
                    ),
                        {"name": name, "constraint": pair[0],
                         "function": pair[1]})
                connection.commit()
        except IntegrityError as ie:
            logging.warning(
                f"The aggregation process with the name \"{name}\" cannot " +
                f"be stored, since \n - an aggregation process with the same name already exists, or\n" +
                " - it was tried to add a combination of constraint and aggregation function " +
                "that was already associated with this aggregation process, or" +
                " - the supplied constraints and aggregation functions targeted different levels of data granularity.")
        for dimension_name in dimensions:
            try:
                with self._engine.connect() as connection:
                    connection.execute(text(
                        "INSERT INTO aggregation_process_computes_value_for_dimension " +
                        "(aggregation_process_name, dimension_name) VALUES (:a_name, :d_name)"),
                        {"a_name": name, "d_name": dimension_name})
                    connection.commit()
            except IntegrityError:
                logging.warning(
                    f"The aggregation process with the name \"{name}\" cannot be associated with the " +
                    f"DQ dimension \"{dimension_name}\", since\n - this association is already in place, " +
                    f"or \n - the dimension \"{dimension_name}\" does not exist.")

    def store_dq_dimension(self, name: str, description: str or None = None, is_subdimension_of: str or None = None):
        """Stores a DQ dimension in the database part of DaQSS.

        Args:
            name: The name of the DQ dimension to be stored.
            description: The description of the DQ dimension to be stored.
            is_subdimension_of: The name of the dimension of which this dimension is a sub-dimension.
            """
        try:
            with self._engine.connect() as connection:
                if is_subdimension_of is not None:
                    result: list[Row] = list(connection.execute(
                        text("SELECT * FROM dq_dimension WHERE dimension_name = :dimension_name"),
                        {"dimension_name": is_subdimension_of}).fetchall())
                    if len(result) < 1:
                        raise ValueError(f"The supplied parent dimension \"{is_subdimension_of}\" does not exist.")

                    if description is not None:
                        connection.execute(text(
                            """INSERT INTO dq_dimension (dimension_name, dimension_description, is_sub_dimension_of)
                             VALUES (:name, :description, :is_subdimension_of)"""),
                            {"name": name, "description": description, "is_subdimension_of": is_subdimension_of})
                    else:
                        assert description is None
                        connection.execute(text(
                            """INSERT INTO dq_dimension (dimension_name, is_sub_dimension_of)
                             VALUES (:name, :is_subdimension_of)"""),
                            {"name": name, "is_subdimension_of": is_subdimension_of})
                else:
                    assert is_subdimension_of is None
                    if description is not None:
                        connection.execute(text(
                            """INSERT INTO dq_dimension (dimension_name, dimension_description)
                             VALUES (:name, :description)"""),
                            {"name": name, "description": description})
                    else:
                        assert description is None
                        connection.execute(text(
                            """INSERT INTO dq_dimension (dimension_name)
                             VALUES (:name)"""),
                            {"name": name})
                connection.commit()

        except IntegrityError:
            logging.warning(
                f"A DQ dimension with the name \"{name}\" cannot be created," +
                f" since a dimension with the same name already exists.")

    def store_dq_metric(self, dq_metric: Callable, dimensions: list[str],
                        level_of_data_granularity: LevelOfDataGranularity):
        """Store the Python implementation of a DQ metric in the connected PostgreSQL database.

                Args:
                    dq_metric (Callable): The Python implementation of the DQ metric to be stored.
                    dimensions (list[str]): The DQ dimensions for which the DQ metric computes values.
                    level_of_data_granularity (LevelOfDataGranularity): The level of data granularity on which the
                        DQ Metric operates.
                    """
        dq_metric_name = getattr(dq_metric, '__name__', repr(dq_metric))
        # 1. param: the object of which the name attribute should be retrieved
        # 2. param: specifies that the '__name__' attribute should be retrieved
        # 3. param: if the object has no '__name__' parameter,
        #           the string representation of the object should be used as name

        dq_metric_description = getattr(dq_metric, '__doc__', None)
        # 1. param: the object of which the docstring should be retrieved
        # 2. param: specifies that the '__doc__' attribute should be retrieved
        # 3. param: if the object has no docstring, set the variable to None

        dq_metric_serialized = dill.dumps(dq_metric)

        try:
            with self._engine.connect() as connection:
                connection.execute(text(
                    """INSERT INTO dq_metric (metric_name, metric_description, python_implementation, 
                    designed_for_level_of_data_granularity) VALUES (:name, :description, :implementation, :lodg)"""),
                    {"name": dq_metric_name, "description": dq_metric_description,
                     "implementation": dq_metric_serialized, "lodg": level_of_data_granularity.name})
                connection.commit()
        except IntegrityError:
            logging.warning(
                f"A DQ metric with the name \"{dq_metric_name}\" cannot be stored, " +
                f"since a metric with the same name already exists.")

        for dimension_name in dimensions:
            try:
                with self._engine.connect() as connection:
                    connection.execute(text(
                        """INSERT INTO metric_computes_value_for_dimension (metric_name, dimension_name) VALUES (:m_name, :d_name)"""),
                        {"m_name": dq_metric_name, "d_name": dimension_name})
                    connection.commit()
            except IntegrityError:
                logging.warning(
                    f"""The DQ metric with the name \"{dq_metric_name}\" cannot be associated with the DQ dimension \"{dimension_name}\", since\n - this association is already in place, or \n the dimension \"{dimension_name}\" does not exist.""")

    def store_data_element(self,
                           global_identifier: str,
                           local_identifier: str,
                           level_of_data_granularity: LevelOfDataGranularity,
                           parent_identifier: str | None = None):
        """Store the representation of a data element in the connected PostgreSQL database.

        Args:
            global_identifier (str): The globally unique identifier of a data element to be represented in DaQSS.
            local_identifier (str): The identifier that identifies a data element within its parent data element.
            level_of_data_granularity (LevelOfDataGranularity): The level of data granularity of the data element.
            parent_identifier (str | None, optional):
                The unique identifier of a data element in which this data element is contained.
                Defaults to None, which means that the data element is not contained in any other data element.
            """
        if parent_identifier is None:
            try:
                with self._engine.connect() as connection:
                    connection.execute(text(
                        "INSERT INTO data_element (data_element_global_identifier, data_element_local_identifier, " +
                        "is_of_level_of_data_granularity) VALUES (:g_id, :l_id, :lodg)"),
                        {"g_id": global_identifier,
                         "l_id": local_identifier,
                         "lodg": level_of_data_granularity.name})
                    connection.commit()
            except IntegrityError:
                logging.warning(
                    f"The data element with the global_identifier \"{global_identifier}\" cannot " +
                    f"be stored, since an data element with the same global_identifier already exists.")
        else:
            try:
                with self._engine.connect() as connection:
                    connection.execute(text(
                        "INSERT INTO data_element (data_element_global_identifier, data_element_local_identifier, " +
                        "is_of_level_of_data_granularity, parent_data_element_global_identifier) " +
                        "VALUES (:g_id, :l_id, :lodg, :parent_identifier)"),
                        {"g_id": global_identifier,
                         "l_id": local_identifier,
                         "lodg": level_of_data_granularity.name,
                         "parent_identifier": parent_identifier})
                    connection.commit()
            except IntegrityError:
                logging.warning(
                    f"The data element with the global_identifier \"{global_identifier}\" cannot " +
                    f"be stored, since \n - an data element with the same global_identifier already exists, or\n " +
                    f"- the provided parent data element global_identifier \"{parent_identifier} does not exist.")

    def store_dq_aggregation_results_from_series(self,
                                                 aggregation_process: str,
                                                 level_of_data_granularity: LevelOfDataGranularity,
                                                 parent_data_element: str,
                                                 values: pandas.Series):
        """Stores multiple result values computed by a DQ aggregation process.
        If they do not exist, the representations of the data of which the DQ was computed are created.

        Args:
            aggregation_process: The name of the aggregation process that was used to compute the result values.
            level_of_data_granularity: The level of data granularity of the individual result values.
            parent_data_element: The parent data element which contains the individual result values to be stored.
            values: A Pandas series of values that contains the computed result values and the local identifiers of
                their corresponding data values.
        """
        timestamp: str = datetime.now(tz=timezone.utc).isoformat()
        show_warning: bool = False
        for index, value in values.items():
            try:
                with self._engine.connect() as connection:
                    data_element = parent_data_element + "#" + str(index)
                    connection.execute(text(
                        "INSERT INTO data_element (data_element_global_identifier, data_element_local_identifier," +
                        " is_of_level_of_data_granularity, parent_data_element_global_identifier) " +
                        "VALUES (:g_id, :l_id, :lodg, :parent_identifier) " +
                        "ON CONFLICT DO NOTHING "),
                        {"g_id": data_element,
                         "l_id": str(index),
                         "lodg": level_of_data_granularity.name,
                         "parent_identifier": parent_data_element})
                    connection.execute(text(
                        "INSERT INTO dq_result " +
                        "(creation_timestamp, result_value, computed_on_data_element_global_id," +
                        " calculated_by_aggregation_process) VALUES (:timestamp, :result_value, :data_element, :agg)"),
                        {"timestamp": timestamp, "result_value": value, "data_element": data_element,
                         "agg": aggregation_process})
                connection.commit()
            except IntegrityError as ie:
                show_warning = True

        if show_warning:
            logging.warning(
                f"At least one DQ aggregation result cannot be stored, since for at least one result value\n" +
                f" - no data element global_identifier was provided, or\n" +
                f" - the DQ aggregation computed two results for the same data element, or\n" +
                f" - the provided parent data element is not represented in DaQSS")

    def store_dq_measurement_results_from_series(self, dq_metric: Callable,
                                                 level_of_data_granularity: LevelOfDataGranularity,
                                                 parent_data_element: str,
                                                 values: pandas.Series):
        """Stores multiple result values computed by a DQ metric.
        If they do not exist, the representations of the data of which the DQ was computed are created.


        Args:
            dq_metric: The name of the DQ metric that was used to compute the result values.
            level_of_data_granularity: The level of data granularity of the individual result values.
            parent_data_element: The parent data element which contains the individual result values to be stored.
            values: A Pandas series of values that contains the computed result values and the local identifiers of
                their corresponding data values."""
        timestamp: str = datetime.now(tz=timezone.utc).isoformat()
        show_warning: bool = False

        for index, value in values.items():
            try:
                with self._engine.connect() as connection:
                    data_element = parent_data_element + "#" + str(index)
                    connection.execute(text(
                        "INSERT INTO data_element (data_element_global_identifier,  data_element_local_identifier, " +
                        "is_of_level_of_data_granularity, parent_data_element_global_identifier) " +
                        "VALUES (:g_id, :l_id, :lodg, :parent_identifier) " +
                        "ON CONFLICT DO NOTHING "),
                        {"g_id": data_element, "l_id": str(index), "lodg": level_of_data_granularity.name,
                         "parent_identifier": parent_data_element})
                    connection.execute(text(
                        "INSERT INTO dq_result " +
                        "(creation_timestamp, result_value, computed_on_data_element_global_id," +
                        " calculated_by_dq_metric) VALUES (:timestamp, :result_value, :data_element, :metric_name)"),
                        {"timestamp": timestamp, "result_value": value, "data_element": data_element,
                         "metric_name": dq_metric.__name__})
                    connection.commit()
            except IntegrityError as ie:
                show_warning = True

        if show_warning:
            logging.warning(
                f"At least one DQ measurement result cannot be stored, since for at least one result value\n" +
                f" - no data element global_identifier was provided, or\n" +
                f" - the DQ metric computed two results for the same data element, or\n" +
                f" - the provided parent data element is not represented in DaQSS")
