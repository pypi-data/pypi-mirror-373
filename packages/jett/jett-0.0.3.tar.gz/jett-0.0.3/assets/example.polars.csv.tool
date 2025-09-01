type: polars
name: load_customer_to_raw
author: data-engineer
tags: ["polars", "example"]

source:
  type: local
  file_format: csv
  path: "./assets/data/customers-1000.csv"
  delimiter: ","
  header: true
  sample_records: 20

transforms:
  - op: rename_snakecase

  - op: sql
    sql_file: import_statement.polars.sql

  - op: sql
    sql: |
      SELECT
        index
        , customer_id
        , email
        , subscription_date
      FROM self

  - op: rename
    columns:
      - name: id
        source: index

#  - op: drop_columns
#    priority_apply: false
#    target_col:
#      - validated_by_constraint

sink:
  type: console

metrics:
  - type: console

  - type: restapi
    condition: only_failed
    base_url: http://localhost:1010
    path: /api/alert/slack
    method: POST
