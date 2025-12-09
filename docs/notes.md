# Notes

## Data Lakehouse Delta Lake

Traditional data warehouse:
- Long ETL
- Can't process real-time
- Only structured data

Data lake:
- File based format
- Structured
- Unstructured
- Semi structured data

Data lake limitations:
- Difficult to enforce data governance
- Data quality issues
- Data duplication
- Difficult to find data

Data Lakehouse:
- Like a data-lake: can process structured and unstructured data, file based structure
- Like a data-lake: supports ML use cases
- Like a data warehouse: Process queries in a fast optimized way
- Data lineage

## Databricks Lakehouse architecture

Storage:
- DBFS, S3, Azure
- Delta table (parquet)
- SQL engine

Software:
- Delta lake: open source build on Apache Spark
- Performance optimization
- ACID transaction support (transaction log)

Delta Lake:
- Delta files (parquet)
- Delta tables (parquet + logs)
- Delta storage (keeps data in object storage, structure and unstructured)
- Delta engine: optimized query engine

Delta table:
- Parquet files
- Delta log
- Provides table-like representation (for SQL and Spark)
- ACID transaction support
- S3 / blob integration
- Time travel to previous version and restore

## Databrics SQL vs. Spark SQL

- Spark SQL: can be used in any Spark environment
- Databricks SQL:
  - Optimized SQL engine optimized for Databricks
  - Additional commands not available in Spark SQL
  - recommended for operating on delta tables (10x speedup!)

## Datatable caching

- Delta Table Caching provided by Delta Engine
- 2x speedup

## Delta table partitioning

- Partition on categorical columns
- Optimize for frequent queries (columns frequently used in `WHERE` clauses)

## Z-Ordering

- Specify set of columns that the data should be sorted by
- Z-ordering works particularly well for range-based queries (e.g. date ranges, amounts)