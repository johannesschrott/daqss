The database part of DaQSS is realized using the DBMS [PostgreSQL](https://www.postgresql.org/).
PostgreSQL has been chosen since it is a popular, relational open-source DBMS (cf.
the [DB-Engines.com ranking](https://db-engines.com/en/ranking)).
On this page, the conceptual model is introduced at first
and as second a reference to the documentation of the relational database resulting from that model is provided.

## Conceptual Model

<img src="../../images/conceptual_model.svg" width=100%>

## Database Implementation

The conceptual model is realized in PostgreSQL in the form of 11 tables.
A documentation of the database implementation, which has been generated using the
tool [SchemaSpy](https://schemaspy.org/),
can be found under <https://johannes.schrott.onl/daqss/database_docs>.

*[DBMS]: database management system
*[UML]: Unified Modeling Language