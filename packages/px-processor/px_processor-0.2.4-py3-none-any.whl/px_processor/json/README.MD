# JSON Validator

A Python module for validating JSON objects using [Pydantic](https://pydantic-docs.helpmanual.io/). This module validates JSON data against a specified Pydantic model, aggregates validation errors, and raises an exception when invalid data is encountered.

## Overview

The JSON Validator module provides a straightforward way to validate JSON data. It converts all keys in the input JSON to strings (ensuring compatibility with Pydantic models), validates the data against a provided Pydantic model, and processes any validation errors into a human-readable format. If the JSON data does not meet the expected schema, an `InvalidInputError` is raised with detailed error messages.

## Features

- **Pydantic-Based Validation:**
  Utilises the powerful validation capabilities of Pydantic to ensure JSON data adheres to a defined schema.

- **Error Aggregation:**
  Captures all validation errors and aggregates them into a clear, human-readable error message.

- **Key Conversion:**
  Automatically converts JSON keys to strings to avoid potential type issues during validation.

- **Extensible Design:**
  Provides placeholder methods (`validate_keys`, `validate_values`, `validate_schema`, and `validate_types`) for potential future enhancements.

## Requirements

- **Python:** 3.10 or above.
- **Libraries:**
  - [Pydantic](https://pydantic-docs.helpmanual.io/)
  - [pydantic-core](https://pypi.org/project/pydantic-core/)

- **Custom Modules:**
  - `src.validator.BaseValidator`
  - `src.validator.InvalidInputError`

## Usage

  Below is an example demonstrating how to use the JSONValidator:

```python
from pydantic import BaseModel
from src.validator.json.main import JSONValidator


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

## Detailed Class Description

`JSONValidator`

The JSONValidator class extends BaseValidator and is responsible for validating JSON objects against a Pydantic model.

### Initialisation

```python
def __init__(self, model: type[BaseModel], input_: dict[Hashable, Any]) -> None:
```

### Parameters

- `model` (type[BaseModel]): The Pydantic model class that defines the schema for the JSON data.
- `input_` (dict[Hashable, Any]): The JSON data to validate. All keys are converted to strings for compatibility.

### Raises

`InvalidInputError`: Raised when the JSON data fails to validate against the Pydantic model.

### Key Methods

- `validate`: Checks if the JSON data is valid. Returns True if no errors are present; otherwise, returns False.

- `__add_errors`: Processes and stores the validation errors provided by Pydantic.

- `__generate_error_message`: Aggregates validation errors into a single, formatted error message. Each error is listed with its type and the relevant field.

### Placeholder Methods

- `validate_keys`
- `validate_values`
- `validate_schema`
- `validate_types`

These methods are reserved for future validation extensions.

### Error Handling

If the JSON data does not conform to the expected schema defined by the Pydantic model, the JSON Validator captures the validation errors and compiles them into a detailed error message. When the validate method detects errors, an `InvalidInputError` is raised, providing insight into the specific validation issues.

## Contributing

Contributions are welcome! Please adhere to standard code review practices and ensure your contributions are well tested and documented.

## Licence

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For further enquiries or to report issues, please contact [pratheesh.prakash@cognext.ai].
