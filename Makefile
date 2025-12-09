.PHONY: build up down logs shell sync clean prune download-datasets

# Enable Docker Compose bake for better build performance
export COMPOSE_BAKE=true

# Build the Docker image
build:
	docker compose build

# Start the Spark/Jupyter container
up:
	docker compose up -d
	@echo "Jupyter available at http://localhost:8888"
	@echo "Spark UI at http://localhost:4040 (when job running)"

# Stop the container
down:
	docker compose down

# View container logs
logs:
	docker compose logs -f

# Open a shell in the running container
shell:
	docker exec -it data-engineering-bootcamp /bin/bash

# Open PySpark shell in the container
pyspark:
	docker exec -it data-engineering-bootcamp pyspark

# Sync local virtualenv (for IDE support)
sync:
	uv sync

# Clean up containers and volumes
clean:
	docker compose down -v

# Full prune (removes image too)
prune: clean
	docker rmi data-engineering-bootcamp:latest 2>/dev/null || true

# Download Databricks sample datasets
download-datasets:
	uv run python scripts/download_datasets.py

# First-time setup
setup: sync download-datasets build up
	@echo "Setup complete!"
