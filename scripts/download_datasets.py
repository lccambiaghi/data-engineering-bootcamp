#!/usr/bin/env python3
"""
Download popular Databricks datasets for local development.

These datasets mirror what's available at dbfs:/databricks-datasets/
"""

import urllib.request
import zipfile
import tarfile
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "data" / "databricks-datasets"

DATASETS = {
    # R datasets (from CRAN) - includes Titanic, iris, mtcars, etc.
    "Rdatasets": {
        "url": "https://github.com/vincentarelbundock/Rdatasets/archive/refs/heads/master.zip",
        "type": "zip",
        "extract_subdir": "Rdatasets-master",
        "rename_to": "Rdatasets",
    },
    # Wine quality dataset (GitHub mirror)
    "wine-quality": {
        "files": [
            {
                "url": "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/flight-data/csv/2015-summary.csv",
                "name": "flights-2015-summary.csv",
            },
        ],
    },
    # Iris dataset (from Rdatasets - already in Rdatasets/csv/datasets/)
    # Skipping since it's already available
    # Adult/Census income dataset (GitHub mirror)
    "adult": {
        "files": [
            {
                "url": "https://raw.githubusercontent.com/jbrownlee/Datasets/master/adult-all.csv",
                "name": "adult.csv",
            },
        ],
    },
    # Sample data (creating simple examples)
    "samples": {
        "create": True,
    },
}


def download_file(url: str, dest: Path) -> None:
    """Download a file with progress indication."""
    print(f"  Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"  ✓ Saved to {dest}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")


def extract_zip(zip_path: Path, extract_to: Path, subdir: str | None = None) -> None:
    """Extract a zip file."""
    print(f"  Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    zip_path.unlink()  # Remove zip after extraction
    print(f"  ✓ Extracted to {extract_to}")


def create_sample_data(dest: Path) -> None:
    """Create sample datasets similar to Databricks samples."""
    dest.mkdir(parents=True, exist_ok=True)

    # Sample people data
    people_data = """name,age,city
Alice,30,New York
Bob,25,San Francisco
Charlie,35,Chicago
Diana,28,Seattle
Eve,32,Boston"""

    (dest / "people.csv").write_text(people_data)
    print(f"  ✓ Created {dest / 'people.csv'}")

    # Sample sales data
    sales_data = """date,product,quantity,price
2024-01-01,Widget A,10,29.99
2024-01-01,Widget B,5,49.99
2024-01-02,Widget A,8,29.99
2024-01-02,Widget C,12,19.99
2024-01-03,Widget B,3,49.99"""

    (dest / "sales.csv").write_text(sales_data)
    print(f"  ✓ Created {dest / 'sales.csv'}")


def download_dataset(name: str, config: dict) -> None:
    """Download and set up a single dataset."""
    print(f"\n📦 {name}")
    dest = BASE_DIR / name

    if dest.exists() and any(dest.iterdir()):
        print(f"  ⏭ Already exists, skipping")
        return

    if "create" in config:
        dest.mkdir(parents=True, exist_ok=True)
        create_sample_data(dest)
        return

    if "files" in config:
        dest.mkdir(parents=True, exist_ok=True)
        for file_info in config["files"]:
            download_file(file_info["url"], dest / file_info["name"])
        return

    if "url" in config:
        # Download archive
        suffix = ".zip" if config["type"] == "zip" else ".tar.gz"
        archive_path = dest.parent / f"{name}{suffix}"
        download_file(config["url"], archive_path)

        # Extract
        if config["type"] == "zip":
            extract_zip(archive_path, dest.parent)

        # Rename if needed
        if "extract_subdir" in config and "rename_to" in config:
            extracted = dest.parent / config["extract_subdir"]
            target = dest.parent / config["rename_to"]
            # Remove empty target dir if it exists
            if target.exists() and not any(target.iterdir()):
                target.rmdir()
            if extracted.exists() and not target.exists():
                extracted.rename(target)
                print(f"  ✓ Renamed to {target}")


def main():
    print("=" * 50)
    print("Databricks Datasets Downloader")
    print("=" * 50)
    print(f"Download location: {BASE_DIR}")

    BASE_DIR.mkdir(parents=True, exist_ok=True)

    for name, config in DATASETS.items():
        try:
            download_dataset(name, config)
        except Exception as e:
            print(f"  ✗ Error downloading {name}: {e}")

    print("\n" + "=" * 50)
    print("✅ Done! Datasets available at:")
    print(f"   Local:  ./data/databricks-datasets/")
    print(f"   Spark:  /databricks-datasets/ (via dbutils)")
    print("=" * 50)


if __name__ == "__main__":
    main()

