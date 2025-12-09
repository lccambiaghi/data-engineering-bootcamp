#!/bin/bash
# Load Airbnb CSV data into PostgreSQL
# This script runs after 01_create_schemas.sql

DATA_DIR="/docker-entrypoint-initdb.d/data"

echo "=================================================="
echo "Loading Airbnb course data into PostgreSQL..."
echo "=================================================="

# Load listings
if [ -f "$DATA_DIR/listings.csv" ]; then
    echo "Loading listings..."
    psql -U dbt -d airbnb -c "\COPY raw.listings FROM '$DATA_DIR/listings.csv' WITH CSV HEADER;"
    COUNT=$(psql -U dbt -d airbnb -t -c "SELECT COUNT(*) FROM raw.listings;")
    echo "✓ Loaded $COUNT listings"
else
    echo "⚠ listings.csv not found"
fi

# Load hosts
if [ -f "$DATA_DIR/hosts.csv" ]; then
    echo "Loading hosts..."
    psql -U dbt -d airbnb -c "\COPY raw.hosts FROM '$DATA_DIR/hosts.csv' WITH CSV HEADER;"
    COUNT=$(psql -U dbt -d airbnb -t -c "SELECT COUNT(*) FROM raw.hosts;")
    echo "✓ Loaded $COUNT hosts"
else
    echo "⚠ hosts.csv not found"
fi

# Load reviews
if [ -f "$DATA_DIR/reviews.csv" ]; then
    echo "Loading reviews..."
    psql -U dbt -d airbnb -c "\COPY raw.reviews FROM '$DATA_DIR/reviews.csv' WITH CSV HEADER;"
    COUNT=$(psql -U dbt -d airbnb -t -c "SELECT COUNT(*) FROM raw.reviews;")
    echo "✓ Loaded $COUNT reviews"
else
    echo "⚠ reviews.csv not found"
fi

echo "=================================================="
echo "Data loading complete!"
echo ""
echo "Run: python scripts/download_airbnb_data.py"
echo "if data files are missing."
echo "=================================================="
