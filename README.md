# Data Engineering Bootcamp

A hands-on learning environment for Apache Spark, Delta Lake, and data engineering fundamentals.

## Features

- **PySpark** with Delta Lake support
- **Databricks-compatible utilities** (`display`, `dbutils`) for local development
- **Jupyter notebooks** with curated exercises
- **Sample datasets** including the Databricks datasets collection

## Quick Start

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

## Usage

### Makefile Commands

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

### In Notebooks

```python
from bootcamp import display, dbutils, spark

# Use spark, display(), and dbutils just like in Databricks
df = spark.read.csv("/databricks-datasets/samples/people.csv", header=True)
display(df)
```

## Project Structure

```
├── bootcamp/           # Python package with Databricks compat layer
├── data/               # Local datasets (gitignored)
├── notebooks/          # Jupyter notebooks
├── scripts/            # Utility scripts
├── Dockerfile          # Spark + Jupyter environment
├── docker-compose.yml  # Container orchestration
└── Makefile            # Development commands
```

## License

MIT

