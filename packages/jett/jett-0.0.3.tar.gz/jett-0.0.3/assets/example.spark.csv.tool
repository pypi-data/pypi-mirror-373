type: spark
name: load_customer_to_raw
author: data-engineering
tags: ["spark", "example"]
master: local
enable_hive_support: false
conf:
  spark.sql.session.timeZone: UTC
  spark.jars.packages: org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.4.3
  spark.sql.extensions: org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
#  spark.sql.catalog.spark_catalog: org.apache.iceberg.spark.SparkSessionCatalog
#  spark.sql.catalog.spark_catalog.type: hive
#  spark.sql.catalog.spark_catalog.cache-enabled: false
  spark.sql.sources.partitionOverwriteMode: dynamic

source:
  type: local
  file_format: csv
  path: "./assets/data/customers-1000.csv"
  delimiter: ","
  header: true
  sample_records: 20

transforms:
  - op: rename_snakecase

#  - op: sql
#    sql_file: import_statement.sql
#
#  - op: sql
#    priority_apply: true
#    sql: |
#      SELECT
#        index
#        , customer_id
#        , email
#        , subscription_date
#      FROM df

  - op: rename_columns
    priority: group
    columns:
      - name: id
        source: index

  - op: drop_columns
    priority: post
    columns:
      - id
      - phone_1
      - phone_2
      - website
      - company
      - country
      - city

sink:
  type: console

metrics:
  - type: console
