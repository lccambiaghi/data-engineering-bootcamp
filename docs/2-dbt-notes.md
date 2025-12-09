# DBT Notes

## Features

- Tests: data quality checks
- Documentation: lineage graphs for pipelines
- Extensions: column-level lineage
- Modular & reusable code

## Local Setup (PostgreSQL instead of Snowflake)

Project structure:
```
dbt/
├── airbnb/               # The dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml      # Connection config
│   ├── models/
│   ├── seeds/
│   └── ...
└── init/                 # PostgreSQL init scripts
    └── data/             # CSV source files
```

### Running dbt commands

Run from inside the project folder:
```bash
cd dbt/airbnb
dbt debug
dbt run
```

## Models

Each model will be a view.

### Organize in stages

- src: staging layer
- core layer:
  - Dimensions (cleansing)
  - Facts (incremental)

### Running

To create the views, `cd` into `dbt/airbnb` and run `dbt run`

## Materialisations

- View: 
  - very lightweight
  - use if you don't reuse data too often
- Table: 
  - You read from this model repeatedly
- Incremental (table appends):
  - fact tables; appends to tables
- Ephemeral: you want an alias (will not be in the data warehouse)