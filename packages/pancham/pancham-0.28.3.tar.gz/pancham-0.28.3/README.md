# Pancham Data Pipelines

![Github Actions](https://github.com/loqui-tech/pancham/actions/workflows/build.yml/badge.svg)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Loqui-Tech_pancham&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Loqui-Tech_pancham)

Pancham simplifies the process of reading and processing data with Pandas. 

## What is it for

A common scenario in data migration projects is to need to take exports from one system, apply some transformation rules and write the data somewhere else. This could be files, a database or an API. All of this can be done with Pandas but we would need to write a lot of code, Pancham is here to make that process easier.

```mermaid
flowchart LR;
    s[Source Files]-->t[Transformation];
    t-->o[Output Files];
```
### Key features

- Load files
- Rename fields
- Validate data types and not-null columns
- Apply python functions to transform values
- Return data as a Pandas DataFrame
- Write data to a database

### Supported Source Files

- Excel
- SQL
- YAML
- CSV
- JSON

### Supported Output

- SQL
- CSV

Additional sources and output formats will be added with time.

## Usage

The most common approach is to use a mapping file.

```yaml
name: example
file_type: yaml
file_path: source/customer.yml
key: customer
output:
  - table: customers
    output_type: database
fields:
  - name: id
    source_name: customer_id
    field_type: str
    nullable: false
  - name: status
    source_name: account_status
    field_type: str
    nullable: false
```

This simple mapping file expects to be able to load a source file called `customer.yml` with the following content:

```yaml
customer:
    - customer_id: 123
      account_status: active
    - customer_id: 456
      account_status: on_hold
```

The pipeline wll read the input file and populate a database that you can then query.

The final part is the pancham configuration.
