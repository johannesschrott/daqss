-- Switch to the "daqss" database before the tables are created
\c daqss
START TRANSACTION;

CREATE TABLE IF NOT EXISTS levels_of_data_granularity
(
    level_name TEXT
        CONSTRAINT levels_of_data_granularity_pk PRIMARY KEY,
    ordering   SMALLINT NOT NULL
);

COMMENT ON TABLE levels_of_data_granularity IS 'Provides the levels of data granularity available in DaQSS.';
COMMENT ON COLUMN levels_of_data_granularity.level_name IS 'The name of a level of data granularity. '
    'This column is the primary key of the table "levels_of_data_granularity", '
    'since the individual levels can have the same value for the column ordering while being semantically different.';
COMMENT ON COLUMN levels_of_data_granularity.ordering IS 'Provides an integer value that declares the order of '
    'the levels of data granularity. Fine-granular levels are assigned smaller integer values,'
    ' coarse-granular levels are assigned greater integer values.';


CREATE TABLE IF NOT EXISTS dq_metric
(
    metric_name                            TEXT
        CONSTRAINT dq_metric_pk PRIMARY KEY,
    metric_description                     TEXT,
    python_implementation                  bytea,
    designed_for_level_of_data_granularity TEXT REFERENCES levels_of_data_granularity (level_name) NOT NULL
);

COMMENT ON TABLE dq_metric IS 'Contains data quality metrics that are designed for a specific level of data granularity '
    'and there serialized Python implementation.';
COMMENT ON COLUMN dq_metric.metric_name IS 'The name of a data quality metric. '
    'This column is the primary key of the table "dq_metric".';
COMMENT ON COLUMN dq_metric.metric_description IS
    'Describes the behavior of a data quality metric, i.e., how it computes a measurement result.';
COMMENT ON COLUMN dq_metric.python_implementation IS
    'Contains the Dill serialization of the Python function that implements this data quality metric';
COMMENT ON COLUMN dq_metric.designed_for_level_of_data_granularity IS
    'References the level of data granularity which the data quality metric is targeted at.';



CREATE TABLE IF NOT EXISTS dq_dimension
(
    dimension_name        TEXT
        CONSTRAINT dq_dimension_pk PRIMARY KEY,
    dimension_description TEXT,
    is_sub_dimension_of   TEXT REFERENCES dq_dimension (dimension_name)
);

COMMENT ON TABLE dq_dimension IS 'Contains the DQ dimensions that are available in DaQSS.';
COMMENT ON COLUMN dq_dimension.dimension_name IS 'The name of a data quality dimension. '
    'This column is the primary key of the table "dq_dimension".';
COMMENT ON COLUMN dq_dimension.dimension_description IS
    'Describes the the data quality dimension in more detail.';
COMMENT ON COLUMN dq_dimension.is_sub_dimension_of IS
    'A data quality dimension may be a sub-dimension of another data quality dimension.';



CREATE TABLE IF NOT EXISTS metric_computes_value_for_dimension
(
    metric_name    TEXT REFERENCES dq_metric (metric_name),
    dimension_name TEXT REFERENCES dq_dimension (dimension_name),
    CONSTRAINT metric_computes_value_for_dimension_pk PRIMARY KEY (metric_name, dimension_name)
);
COMMENT ON TABLE metric_computes_value_for_dimension IS 'Stores information on which metric computes values '
    'for which dimension.';
COMMENT ON COLUMN metric_computes_value_for_dimension.metric_name IS 'The name of the metric that computes a value '
    'for the provided dimension ';
COMMENT ON COLUMN metric_computes_value_for_dimension.dimension_name IS 'The name of a data quality dimension. ';



CREATE TABLE IF NOT EXISTS aggregation_constraint
(
    aggregation_constraint_name        TEXT
        CONSTRAINT aggregation_constraint_pk PRIMARY KEY,
    aggregation_constraint_description TEXT,
    aggregation_constraint_formula     TEXT                                                    NOT NULL,
    covers_level_of_data_granularity   TEXT REFERENCES levels_of_data_granularity (level_name) NOT NULL
);
COMMENT ON TABLE aggregation_constraint IS 'Stores constraints for usage with CobADQ.';
COMMENT ON COLUMN aggregation_constraint.aggregation_constraint_name IS
    'The name of a constraint used for aggregation. '
        'This column is the primary key of the table "aggregation constraint".';
COMMENT ON COLUMN aggregation_constraint.aggregation_constraint_description IS
    'Describes the aggregation constraint in detail.';
COMMENT ON COLUMN aggregation_constraint.aggregation_constraint_formula IS
    'Contains the formula of the aggregation constraint encoded in CobADQs custom constraint language.';
COMMENT ON COLUMN aggregation_constraint.covers_level_of_data_granularity IS
    'References the level of data granularity which is covered by the aggregation constraint.';



CREATE TABLE IF NOT EXISTS aggregation_function
(
    aggregation_function_name        TEXT
        CONSTRAINT aggregation_function_pk PRIMARY KEY,
    aggregation_function_description TEXT,
    aggregation_function_expression  TEXT                                                    NOT NULL,
    source_level_of_data_granularity TEXT REFERENCES levels_of_data_granularity (level_name) NOT NULL,
    target_level_of_data_granularity TEXT REFERENCES levels_of_data_granularity (level_name) NOT NULL
);
COMMENT ON TABLE aggregation_function IS 'Stores aggregation functions for usage with CobADQ.';
COMMENT ON COLUMN aggregation_function.aggregation_function_name IS
    'The name of an aggregation function. '
        'This column is the primary key of the table "aggregation function".';
COMMENT ON COLUMN aggregation_function.aggregation_function_description IS
    'Describes the aggregation function in detail.';
COMMENT ON COLUMN aggregation_function.aggregation_function_expression IS
    'Contains the arithmetic expression of the aggregation function encoded in CobADQs custom constraint language.';
COMMENT ON COLUMN aggregation_function.source_level_of_data_granularity IS
    'References the level of data granularity of the data which will be aggregated.';
COMMENT ON COLUMN aggregation_function.target_level_of_data_granularity IS
    'References the level of data granularity the aggregation result refers to.';



CREATE TABLE IF NOT EXISTS aggregation_process
(
    aggregation_process_name        TEXT
        CONSTRAINT aggregation_process_pk PRIMARY KEY,
    aggregation_process_description TEXT,
    aggregation_query_for_values    TEXT
);
COMMENT ON TABLE aggregation_process IS 'Stores a reference to the values that are aggregated. '
    'The table has relationships to aggregation functions and constraints that aggregate this values.';
COMMENT ON COLUMN aggregation_process.aggregation_process_name IS
    'The name of an aggregation process. '
        'This column is the primary key of the table "aggregation process".';
COMMENT ON COLUMN aggregation_process.aggregation_process_description IS
    'Describes the aggregation process in detail.';
COMMENT ON COLUMN aggregation_process.aggregation_query_for_values IS
    'A SQL query that returns the values which are aggregated by this aggregation process.';



CREATE TABLE IF NOT EXISTS aggregation_process_is_based_on
(
    aggregation_process_name    TEXT REFERENCES aggregation_process (aggregation_process_name)       NOT NULL,
    aggregation_constraint_name TEXT REFERENCES aggregation_constraint (aggregation_constraint_name) NOT NULL,
    aggregation_function_name   TEXT REFERENCES aggregation_function (aggregation_function_name)     NOT NULL,
    CONSTRAINT aggregation_is_based_on_pk PRIMARY KEY (aggregation_process_name, aggregation_constraint_name)
);
COMMENT ON TABLE aggregation_process_is_based_on IS 'Stores the references to the aggregation functions and '
    'constraints used by an aggregation process.';
COMMENT ON COLUMN aggregation_process_is_based_on.aggregation_process_name IS
    'References the aggregation process that is based on a pair of constraints and aggregation functions. '
        'Part of the primary key of the table "aggregation process is based on".';
COMMENT ON COLUMN aggregation_process_is_based_on.aggregation_constraint_name IS
    'References an aggregation constraint '
        'that implies the usage of a certain aggregation function in the aggregation process. '
        'Part of the primary key of the table "aggregation process is based on".';
COMMENT ON COLUMN aggregation_process_is_based_on.aggregation_function_name IS
    'References the aggregation function '
        'that is used in the aggregation process when the referenced constraint is fulfilled. ';

CREATE TABLE IF NOT EXISTS aggregation_process_computes_value_for_dimension
(
    aggregation_process_name TEXT REFERENCES aggregation_process (aggregation_process_name),
    dimension_name           TEXT REFERENCES dq_dimension (dimension_name),
    CONSTRAINT aggregation_process_computes_value_for_dimension_pk PRIMARY KEY (aggregation_process_name, dimension_name)
);
COMMENT ON TABLE aggregation_process_computes_value_for_dimension IS 'Stores information on which aggregation process '
    'computes values for which dimension.';
COMMENT ON COLUMN aggregation_process_computes_value_for_dimension.aggregation_process_name IS
    'The name of the aggregation process that computes a value for the provided dimension ';
COMMENT ON COLUMN aggregation_process_computes_value_for_dimension.dimension_name IS
    'The name of a data quality dimension. ';

CREATE TABLE IF NOT EXISTS data_element
(
    data_element_global_identifier        TEXT PRIMARY KEY,
    data_element_local_identifier         TEXT,
    is_of_level_of_data_granularity       TEXT REFERENCES levels_of_data_granularity (level_name) NOT NULL,
    parent_data_element_global_identifier TEXT REFERENCES data_element (data_element_global_identifier) ON DELETE CASCADE
);
COMMENT ON TABLE data_element IS 'Stores representations of data elements, i.e., whole databases, tables, columns, ...';
COMMENT ON COLUMN data_element.data_element_global_identifier IS
    'Globally identifies a data element. '
        'The global global_identifier consists either of a filepath or a database connection string. '
        'In case it is the global_identifier of a column, '
        'the columns global_identifier appended to the filepath or database connection string after a slash. '
        'In case, a value or a row are identified, '
        'the identifying values of a row are listed after a hashtag in a CSV like list.';
COMMENT ON COLUMN data_element.data_element_local_identifier IS 'Locally identifies a data element.'
    'E.g., the name of a database, a table, a column or the key of a row in a CSV-like structure.';
COMMENT ON COLUMN data_element.is_of_level_of_data_granularity IS
    'The level of data granularity of the data element.';
COMMENT ON COLUMN data_element.parent_data_element_global_identifier IS
    'The global global_identifier of the more coarse-granular data element that contains '
        'this more fine-granular data element.';

CREATE TABLE dq_result
(
    creation_timestamp                 TIMESTAMP NOT NULL,
    result_value                       NUMERIC   NOT NULL,
    computed_on_data_element_global_id TEXT      NOT NULL
        REFERENCES data_element (data_element_global_identifier) ON DELETE CASCADE,
    calculated_by_dq_metric            TEXT REFERENCES dq_metric (metric_name),
    calculated_by_aggregation_process  TEXT REFERENCES aggregation_process (aggregation_process_name),
    CONSTRAINT calculated_by_dq_metric_xor_aggregation_process CHECK (
        (calculated_by_dq_metric IS NOT NULL AND calculated_by_aggregation_process IS NULL) OR
        (calculated_by_dq_metric IS NULL AND calculated_by_aggregation_process IS NOT NULL)),
    UNIQUE (creation_timestamp, computed_on_data_element_global_id, calculated_by_dq_metric)
);
COMMENT ON TABLE dq_result IS 'Stores DQ results computed on a data element either by a DQ metric or'
    ' an aggregation process.';
COMMENT ON COLUMN dq_result.creation_timestamp IS
    'The timestamp of the point in time when the data quality results has been computed.'
        'Part of the tables uniqueness constraint.';
COMMENT ON COLUMN dq_result.result_value IS
    'The data quality result value that has been computed.';
COMMENT ON COLUMN dq_result.computed_on_data_element_global_id IS
    'References the data element for which the data quality result value that has been computed.'
        'Part of the tables uniqueness constraint.';
COMMENT ON COLUMN dq_result.calculated_by_dq_metric IS
    'References the data quality metric that computed the result value.'
        'Part of the tables uniqueness constraint.';
COMMENT ON COLUMN dq_result.calculated_by_aggregation_process IS
    'References the data quality aggregation process that computed the result value.'
        'Part of the tables uniqueness constraint.';


END TRANSACTION;