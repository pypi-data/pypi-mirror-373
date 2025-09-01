type: duckdb
name: load_customer_to_raw
author: data-engineering
tags: ["duckdb", "example"]

source:
  type: local
  file_format: json
  path: "./assets/data/explode-customer.json"
  format: newline_delimited

transforms:
  - op: rename_snakecase

  - op: sql
    sql_file: import_statement.sql

  - op: sql
    priority: post
    sql: |
      SELECT
        id
        , TRY_CAST(timestamp AS TIMESTAMP)        AS event_timestamp
        , json_extract(user, '$.name')::VARCHAR   AS username
        , json_extract(user, '$.email')::VARCHAR  AS email
        , UNNEST(items, recursive := true)
      FROM df

  - op: rename_columns
    priority: post
    columns:
      - name: qty
        source: quantity

sink:
  type: console

metrics:
  - type: console
