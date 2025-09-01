"""Custom exceptions for the validator module."""

from collections.abc import Hashable, Sequence
from datetime import datetime
from typing import Any

from px_processor.config import CSVConfig


class _ValidationError(Exception):
    """Base class for all validation errors."""

    def __init__(self, message: str) -> None:
        """Initialise the object."""
        self.message: str = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
            str: A string representation of the object.

        """
        return self.message

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
            str: A string representation of the object.

        """
        return self.__str__()

    def __bool__(self) -> bool:
        """Return a boolean representation of the object.

        Returns
        -------
            bool: True if the message is not empty, False otherwise

        """
        return bool(self.message)


class InvalidKeyError(_ValidationError):
    """Raised when a key is invalid."""

    def __init__(self, key: Hashable) -> None:
        """Initialise the object."""
        self.key: Hashable = key
        message: str = f"Invalid key: {key}"
        super().__init__(message=message)


class InvalidValueError(_ValidationError):
    """Raised when a value is invalid."""

    def __init__(self, value: str) -> None:
        """Initialise the object."""
        self.value: str = value
        message: str = f"Invalid value: {value}"
        super().__init__(message=message)


class InvalidTypeError(_ValidationError):
    """Raised when a type is invalid."""

    def __init__(self, type_: str) -> None:
        """Initialise the object."""
        self.type_: str = type_
        message: str = f"Invalid type: {type_}"
        super().__init__(message=message)


class InvalidInputError(_ValidationError):
    """Invalid input."""

    def __init__(self, message: str) -> None:
        """Initialise the object."""
        self.message: str = (
            f"\n\nInput validation failed due to the following errors: \n\n{message}"
        )
        super().__init__(message=self.message)


class InvalidDateFormatError(_ValidationError):
    """Raised when a date format is invalid."""

    def __init__(self, column: str) -> None:
        """Initialise the object."""
        error_message: str = f"Values in '{column}' should follow ISO8601 format."
        super().__init__(message=error_message)


class FixedValueColumnError(_ValidationError):
    """Raised when a fixed value column has invalid values."""

    def __init__(self, column: str, valid_values: list[str]) -> None:
        """Initialise the object."""
        error_message: str = f"Valid values for '{column}' column are {valid_values}."
        super().__init__(message=error_message)


class MissingDataError(_ValidationError):
    """Raised when a column has missing data."""

    def __init__(self, column: str, rows: list[Any]) -> None:
        """Initialise the object."""
        error_message: str = f"Missing data in '{column}' column in rows: {rows}."
        super().__init__(message=error_message)


class MissingColumnError(_ValidationError):
    """Raised when a column is missing."""

    def __init__(self, column: str) -> None:
        """Initialise the object."""
        error_message: str = f"The '{column}' column could not be found."
        super().__init__(message=error_message)


class MissingPathsError(_ValidationError):
    """Raised when file-paths are missing."""

    def __init__(self) -> None:
        """Initialise the object."""
        error_message: str = "Empty file-paths."
        super().__init__(message=error_message)


class UniqueValueError(_ValidationError):
    """Raised when a column has duplicate values."""

    def __init__(self, column: str) -> None:
        """Initialise the object."""
        error_message: str = f"Duplicate values in '{column}'."
        super().__init__(message=error_message)


class EmptyInputError(_ValidationError):
    """Empty input error."""

    def __init__(self) -> None:
        """Initialise the object."""
        self.message: str = "Empty input. Please provide a non-empty input."
        super().__init__(message=self.message)


class MandatoryColumnError(_ValidationError):
    """Raised when a mandatory column is missing."""

    def __init__(self, missing_columns: Sequence[str]) -> None:
        """Initialise the object."""
        self.columns: Sequence[str] = missing_columns
        error_message: str = f"The mandatory columns {missing_columns} are missing."
        super().__init__(message=error_message)


class ColumnValueLimitError(_ValidationError):
    """Raised when a column value exceeds the defined limits."""

    def __init__(
        self,
        column: str,
        min_value: float | datetime | None,
        max_value: float | datetime | None,
    ) -> None:
        """Initialise the object."""
        self.column: str = column
        self.min_value: float | datetime | None = min_value
        self.max_value: float | datetime | None = max_value

        error_message: str = f"Values in '{column}' should be between {min_value} and {max_value}."
        super().__init__(message=error_message)


class ColumnComparisonError(_ValidationError):
    """Raised when column comparison fails."""

    def __init__(
        self, left_column: str, operator: str, right_column: str, failed_rows: list[int]
    ) -> None:
        """Initialise the object."""
        self.left_column: str = left_column
        self.operator: str = operator
        self.right_column: str = right_column
        self.failed_rows: list[int] = failed_rows

        if len(failed_rows) <= CSVConfig.MAX_ROWS_TO_BE_SHOWN_IN_ERROR:
            rows_str: str = str(failed_rows)
        else:
            rows_str = (
                f"{failed_rows[: CSVConfig.MAX_ROWS_TO_BE_SHOWN_IN_ERROR]} ... "
                f"and {len(failed_rows) - CSVConfig.MAX_ROWS_TO_BE_SHOWN_IN_ERROR} more rows"
            )

        error_message: str = (
            f"Column comparison '{left_column} {operator} {right_column}' failed "
            f"in rows: {rows_str}."
        )
        super().__init__(message=error_message)


class ColumnComparisonDataTypeError(_ValidationError):
    """Raised when columns in comparison have incompatible data types."""

    def __init__(
        self, left_column: str, left_type: str, right_column: str, right_type: str
    ) -> None:
        """Initialise the object."""
        self.left_column: str = left_column
        self.left_type: str = left_type
        self.right_column: str = right_column
        self.right_type: str = right_type

        error_message: str = (
            f"Cannot compare columns '{left_column}' (type: {left_type}) and "
            f"'{right_column}' (type: {right_type}) - incompatible data types."
        )
        super().__init__(message=error_message)


class ColumnComparisonNullValueError(_ValidationError):
    """Raised when columns in comparison contain null values."""

    def __init__(self, columns_with_nulls: dict[str, list[int]]) -> None:
        """Initialise the object."""
        self.columns_with_nulls: dict[str, list[int]] = columns_with_nulls

        error_parts = []
        for column, null_rows in columns_with_nulls.items():
            if len(null_rows) <= CSVConfig.MAX_ROWS_TO_BE_SHOWN_IN_ERROR:
                rows_str: str = str(null_rows)
            else:
                rows_str = (
                    f"{null_rows[: CSVConfig.MAX_ROWS_TO_BE_SHOWN_IN_ERROR]} ... "
                    f"and {len(null_rows) - CSVConfig.MAX_ROWS_TO_BE_SHOWN_IN_ERROR} more rows"
                )
            error_parts.append(f"'{column}' has null values in rows: {rows_str}")

        error_message: str = f"Column comparison contains null values - {'; '.join(error_parts)}."
        super().__init__(message=error_message)


class InvalidComparisonOperatorError(_ValidationError):
    """Raised when an invalid comparison operator is used."""

    def __init__(self, operator: str) -> None:
        """Initialise the object."""
        self.operator: str = operator
        valid_operators = ["==", "!=", "<", "<=", ">", ">="]

        error_message: str = (
            f"Invalid comparison operator '{operator}'. Valid operators are: {valid_operators}."
        )
        super().__init__(message=error_message)


class InvalidInputParameterError(_ValidationError):
    """Raised when a parameter is invalid."""

    def __init__(self, message: str) -> None:
        """Initialise the object."""
        self.message: str = message
        super().__init__(message=message)


class InvalidEngineError(InvalidInputParameterError):
    """Raised when an invalid engine is specified."""

    def __init__(self, engine: str) -> None:
        """Initialise the object."""
        self.engine: str = engine
        error_message: str = (
            f"Invalid engine '{engine}'. Supported engines are 'pandas' and 'polars'."
        )
        super().__init__(message=error_message)


class UnsupportedDataTypeError(InvalidInputParameterError):
    """Raised when an invalid data type is specified in PlatformXDataTypeOverride."""

    def __init__(self, column: str, data_type: str) -> None:
        """Initialise the object."""
        self.column: str = column
        self.data_type: str = data_type

        error_message: str = f"Invalid data type '{data_type}' for column '{column}'. "
        super().__init__(message=error_message)
