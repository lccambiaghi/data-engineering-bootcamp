"""
Databricks compatibility layer for local Spark development.

Usage in notebooks:
    from bootcamp.databricks_compat import display, dbutils, spark
    from data.config import DATA_DIR

This provides:
    - display(): Renders DataFrames as HTML tables in Jupyter
    - dbutils: Mock with fs.ls() and other common utilities
    - spark: Pre-configured SparkSession with Delta Lake
    - %sql / %%sql: Cell magic for SQL queries (auto-registered on import)
"""

from pathlib import Path
from typing import Any, Optional

from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.display import HTML, display as ipy_display
from pyspark.sql import DataFrame, SparkSession


def init_spark(app_name: str = "LearnSpark") -> SparkSession:
    """Initialize a SparkSession with Delta Lake support and shared metastore."""
    # Use same warehouse path as Hive Metastore (both containers mount same volume here)
    warehouse_dir = "/opt/hive/data/warehouse"
    
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.warehouse.dir", warehouse_dir)
        # Connect to Hive Metastore Service via Thrift (shared across all notebooks)
        .config("spark.hadoop.hive.metastore.uris", "thrift://hive-metastore:9083")
        .enableHiveSupport()
        .getOrCreate()
    )


# Pre-initialized spark session (lazy)
_spark: Optional[SparkSession] = None


def get_spark() -> SparkSession:
    """Get or create the SparkSession."""
    global _spark
    if _spark is None:
        _spark = init_spark()
    return _spark


# Make spark available as a module-level variable
class _SparkProxy:
    """Lazy proxy for SparkSession to avoid initialization on import."""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_spark(), name)

    def __repr__(self) -> str:
        return repr(get_spark())


spark = _SparkProxy()


def display(
    df: DataFrame,
    limit: int = 20,
    truncate: bool = True,
    max_col_width: int = 50,
) -> None:
    """
    Display a DataFrame as an HTML table (Databricks-style).

    Args:
        df: PySpark DataFrame to display
        limit: Maximum number of rows to show (default: 20)
        truncate: Whether to truncate long strings (default: True)
        max_col_width: Maximum column width when truncating (default: 50)
    """
    if not isinstance(df, DataFrame):
        # Fall back to IPython display for non-DataFrames
        ipy_display(df)
        return

    # Convert to Pandas for HTML rendering
    pdf = df.limit(limit).toPandas()

    # Truncate long strings if requested
    if truncate:
        for col in pdf.select_dtypes(include=["object"]).columns:
            pdf[col] = pdf[col].apply(
                lambda x: (str(x)[:max_col_width] + "...") 
                if isinstance(x, str) and len(str(x)) > max_col_width 
                else x
            )

    # Style the table
    styled_html = f"""
    <style>
        .spark-table {{ 
            border-collapse: collapse; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
        }}
        .spark-table th {{ 
            background-color: #f5f5f5; 
            border: 1px solid #ddd; 
            padding: 8px 12px;
            text-align: left;
            font-weight: 600;
        }}
        .spark-table td {{ 
            border: 1px solid #ddd; 
            padding: 8px 12px;
        }}
        .spark-table tr:nth-child(even) {{ background-color: #fafafa; }}
        .spark-table tr:hover {{ background-color: #f0f0f0; }}
        .spark-info {{ 
            color: #666; 
            font-size: 12px; 
            margin-top: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
    </style>
    <table class="spark-table">
        <thead>
            <tr>{''.join(f'<th>{col}</th>' for col in pdf.columns)}</tr>
        </thead>
        <tbody>
            {''.join(
                '<tr>' + ''.join(f'<td>{val}</td>' for val in row) + '</tr>'
                for row in pdf.values
            )}
        </tbody>
    </table>
    <div class="spark-info">Showing {len(pdf)} of {df.count()} rows</div>
    """

    ipy_display(HTML(styled_html))


class _DbUtilsFs:
    """Mock of dbutils.fs for local filesystem operations."""

    def __init__(self, base_path: str = "/home/jovyan/work/data"):
        self.base_path = base_path

    def _resolve_path(self, path: str) -> Path:
        """Resolve dbfs:/ paths to local paths."""
        # Strip dbfs: prefix
        if path.startswith("dbfs:"):
            path = path[5:]
        # Handle absolute paths starting with /
        if path.startswith("/"):
            # Map /databricks-datasets to local data/databricks-datasets folder
            if path.startswith("/databricks-datasets"):
                local_datasets = Path(self.base_path) / "databricks-datasets"
                if not local_datasets.exists():
                    print(f"⚠️  /databricks-datasets not downloaded yet.")
                    print(f"   Run: make download-datasets")
                # Keep the path structure: /databricks-datasets/X -> data/databricks-datasets/X
                return Path(self.base_path) / path.lstrip("/")
            # Map /user/hive/warehouse to Hive warehouse folder (shared volume)
            if path.startswith("/user/hive/warehouse"):
                remainder = path[len("/user/hive/warehouse"):].lstrip("/")
                return Path("/opt/hive/data/warehouse") / remainder
            return Path(self.base_path).parent / path.lstrip("/")
        return Path(self.base_path) / path

    def ls(self, path: str) -> list:
        """
        List files in a directory (like dbutils.fs.ls).

        Returns list of FileInfo objects with: path, name, size, modificationTime
        """
        resolved = self._resolve_path(path)

        if not resolved.exists():
            raise FileNotFoundError(f"Path does not exist: {resolved}")

        results = []
        for item in sorted(resolved.iterdir()):
            stat = item.stat()
            info = {
                "path": f"dbfs:{item}",
                "name": item.name + ("/" if item.is_dir() else ""),
                "size": stat.st_size if item.is_file() else 0,
                "modificationTime": int(stat.st_mtime * 1000),
            }
            results.append(type("FileInfo", (), info)())

        return results

    def head(self, path: str, max_bytes: int = 65536) -> str:
        """Read the first bytes of a file."""
        resolved = self._resolve_path(path)
        with open(resolved, "rb") as f:
            return f.read(max_bytes).decode("utf-8", errors="replace")

    def mkdirs(self, path: str) -> bool:
        """Create directories."""
        resolved = self._resolve_path(path)
        resolved.mkdir(parents=True, exist_ok=True)
        return True

    def rm(self, path: str, recurse: bool = False) -> bool:
        """Remove a file or directory."""
        import shutil
        resolved = self._resolve_path(path)
        if resolved.is_dir() and recurse:
            shutil.rmtree(resolved)
        else:
            resolved.unlink()
        return True


class _DbUtils:
    """Mock of Databricks dbutils."""

    def __init__(self):
        self.fs = _DbUtilsFs()

    def help(self) -> None:
        """Show available utilities."""
        print("dbutils (local mock)")
        print("=" * 40)
        print("Available utilities:")
        print("  dbutils.fs       - File system utilities")
        print("")
        print("dbutils.fs methods:")
        print("  ls(path)         - List directory contents")
        print("  head(path)       - Read first bytes of file")
        print("  mkdirs(path)     - Create directories")
        print("  rm(path)         - Remove file/directory")
        print("")
        print("Note: This is a local mock. Some Databricks")
        print("features may not be available.")


dbutils = _DbUtils()


# =============================================================================
# SQL Magic Support
# =============================================================================

@magics_class
class SparkSQLMagic(Magics):
    """
    IPython magic for executing Spark SQL queries.
    
    Usage:
        %sql SELECT * FROM table LIMIT 10
        
        %%sql
        SELECT *
        FROM table
        WHERE condition
        LIMIT 10
    """

    @line_magic
    def sql(self, line: str) -> None:
        """Execute a single-line SQL query."""
        self._execute_sql(line)

    @cell_magic
    def sql(self, line: str, cell: str) -> None:  # noqa: F811
        """Execute a multi-line SQL query."""
        # Combine line and cell content (line may have options in the future)
        query = cell.strip()
        self._execute_sql(query)

    def _execute_sql(self, query: str) -> None:
        """Execute SQL query and display results."""
        if not query.strip():
            print("Empty SQL query")
            return
        
        try:
            spark_session = get_spark()
            result_df = spark_session.sql(query)
            display(result_df)
        except Exception as e:
            print(f"SQL Error: {e}")


def _display_file_info(file_infos: list) -> None:
    """Display FileInfo results as an HTML table (Databricks-style)."""
    if not file_infos:
        print("(empty directory)")
        return

    # Build HTML table matching Databricks style
    rows_html = ""
    for info in file_infos:
        rows_html += f"""
            <tr>
                <td>{info.path}</td>
                <td>{info.name}</td>
                <td>{info.size}</td>
                <td>{info.modificationTime}</td>
            </tr>"""

    styled_html = f"""
    <style>
        .fs-table {{ 
            border-collapse: collapse; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
        }}
        .fs-table th {{ 
            background-color: #f5f5f5; 
            border: 1px solid #ddd; 
            padding: 8px 12px;
            text-align: left;
            font-weight: 600;
        }}
        .fs-table td {{ 
            border: 1px solid #ddd; 
            padding: 8px 12px;
        }}
        .fs-table tr:nth-child(even) {{ background-color: #fafafa; }}
        .fs-table tr:hover {{ background-color: #f0f0f0; }}
    </style>
    <table class="fs-table">
        <thead>
            <tr>
                <th>path</th>
                <th>name</th>
                <th>size</th>
                <th>modificationTime</th>
            </tr>
        </thead>
        <tbody>{rows_html}
        </tbody>
    </table>
    """
    ipy_display(HTML(styled_html))


@magics_class
class DbFsMagic(Magics):
    """
    IPython magic for Databricks filesystem operations.
    
    Usage:
        %fs ls /path/to/dir
        %fs head /path/to/file
    """

    @line_magic
    def fs(self, line: str) -> None:
        """Execute a filesystem command."""
        parts = line.strip().split(None, 1)
        if not parts:
            print("Usage: %fs <command> [path]")
            print("Commands: ls, head, mkdirs, rm")
            return
        
        cmd = parts[0].lower()
        path = parts[1] if len(parts) > 1 else "/"
        
        try:
            if cmd == "ls":
                results = dbutils.fs.ls(path)
                _display_file_info(results)
            elif cmd == "head":
                print(dbutils.fs.head(path))
            elif cmd == "mkdirs":
                dbutils.fs.mkdirs(path)
                print(f"Created: {path}")
            elif cmd == "rm":
                dbutils.fs.rm(path)
                print(f"Removed: {path}")
            else:
                print(f"Unknown command: {cmd}")
                print("Available: ls, head, mkdirs, rm")
        except Exception as e:
            print(f"FS Error: {e}")


def register_magics() -> None:
    """Register all Databricks-compatible magics with IPython."""
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ipython.register_magics(SparkSQLMagic)
            ipython.register_magics(DbFsMagic)
    except (ImportError, AttributeError):
        # Not running in IPython/Jupyter
        pass


# Auto-register magics when module is imported
register_magics()
