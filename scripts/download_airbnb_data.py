#!/usr/bin/env python3
"""
Download Airbnb data for the dbt bootcamp course.

This script downloads the exact datasets used in the Udemy course:
https://github.com/nordquant/complete-dbt-bootcamp-zero-to-hero

Source: https://github.com/nordquant/complete-dbt-bootcamp-zero-to-hero/blob/main/_course_resources/source-data-locations.md

Usage:
    python scripts/download_airbnb_data.py
"""

import urllib.request
import os
from pathlib import Path

# Course datasets from S3
# Source: https://github.com/nordquant/complete-dbt-bootcamp-zero-to-hero/blob/main/_course_resources/source-data-locations.md
DATASETS = {
    "listings": "https://dbt-datasets.s3.amazonaws.com/listings.csv",
    "reviews": "https://dbt-datasets.s3.amazonaws.com/reviews.csv",
    "hosts": "https://dbt-datasets.s3.amazonaws.com/hosts.csv",
}


def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from URL to destination path."""
    print(f"  Downloading: {url}")
    try:
        urllib.request.urlretrieve(url, dest_path)
        # Get file size
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Saved: {dest_path.name} ({size_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"  ✗ Error downloading {url}: {e}")
        return False


def main():
    print(f"\n{'='*60}")
    print("Downloading Airbnb Course Datasets")
    print("Source: dbt-datasets.s3.amazonaws.com")
    print("Course: Complete dbt Bootcamp (Udemy)")
    print(f"{'='*60}\n")
    
    # Determine output directory
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / "bootcamp" / "dbt" / "init" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Output directory: {output_dir}\n")
    
    success_count = 0
    
    # Download each dataset
    for name, url in DATASETS.items():
        csv_path = output_dir / f"{name}.csv"
        if download_file(url, csv_path):
            success_count += 1
        print()
    
    print(f"{'='*60}")
    print(f"Download complete! ({success_count}/{len(DATASETS)} files)")
    print(f"\nNext steps:")
    print("1. Start the database: docker-compose up dbt-db -d")
    print("2. Install dbt-postgres: pip install dbt-postgres")
    print("3. Navigate to dbt project: cd bootcamp/dbt/airbnb")
    print("4. Run dbt: dbt debug --profiles-dir ..")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
