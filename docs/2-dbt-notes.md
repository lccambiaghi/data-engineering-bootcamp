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
- Custom generic tests:
  - Define them `tests/generic`
  - Apply them to models in `schema.yml`
- Can import tests

Can run tests with `dbt test`. 

Debugging:
- With `dbt test -x` it will stop at first failure
- You can look at compiled test
- You can execute the query and see which are the values breaking the tests

Can save test failures in an audit table.

## Data contracts

Can define contracts in `schema.yml` and set contract enforced.

## DBT packages

- Find them on hub.dbt.com
- Add them to `packages.yml`.
- Remember to run `dbt run --full-refresh` if the schema changes.

## Documentation

- Docs can be defined in yaml files (e.g. `schema.yml`) or in markdown files
- Can build with `dbt docs generate`, found in `target`
- DBT ships with a lightweight documentation web server, which can be started with `dbt docs serve`

## Analyses

Useful to execute SQL queries leveraging `dbt` models and macros.
You can run `dbt compile`, take the query from the `target/compiled` and execute it on the DB.

## Hooks

SQL that are executed at pre-defined times, examples:
- `on_run_start`
- `on_run_end`
- `pre-hook`
- `post-hook`: after a model or seed or snapshot is materialized

In the dbt hub there are a lot of third-party packages that help with auditing.

## Grants

Can assign `select` grant to different roles, for the different models

## DBT Fusion

DBT engine rewritten in Rust, handles parsing and compilation much faster.

It should be installed as a system package (not within the `venv`) with

```
curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh -s -- --update
```

It can be run with `~/.local/bin/dbt run`. NOTE that it does not yet support `postgres`.

Can use `dbt-autfoix deprecations` to automatically fix deprecations.
