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

## Running

To create the views / tables, `cd` into `dbt/airbnb` and run `dbt run`

## Materialisations

- View: 
  - Very lightweight, use if you don't reference the models very often
- Table: 
  - You read from this model repeatedly
- Incremental (table appends):
  - fact tables; appends to tables
- Ephemeral:
  - You just want an alias
  - Thet will not be materialized as views in the data warehouse

## Templating

In core layers, we can reference the staging layer using `jinja` tags

## Incremental table & load

On schema change:
- Fact reviews table will not be created every time
- If upstream tables change, we fail

Incremental load:
- We insert an item in the raw reviews table (latest timestamp)
- Run `dbt run` and it will create an incremental load for the facts table

Rebuild all tables:
- Run `dbt run --full-refresh`

## Target

Can check compiled `SQL` code in e.g. `.../target/.../dim_listings_cleansed.sql`