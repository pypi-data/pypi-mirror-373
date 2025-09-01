type: arrow
name: load_customer_to_raw
author: data-engineering
tags: ["arrow", "example"]

source:
  type: local
  arrow_type: table
  file_format: json
  path: "./assets/data/explode-customer.json"

sink:
  - type: console

metrics:
  - type: console
