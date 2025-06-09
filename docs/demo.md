The demonstration of DaQSS is split into three parts. By doing so, the reuse and provenance aspect of the system can be
highlighted more easily.

- The [first demonstration](demo1.ipynb) covers the computation of DQ result values through a DQ metric.
  For provenance purposes, the metric and the result values are stored in DaQSS.

- The [second demonstration](demo2.ipynb) shows a constraint-based aggregation of DQ result values, the storing
  of the results and the metadata of the aggregation process in DaQSS.

- The [third demonstration](demo3.ipynb) highlights how information that is stored in DaQSS, such as DQ metrics,
  constraint-base aggregation processes, or DQ result values, can be reused.

## Datasets used in the Demonstrations

The demonstrations rely on two different data sets:

* A CSV file containing [fake customer data](https://github.com/johannesschrott/fake_customer_data) with missing values
  is used in the [first](demo1.ipynb) and the [third](demo3.ipynb) demonstration.
* A [SQLite](https://www.sqlite.org/) database created from three files containing information about products on
  Amazon[^1][^2][^3] is used in the [second](demo2.ipynb) demonstration. The database is available for
  download [here](https://johannes.schrott.onl/daqss/demo/product_information.sqlite).
  The original files[^1][^2][^3] are made available under the [ODC Attribution License](https://opendatacommons.org/licenses/by/1-0/index.html).

To generate the SQLite database, the Python package [`csv-to-sqlite`](https://pypi.org/project/csv-to-sqlite/)
has been used in the following Python script:

```python
import csv_to_sqlite

options = csv_to_sqlite.CsvOptions(typing_style="full", encoding="utf-8")
input_files = ["amazon_us_products.csv",
               "amazon_us_categories.csv",
               "amz_ca_total_products_data_processed.csv",
               "amz_in_total_products_data_processed.csv"]
csv_to_sqlite.write_csv(input_files, "product_information.sqlite", options)
```

Following this,
all records with a `listPrice` of `0` have been deleted from all tables of the databases tables and
with a probability of 20%, the values of the column `price` and `listPrice` of a record have been swapped in order to
pollute the database.

[^1]: <https://www.kaggle.com/datasets/asaniczka/amazon-products-dataset-2023-1-4m-products>, last visited on
16-Nov-2024
[^2]: <https://www.kaggle.com/datasets/asaniczka/amazon-canada-products-2023-2-1m-products>, last visited on
16-Nov-2024
[^3]: <https://www.kaggle.com/datasets/asaniczka/amazon-india-products-2023-1-5m-products>, last visited on
16-Nov-2024

*[CSV]: comma-separated values
*[DQ]: data quality
