"""Dagster project configuration for dbt integration."""

from pathlib import Path

from dagster_dbt import DbtProject

# Absolute path to the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Absolute path to the dbt directory
DBT_DIR = PROJECT_ROOT / "dbt"

# Absolute path to the airbnb dbt project
DBT_AIRBNB_DIR = DBT_DIR / "airbnb"

# Path for packaged dbt project (used in production deployments)
DBT_PACKAGED_DIR = PROJECT_ROOT / "dbt-project"

airbnb_project = DbtProject(
    project_dir=DBT_AIRBNB_DIR,
    packaged_project_dir=DBT_PACKAGED_DIR,
)
airbnb_project.prepare_if_dev()