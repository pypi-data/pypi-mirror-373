# CSV Validator

A Python module for validating CSV files using either the Pandas or Polars dataframe engine. This module is part of a larger validation framework and provides comprehensive CSV file checks such as missing data, date format validation, fixed column values, and unique value constraints.

## Overview

The CSV Validator is designed to read one or more CSV files concurrently and validate their contents against a set of configurable rules. It supports:

- Validation of required columns and data types.
- Enforcement of strict validation rules (raising exceptions when data is invalid).
- Adaptation to either Pandas or Polars as the underlying dataframe engine, based on your configuration.

## Features

- **Multiple Engine Support:**
  Choose between Pandas and Polars via configuration.

- **Concurrent File Reading:**
  Utilises threading to read multiple CSV files concurrently.

- **Flexible Schema Definition:**
  Define column names, data types, and drop unwanted columns.

- **Comprehensive Validations:**
  - **Missing Data:** Checks for missing values in specified columns.
  - **Date Format:** Ensures date columns adhere to an expected format (ISO8601).
  - **Fixed Column Values:** Validates that columns contain only allowed values.
  - **Unique Values:** Ensures that specified columns contain unique values.

- **Error Aggregation:**
  Aggregates all validation errors into a single error message for easier debugging.

## Requirements

- **Python:** Version 3.10 or above.
- **Libraries:**
  - For Pandas engine: [pandas](https://pandas.pydata.org/) (and optionally [pyarrow](https://arrow.apache.org/) if using the `pyarrow` engine).
  - For Polars engine: [polars](https://www.pola.rs/).

- **Custom Modules:**
  This module is part of a larger package and depends on:
  - `src.validator.BaseValidator`
  - `src.validator.CSVConfig`
  - Custom error classes such as `EmptyInputError`, `FixedValueColumnError`, `InvalidDateFormatError`, `InvalidInputError`, `MissingColumnError`, `MissingDataError`, `MissingPathsError`, and `UniqueValueError`.

## Configure CSVConfig

Adjust the configuration in CSVConfig to select your desired engine ("pandas" or "polars") and set any other parameters like `PANDAS_ENGINE`, `PANDAS_DTYPE_MAPPING`, and `DATE_FORMAT`.

## Usage

Below is a simple example of how to use the CSVValidator:

```python
from src.validator.csv.main import CSVValidator

Initialise the CSVValidator with your CSV paths and validation rules
validator = CSVValidator(
    csv_paths=["data/file1.csv", "data/file2.csv"],
    data_types=["character", "integer", "double"],  # Use platform-x data-types.
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

Note: If strict_validation is set to True, an InvalidInputError will be raised immediately when validations fail.

## Detailed Class Description

### CSVValidator

The CSVValidator class is the central class responsible for validating CSV files. It extends BaseValidator and utilises configuration settings from CSVConfig.

#### Initialisation

```python
def __init__(
    *,
    csv_paths: list[str],
    data_types: list[str],
    column_names: list[str],
    unique_value_columns: list[str] | None = None,
    columns_with_no_missing_data: list[str] | None = None,
    missing_data_column_mapping: dict[str, list[str]] | None = None,
    valid_column_values: dict[str, list[str]] | None = None,
    drop_columns: list[str] | None = None,
    strict_validation: bool = True,
) -> None:
```

#### Parameters

- `csv_paths` (list[str]): List of CSV file paths to be validated.
- `data_types` (list[str]): Data types corresponding to each column.
- `column_names` (list[str]): Names of the columns to be read from the CSV.
- `unique_value_columns` (list[str], optional): Columns that must contain unique values.
- `columns_with_no_missing_data` (list[str], optional): Columns that must not have missing data.
- `missing_data_column_mapping` (dict[str, list[str]], optional): Mapping for columns that may have custom missing data representations.
- `valid_column_values` (dict[str, list[str]], optional): Mapping defining allowed values for certain columns.
- `drop_columns` (list[str], optional): Columns to exclude from validation.
- `strict_validation` (bool, optional): If set to True, the validator will raise an exception upon encountering validation errors.

#### Raises

- `EmptyInputError`: If the list of CSV paths is empty.
- `InvalidInputError`: If any of the validations fail and strict validation is enabled.

#### Key Methods

- `__read`: Reads the CSV files into a Pandas DataFrame or a Polars LazyFrame. It employs concurrent file reading when multiple CSV paths are provided.

- `validate`: Returns True if no validation errors are found; otherwise, returns False. All errors are stored in the errors attribute.

- `__analyse`: Orchestrates the execution of individual validation checks:

  - `_check_missing_data`: Ensures that columns flagged to have no missing data do not contain any missing entries.

  - `_check_fixed_column_values`: Verifies that specified columns only contain allowed fixed values.

  - `_check_date_format`: Checks whether date columns adhere to the expected ISO8601 format (or equivalent valid datetime types).

  - `_check_unique_values`: Ensures that columns designated to have unique values do indeed have a unique entry for each row.

  - `_generate_error_message`: Compiles individual error messages into a single, human-readable string.

Other placeholder methods (validate_keys, validate_types, validate_values) are provided for potential future validations.

#### Error Handling

The CSV Validator utilises custom exceptions to report specific validation issues:

- `EmptyInputError`
- `FixedValueColumnError`
- `InvalidDateFormatError`
- `InvalidInputError`
- `MissingColumnError`
- `MissingDataError`
- `MissingPathsError`
- `UniqueValueError`

Each error is appended to the errors list and is aggregated into a comprehensive error message.

### Engine Configuration

The behaviour of the CSV Validator is governed by the CSVConfig settings:

- `DATAFRAME_ENGINE`: Specifies the dataframe engine to use ("pandas" or "polars").

- `PANDAS_ENGINE`: If using Pandas, select between "c" and "pyarrow" engines.

- `PANDAS_DTYPE_MAPPING`: Maps data type strings to actual Pandas data types.

- `DATE_FORMAT`: Defines the expected date format for parsing date columns.

Ensure your environment is configured with the correct engine and all required dependencies are installed.

## Contributing

Contributions are welcome! Please adhere to standard code review practices and ensure your contributions are well tested and documented.

## Licence

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For further enquiries or to report issues, please contact [pratheesh.prakash@cognext.ai].
