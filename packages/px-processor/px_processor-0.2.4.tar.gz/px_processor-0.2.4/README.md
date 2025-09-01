# Data Validator Framework

A Python-based data validation framework for CSV and JSON data. This project provides a unified approach to validate data formats and contents using specialised validators built on a common foundation. The framework is easily extendable and leverages industry-standard libraries such as Pandas, Polars, and Pydantic.

---

## Overview

The Data Validator Framework is designed to simplify and standardise data validation tasks. It consists of:

- **CSV Validator**: Validates CSV files using either the Pandas or Polars engine. It checks for issues such as missing data, incorrect data types, invalid date formats, fixed column values, and duplicate entries.
- **JSON Validator**: Validates JSON objects against Pydantic models, ensuring the data conforms to the expected schema while providing detailed error messages.
- **Common Validator Base**: An abstract `BaseValidator` class that defines a standard interface and error management for all validators.
- **Custom Errors**: A set of custom error classes that offer precise and informative error reporting, helping to identify and resolve data issues efficiently.

---

## Features

- **CSV Validation**
  - Supports both Pandas and Polars engines.
  - Reads multiple CSV files concurrently.
  - Validates data types, missing data, date formats, fixed values, and uniqueness constraints.

- **JSON Validation**
  - Uses Pydantic for schema validation.
  - Automatically converts JSON keys to strings to ensure compatibility.
  - Aggregates and formats error messages for clarity.

- **Extensible Architecture**
  - A unified abstract base class (`BaseValidator`) that standardises validation methods.
  - Customisable error handling with detailed messages.

---

## Requirements

- **Python**: 3.10 or above.
- **Dependencies**:
  - For CSV validation:
    - [pandas](https://pandas.pydata.org/)
    - [polars](https://www.pola.rs/) (if using Polars)
    - [pyarrow](https://arrow.apache.org/) (if using the PyArrow engine with Pandas)
  - For JSON validation:
    - [Pydantic](https://pydantic-docs.helpmanual.io/)
    - [pydantic-core](https://pypi.org/project/pydantic-core/)

---

## Installation

1. **Clone the Repository:**

   ```bash
   pip install px_processor
   poetry add px_processor
   uv add px_processor
   ```

--

## Usage

### CSV Validation Example

```python
from processor import CSVValidator

validator = CSVValidator(
    csv_paths=["data/file1.csv", "data/file2.csv"],
    data_types=["str", "int", "float"],
    column_names=["id", "name", "value"],
    unique_value_columns=["id"],
    columns_with_no_missing_data=["name"],
    missing_data_column_mapping={"value": ["NaN", "None"]},
    valid_column_values={"name": ["Alice", "Bob", "Charlie"]},
    drop_columns=["unused_column"],
    strict_validation=True,
)

validator.validate()
```

### JSON Validation Example

```python
from pydantic import BaseModel
from processor import JSONValidator

class UserModel(BaseModel):
    id: int
    name: str
    email: str

json_data = {
    "id": 123,
    "name": "Alice",
    "email": "alice@example.com"
}

validator = JSONValidator(model=UserModel, input_=json_data)
validator.validate()
```

--

## Project Structure

```bash
validator/
├── .gitignore
├── .python-version
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── README.md
├── src/
    └── validator/
        └── config/
        │   ├── __init.py__
        │   └── csv_.py           # Configuration settings for CSV validation.
        ├── __init.py__
        ├── base.py               # Abstract base class for validators.
        ├── errors.py             # Custom error classes for validation.
        ├── README.md
        ├── csv/
        │   ├── __init.py__
        │   ├── README.md
        │   └── main.py           # CSV validation implementation.
        └── json/
        │   ├── __init.py__
        │   ├── README.md
        │   └── main.py          # JSON validation implementation.
        └── tests/
            ├── __init.py__
            ├── config.py           # Test configuration settings.
            |── integration/
            |   ├── __init.py__
            |   ├── test_integration_json.py   # Integration tests for JSON validation.
            |   └── test_integration_csv.py    # Integration tests for CSV validation.
            ├── unit/
            |   ├── __init.py__
            |   ├── test_csv.py     # Unit tests for CSV validation.
            |   └── test_json.py    # Unit tests for JSON validation.
            ├── csvs/               # CSV files for testing.
            └── jsons/              # JSON files for testing.
```

## Contributing

Contributions are welcome! Please adhere to standard code review practices and ensure your contributions are well tested and documented.

## Licence

This project is licensed under the MIT License. See the LICENSE file for details.

## For developers

To generate requirements.txt

```bash
uv export --format requirements.txt --no-emit-project --no-emit-workspace --no-annotate --no-header --no-hashes --no-editable -o requirements.txt
```

To generate CHANGELOG.md

```bash
uv run git-cliff -o CHANGELOG.md
```

To bump version.

```bash
 uv run bump-my-version show-bump
```