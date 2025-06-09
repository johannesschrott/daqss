# DaQSS

Many data-driven tasks require high-quality data to produce meaningful results.
While data quality information can be computed on an ad-hoc basis when needed, a storage system is beneficial for
analysis and for the providing of provenance information on data quality results.
The idea of a data quality storage system is not new.
However, existing developments are based on different types of data models but not solely on the relational data model,
which is the most popular.
As consequence,
this work contributes a new **Da**ta
**Q**uality
**S**torage
**S**ystem,
called DaQSS, which is solely based on the relational data model.
The new system allows to store values resulting from
data quality measurements and aggregations and their associated metadata.
Thus, the system provides provenance information on how data quality results have been computed.
In addition to the concept, a proof-of-concept implementation is provided to demonstrate the practical applicability of
the system.

DaQSS consists of two parts: a database implementation, which is realized using the
database management system [PostgreSQL](https://www.postgresql.org), and a Python package, which enables an easy
integration of scripts with the database.

This documentation is split into three parts:

- The page ["Set up DaQSS"](set-up.md) describes the steps that need to be taken in order to install and use DaQSS.
- The section ["Demonstration"](demo.md) contains three examples of how DaQSS can be used.
- The section ["Technical Documentation"](technical/environment_variables.md) provides background information on both
  parts of DaQSS, the database implementation and the Python package.