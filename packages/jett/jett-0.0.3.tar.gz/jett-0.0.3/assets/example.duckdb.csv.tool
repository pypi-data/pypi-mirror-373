type: duckdb
name: load_customer_to_raw
author: data-engineering
tags: ["duckdb", "example"]

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
    sql_file: import_statement.sql

  - op: sql
    priority: pre
    sql: |
      SELECT
        index
        , customer_id
        , email
        , subscription_date
      FROM df

  - op: rename_columns
    priority: post
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
