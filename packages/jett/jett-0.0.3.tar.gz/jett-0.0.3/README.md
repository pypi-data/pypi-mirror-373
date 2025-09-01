# Jett

[![pypi version](https://img.shields.io/pypi/v/jett)](https://pypi.org/project/jett/)
[![python support version](https://img.shields.io/pypi/pyversions/jett)](https://pypi.org/project/jett/)
[![size](https://img.shields.io/github/languages/code-size/ddeutils/jett)](https://github.com/ddeutils/jett)

**Just an Engine Template Tool** that easy to use and develop for Data Engineer.
This project support the ETL template for multiple DataFrame engine like
`PySpark`, `Duckdb`, `Polars`, etc.

**Supported Features**:

- Dynamic Supported Engines via YAML template
- JSON Schema Validation
- Plugin Airflow Operator

## 📦 Installation

```shell
uv pip install -U jett
```

**Engine Supported**:

| Name    | Status | Description                                           |
|---------|:------:|-------------------------------------------------------|
| Pyspark |   ✅    | Pyspark and Spark submit CLI for distributed workload |
| DuckDB  |   ✅    | DuckDB and Spark API DuckDB                           |
| Polars  |   ✅    | Polars for Python workload                            |
| Arrow   |   ✅    | Arrow for Python workflow with Columnar               |
| Daft    |   ✅    | Daft for Python distributed workload                  |
| DBT     |   ❌    | DBT for SQL workload                                  |
| GX      |   ❌    | Great Expectation for data quality                    |

> [!WARNING]
> This project will focus on the Arrow engine first because it is the base lib
> for most DataFrame libs.

> [!NOTE]
> **Version Tracking**:
>
> | Package |   Version    | Next Support |
> |---------|:------------:|:------------:|
> | Python  |  `3.10.13`   |  `>=3.11.0`  |
> | Spark   |   `3.4.2`    |  `>=4.0.0`   |
> | Hadoop  |     `3`      |     `3`      |
> | Java    | `openjdk@11` | `openjdk@17` |
> | Pyspark |   `3.4.1`    |  `>=4.0.0`   |
> | Scala   |  `2.12.17`   |  `2.12.17`   |
> | DuckDB  |   `1.3.2`    |              |
> | Polars  |   `1.32.0`   |              |
> | Arrow   |   `21.0.0`   |              |
> | Daft    |   `0.5.21`   |              |

## 📝 Usage

For example, making file, `etl.polars.tool` (I use `.tool` be file extension for validate
it with the JSON schema with pattern `*.tool`), for ETL state like:

```yaml
type: polars
name: Load CSV to GGSheet
app_name: load_csv_to_ggsheet
master: local

# 1) 🚰 Load data from source
source:
  type: local
  file_format: csv
  path: ./assets/data/customer.csv

# 2) ⚙️ Transform this data.
transforms:
  - op: rename_to_snakecase
  - op: group
    transforms:
      - op: expr
        sql: "CAST(id AS string)"

# 3) 🎯 Sink result to target (multi-sink supported)
sink:
  - type: local
    file_type: google_sheet
    path: ./assets/landing/customer.gsheet

# 4) 📩 Metric that will send after execution.
metric:
  - type: console
    convertor: basic
  - type: restapi
    convertor: basic
    host: "localhost"
    port: 1234
```

Use by Python API:

```python
from jett import Tool

tool = Tool(path="./etl.spark.tool")
tool.execute(allow_raise=True)
```

## 📖 Documents

This project will reference emoji from the [Pipeline Emojis](https://emojidb.org/pipeline-emojis).

## 💬 Contribute

I do not think this project will go around the world because it has specific propose,
and you can create by your coding without this project dependency for long term
solution. So, on this time, you can open [the GitHub issue on this project 🙌](https://github.com/ddeutils/jett/issues)
for fix bug or request new feature if you want it.
