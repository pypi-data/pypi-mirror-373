type: polars
name: load_customer_to_raw
author: data-engineer
tags: ["polars", "example"]

source:
  type: local
  file_format: ndjson
  path: "./assets/data/explode-customer.json"

transforms:
  - op: rename_snakecase

  - op: flatten_all_except_array

  - op: sql
    sql_file: import_statement.polars.sql

#  - op: sql
#    sql: |
#      SELECT
#        id
#        , TRY_CAST(timestamp AS TIMESTAMP)        AS event_timestamp
#        , json_extract(user, '$.name')::VARCHAR   AS username
#        , json_extract(user, '$.email')::VARCHAR  AS email
#        , UNNEST(items, recursive := true)
#      FROM self

#  - op: rename
#    columns:
#      - name: qty
#        source: quantity

sink:
  type: console

metrics:
  - type: console
