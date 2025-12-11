# Theory notes

## SCD - type 0

- When a dimension changes, data warehouse should not be updated
- Example: fax data went out of fashion so no point in updating the data warehouse

## SCD - type 1

- When a dimension changes, we just overwrite the original data
- Example: 
  - Can filter property on airbnb depending on air-condition
  - If a property adds air-conditioning, not relevant to track changes

## SCD - type 2

- When a dimension change, we need to add a new record
- Historical data remains recoverable
- Add new columns (e.g. `valid_from` and `valid_to`)
- Example: price of property is updated
- Only makes sense for slowly changing data, otherwise it could trigger many pipelines and be expensive

## SCD - type 3

- Columns for "previous type" and "current type"
- Example: 
  - Property changes from Private -> Shared -> Entire
  - We only care about changes with previous type
- Pro: Keep number of records lower
- Cons: harder to process