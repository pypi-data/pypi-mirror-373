type: daft
name: load_customer_to_raw
author: data-engineering
tags: ["daft", "example"]

source:
  type: local
  arrow_type: dataset
  file_format: csv
  path: "./assets/data/customers-1000.csv"
  delimiter: ","
  header: true
  sample_records: 20

transforms:
  - op: rename_snakecase

sink:
  - type: console

metrics:
  - type: console
