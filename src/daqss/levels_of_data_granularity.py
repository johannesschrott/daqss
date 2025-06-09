from collections import namedtuple

LevelOfDataGranularity = namedtuple("LevelOfDataGranularity", ["name", "ordering"])
"""A [named tuple][collections.namedtuple] 
that contains the `name` and the `ordering` of a level of data granularity."""

VALUE = LevelOfDataGranularity("value", 0)
"""An instance of the named tuple LevelOfDataGranularity. Covers a single data value."""

ROW = LevelOfDataGranularity("row", 1)
"""An instance of the named tuple LevelOfDataGranularity. Covers a row (a record) of data values."""

COLUMN = LevelOfDataGranularity("column", 1)
"""An instance of the named tuple LevelOfDataGranularity.
 Covers column of data values, i.e. one attribute of data values."""

TABLE = LevelOfDataGranularity("table", 2)
"""An instance of the named tuple LevelOfDataGranularity. Covers all data values contained in a table (a relation)."""

DATABASE = LevelOfDataGranularity("database", 3)
"""An instance of the named tuple LevelOfDataGranularity. Covers all data values contained in a database."""

SYSTEM = LevelOfDataGranularity("system", 4)
"""An instance of the named tuple LevelOfDataGranularity. 
Covers all data values contained in a system, e.g., a system that integrates multiple databases."""
