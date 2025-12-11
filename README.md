# Data Engineering Bootcamp

A hands-on learning environment for Apache Spark, Delta Lake, dbt, and modern data engineering — running entirely on your local machine with Docker.

## 📚 Based On

This repository follows along with two Udemy courses, adapting the exercises to run locally without cloud dependencies:

| Course | Original Stack | This Repo |
|--------|---------------|-----------|
| [Data Engineering with Spark, Databricks & Delta Lake](https://www.udemy.com/course/data-engineering-with-spark-databricks-delta-lake-lakehouse/) | Databricks, DBFS, Azure/AWS | **Docker + Spark + Hive Metastore** |
| [Complete dbt Bootcamp: Zero to Hero](https://www.udemy.com/course/complete-dbt-data-build-tool-bootcamp-zero-to-hero-learn-dbt) | Snowflake | **DuckDB** |

## ✨ Key Features

### 🐳 Fully Local Docker Setup (No Cloud Required)

Instead of Databricks or cloud services, this repo provides:

- **Apache Spark 3.5** with Delta Lake support in Docker
- **Hive Metastore** backed by PostgreSQL for table catalog persistence
- **Jupyter notebooks** for interactive development
- **Databricks-compatible utilities** (`display`, `dbutils`, `spark`) for seamless code portability

### 🦆 DuckDB Instead of Snowflake

The dbt project uses **DuckDB** as the data warehouse:

- Zero infrastructure — just a local file (`airbnb.duckdb`)
- Blazing fast analytics on modest hardware
- Delta Lake plugin for reading Delta tables as sources
- Perfect for development and learning

### 🔧 Modern Data Stack

- **dbt** with full project structure (models, tests, seeds, snapshots, docs)
- **Dagster** orchestration for dbt assets with partition-aware scheduling
- **dbt Fusion** compatible (Rust-based dbt engine)

## 🚀 Quick Start

### Spark + Delta Lake

```bash
# First-time setup
make setup

# Or step by step:
make sync              # Install Python dependencies locally
make download-datasets # Download sample datasets
make build             # Build Docker image
make up                # Start Jupyter + Spark
```

Then open http://localhost:8888 in your browser.

### dbt with DuckDB

```bash
cd dbt/airbnb

# Validate setup
dbt debug

# Run models
dbt run

# Run tests
dbt test

# Generate and serve docs
dbt docs generate
dbt docs serve
```

### Dagster Orchestration

```bash
uv run dagster dev
```

Open http://127.0.0.1:3000 for the Dagster UI.

## 📁 Project Structure

```
├── bootcamp/              # Python package with Databricks compat layer
│   ├── databricks_compat.py  # display(), dbutils, spark session
│
├── notebooks/             # Jupyter notebooks (Spark + Delta Lake course)
│   ├── 01-spark-basics.ipynb
│   ├── 02-spark_write_save.ipynb
│   ├── ...
│   └── 10-delta_table_zordering.ipynb
│
├── dbt/
│   ├── airbnb/            # dbt project (dbt course)
│   │   ├── models/        # src → dim → fct → mart layers
│   │   ├── seeds/         # CSV files (full moon dates)
│   │   ├── snapshots/     # SCD Type 2 snapshots
│   │   ├── tests/         # Custom generic tests
│   │   └── analyses/      # Ad-hoc SQL analyses
│   └── init/              # Data loading scripts
│
├── dagster_airbnb/        # Dagster orchestration for dbt
│
├── data/                  # Local datasets (gitignored)
│   ├── databricks-datasets/   # Sample datasets
│   └── spark-warehouse/       # Delta tables
│
├── docs/                  # Course notes
│   ├── 1-delta-tables-notes.md
│   └── 2-dbt-notes.md
│
├── docker-compose.yml     # Spark + Hive Metastore + pgAdmin
├── Dockerfile             # Spark + Jupyter environment
└── Makefile               # Development commands
```

## 🛠️ Makefile Commands

| Command | Description |
|---------|-------------|
| `make build` | Build the Docker image |
| `make up` | Start Jupyter/Spark container |
| `make down` | Stop the container |
| `make shell` | Open bash in container |
| `make pyspark` | Open PySpark REPL |
| `make logs` | View container logs |
| `make clean` | Remove containers and volumes |
| `make prune` | Full cleanup including image |

## 📓 Course Content

### Part 1: Spark + Delta Lake

The `notebooks/` folder contains exercises covering:

- Spark basics and transformations
- Reading and writing data (CSV, Parquet, Delta)
- UDFs and Python transformations
- Joins and SQL operations
- Delta table features (caching, partitioning, Z-ordering)
- Time travel and table versioning

### Part 2: dbt Fundamentals

The `dbt/airbnb/` project demonstrates:

- **Models**: Source → Staging → Dimensions → Facts → Marts
- **Materializations**: Views, tables, incremental, ephemeral
- **Testing**: Generic tests, singular tests, custom generic tests
- **Documentation**: Auto-generated docs with lineage graphs
- **Sources & Seeds**: External data integration
- **Snapshots**: SCD Type 2 for slowly changing dimensions
- **Hooks**: Pre/post-run SQL for audit logging
- **Packages**: dbt_utils and other community packages
