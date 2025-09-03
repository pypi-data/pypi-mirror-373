# Snowflake Data Validation

[![License Apache-2.0](https://img.shields.io/:license-Apache%202-brightgreen.svg)](http://www.apache.org/licenses/LICENSE-2.0.txt)
[![Python](https://img.shields.io/badge/python-3.9--3.13-blue)](https://www.python.org/downloads/)

**Snowflake Data Validation** is a command-line tool and Python library for validating data migrations and ensuring data quality between source and target databases, with a focus on Snowflake and SQL Server.

---

##### This package is in Private Preview.

---

## 🚀 Features

- **Multi-level validation**: schema, statistical metrics, and data integrity.
- **Database connectors**: support for SQL Server and Snowflake.
- **User-friendly CLI**: commands for automation and orchestration.
- **Flexible configuration**: YAML-based validation workflows.
- **Detailed reporting**: comprehensive reports and progress tracking.
- **Extensible**: architecture ready for more database engines.

---

## 📦 Installation

```bash
pip install snowflake-data-validation
```

For SQL Server support:

```bash
pip install "snowflake-data-validation[sqlserver]"
```

For development and testing:

```bash
pip install "snowflake-data-validation[all]"
```

---

## ⚡ Quick Start

Run a validation from SQL Server to Snowflake:

```bash
snowflake-data-validation sqlserver run-validation --data-validation-config-file ./config/conf.yaml
```

Or using the short alias:

```bash
sdv sqlserver run-validation --data-validation-config-file ./config/conf.yaml
```

---

## 🛠️ Configuration

Create a YAML file to define your validation workflow:

```yaml
source_platform: SqlServer
target_platform: Snowflake
output_directory_path: /path/to/output
parallelization: false

source_connection:
  mode: credentials
  host: "server"
  port: 1433
  username: "user"
  password: "password"
  database: "db"

target_connection:
  mode: name
  name: "SnowflakeConnection"

validation_configuration:
  schema_validation: true
  metrics_validation: true
  row_validation: false

comparison_configuration:
  tolerance: 0.01

tables:
  - fully_qualified_name: database.schema.table1
    use_column_selection_as_exclude_list: false
    column_selection_list:
      - column1
      - column2
```

See the documentation for more advanced configuration examples.

---

## 🏗️ Architecture

- **CLI**: `main_cli.py`, `sqlserver_cli.py`, `snowflake_cli.py`
- **Connectors**: `connector/`
- **Extractors**: `extractor/`
- **Validation**: `validation/`
- **Configuration**: `configuration/`
- **Orchestrator**: `comparison_orchestrator.py`

Project structure:
```
snowflake-data-validation/
├── src/snowflake/snowflake_data_validation/
│   ├── main_cli.py
│   ├── sqlserver/
│   ├── snowflake/
│   ├── connector/
│   ├── extractor/
│   ├── validation/
│   ├── configuration/
│   ├── utils/
│   └── comparison_orchestrator.py
├── docs/
├── tests/
└── config_files/
```

---

## 📊 Reports

- Schema validation results
- Statistical comparison metrics
- Detailed error logs and recommendations

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](../../CONTRIBUTING.md) for details on how to collaborate, set up your development environment, and submit PRs.

---

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](../../LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: [Full documentation](https://github.com/snowflakedb/migrations-data-validation)
- **Issues**: [GitHub Issues](https://github.com/snowflakedb/migrations-data-validation/issues)

---

**Developed with ❄️ by Snowflake**
