# Validator Module

This directory contains the core components of the validation framework. It provides the abstract base class for all validators as well as custom error classes for detailed error reporting and handling.

The key files in this module are:

- **`base.py`**
  Defines the `BaseValidator` abstract base class which outlines the common interface and error management for all validators.

- **`errors.py`**
  Defines custom exceptions and error classes that are used across various validators to signal specific validation issues.

---

## Table of Contents

- [Validator Module](#validator-module)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [BaseValidator](#basevalidator)
    - [Key Features](#key-features)
    - [Important Methods and Properties](#important-methods-and-properties)
  - [Custom Errors](#custom-errors)
    - [Defined Errors](#defined-errors)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [Licence](#licence)
  - [Contact](#contact)

---

## Overview

The validator module provides a robust foundation for building validators for different data formats such as CSV and JSON. It consists of an abstract base class that defines the standard interface for all validators, as well as a comprehensive set of custom error classes for precise and informative error reporting.

---

## BaseValidator

The `BaseValidator` class, defined in [`base.py`](base.py), is an abstract base class that establishes the standard structure and behaviour for all validator implementations. This class enforces the implementation of essential validation methods and provides extensive error management functionality.

### Key Features

- **Abstract Methods:**
  The following methods must be implemented by any subclass:
  - `validate()`: Performs the primary validation logic.
  - `validate_keys()`: Validates the keys of the data.
  - `validate_values()`: Validates the values within the data.
  - `validate_types()`: Validates the data types of the data.

- **Error Management:**
  Maintains an internal list of errors that can be:
  - Accessed via the `errors` property.
  - Appended to using the setter.
  - Cleared using the deleter.
  - Iterated over, checked for membership, and indexed.

- **Magic Methods:**
  Implements various dunder methods for:
  - String representations (`__str__`, `__repr__`).
  - Boolean evaluation (`__bool__`) to indicate the presence of errors.
  - Determining the number of errors (`__len__`).
  - Iterating over errors (`__iter__`).
  - Membership testing (`__contains__`).
  - Index-based access (`__getitem__`).

### Important Methods and Properties

- **`errors` (property):**
  Returns a list of validation errors. This list is dynamically managed as errors are added or cleared.

- **Abstract Methods to Implement:**
  - `validate()`
  - `validate_keys()`
  - `validate_values()`
  - `validate_types()`

These methods form the backbone of any validator built upon the `BaseValidator`.

---

## Custom Errors

The [`errors.py`](errors.py) file contains custom exception classes that are used to indicate specific validation failures. These errors extend from the base `_ValidationError` class to ensure consistency in error reporting.

### Defined Errors

- **`_ValidationError`**
  The base class for all validation errors. It encapsulates a standard error message and is used as the parent for all custom exceptions.

- **`InvalidKeyError`**
  Raised when a provided key is invalid.

- **`InvalidValueError`**
  Raised when a provided value is invalid.

- **`InvalidTypeError`**
  Raised when a provided type is invalid.

- **`InvalidInputError`**
  Raised when the overall input is invalid. This error aggregates detailed error messages.

- **`InvalidDateFormatError`**
  Raised when a date value does not match the expected format.

- **`FixedValueColumnError`**
  Raised when a column expected to contain fixed valid values includes an invalid value.

- **`MissingDataError`**
  Raised when a required column contains missing data.

- **`MissingColumnError`**
  Raised when a required column is not found in the input data.

- **`MissingPathsError`**
  Raised when file paths are missing.

- **`UniqueValueError`**
  Raised when duplicate values are found in a column that should contain unique entries.

- **`EmptyInputError`**
  Raised when the input provided for validation is empty.

Each error class is designed to provide a clear and informative message, which greatly aids in debugging and ensuring data integrity.

---

## Usage

The validator module is intended to serve as a foundation for creating specific validators (e.g., CSV, JSON). Developers should extend the `BaseValidator` class to implement their custom validation logic and use the provided custom errors for handling validation failures.

Below is an example of how to extend `BaseValidator`:

```python
from src.validator.base import BaseValidator
from src.validator.errors import InvalidInputError

class MyValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.errors:
            return True
        return False

    def validate_keys(self) -> bool:
        return True

    def validate_values(self) -> bool:
        return True

    def validate_types(self) -> bool:
        return True

try:
    validator = MyValidator()
    if validator.validate():
        print("Validation successful!")
    else:
        print("Validation failed!")
except InvalidInputError as e:
    print("Validation error occurred:")
    print(e)
```

## Contributing

Contributions are welcome! Please adhere to standard code review practices and ensure your contributions are well tested and documented.

## Licence

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For further enquiries or to report issues, please contact [pratheesh.prakash@cognext.ai].
