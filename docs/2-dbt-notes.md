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

## Sources and seeds

Seeds: 
- Local files uploaded to data warehouse from dbt
- They live in the `seed-paths`
- Can import into data warehouse with `dbt seed`
- `dbt` automatically infers schema

Sources:
- Data is already in data warehouse
- Sources are added to `sources.yml`
- `dbt compile` will check if references and templates are correct

### Freshness check

Can add freshness check in `sources.yml` and can run with `dbt source freshness`

## Snapshot

### Type-2 slowly changing dimension

Example: e-mails updated

`dbt` adds 2 columns:
- `dbt_valid_from`
- `dbt_valid_to`

You can get the recent value by filtering `dbt_valid_to` equal to `null`

### Configuration and strategies

Snapshots live in the `snapshots` folder. Convention: same filename as model + `_snapshots.yml`.

Snaphost engine looks at a column and will automatically compute the two columns.

Strategies:
- Timestamp: unique key + `updated_at` column (tracked column)
- Check: if change in monitored columns, new record will be created
- Macro

Command for snapshot is `dbt snapshot`. Every time we run it, it will update the snapshot table.

## Tests

Unit tests:
 - Test transformations with mock data
 - Typically next to the model

Data tests:
- Generic: available plug&play
  - unique
  - not_null
  - accepted_values
  - relationships (foreign keys)
- Singular:
  - SQL query in `tests` folder
  - If any record is returned, test will fail
- Can import tests

Can run tests with `dbt test`. 

Debugging:
- With `dbt test -x` it will stop at first failure
- You can look at compiled test
- You can execute the query and see which are the values breaking the tests

Can save test failures in an audit table.

## Data contracts

Can define contracts in `schema.yml` and set contract enforced.