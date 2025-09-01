"""Helper classes and functions for CSV processing."""

from datetime import datetime
from typing import ClassVar, TypedDict

from px_processor.errors import (
    ColumnComparisonDataTypeError,
    InvalidComparisonOperatorError,
    MissingColumnError,
    UnsupportedDataTypeError,
)


class CSVColumnValueLimits:
    """Class to define limits for column values in a CSV file.

    Parameters
    ----------
        column_name (str): The name of the column.
        min_value (float | datetime | str | None): The minimum value allowed for the column
        or None if no limit is set.
        max_value (float | datetime | str | None): The maximum value allowed for the column
        or None if no limit is set.

    Raises
    ------
        TypeError: If column_name is not a string.
        ValueError: If the minimum value is greater than the maximum value.

    Usage:
        >>> limits = CSVColumnValueLimits("age", 0, 100)
        >>> print(limits)
        Column: age, Min: 0, Max: 100
        >>> limits.convert_values_from_string()
        >>> print(limits.min_value, limits.max_value)
        0.0 100.0
        >>> limits = CSVColumnValueLimits("date", "2023-01-01", "2023-12-31")
        >>> limits.convert_values_from_string()
        >>> print(limits.min_value, limits.max_value)
        2023-01-01 00:00:00 2023-12-31 00:00:00

    """

    def __init__(
        self,
        column_name: str,
        min_value: float | datetime | str | None = None,
        max_value: float | datetime | str | None = None,
    ) -> None:
        """Initialise the object.

        Parameters
        ----------
        column_name (str):
            The name of the column.
        min_value (float | datetime | str | None):
            The minimum value allowed for the column or None if no limit is set.
        max_value (float | datetime | str | None):
            The maximum value allowed for the column or None if no limit is set.

        Raises
        ------
        TypeError
            If column_name is not a string.
            If min_value or max_value are not of type float, datetime, str, or None.
        ValueError
            If min_value is greater than max_value when both are set.
            If column_name is empty.
        """
        self.column_name: str = column_name
        self.min_value: float | datetime | None = CSVColumnValueLimits._convert_values_from_string(
            min_value
        )
        self.max_value: float | datetime | None = CSVColumnValueLimits._convert_values_from_string(
            max_value
        )
        error_: str = ""
        if self.min_value is not None and self.max_value is not None:
            if type(self.min_value) is not type(self.max_value):
                error_ = (
                    f"Cannot compare values of different types: "
                    f"min_value is {type(self.min_value).__name__}, "
                    f"max_value is {type(self.max_value).__name__} "
                    f"for column '{self.column_name}'."
                )
                raise TypeError(error_)
            if isinstance(self.min_value, float) and isinstance(self.max_value, float):
                if self.min_value > self.max_value:
                    error_ = (
                        f"Minimum value {self.min_value} cannot be greater than "
                        f"maximum value {self.max_value} for column '{self.column_name}'."
                    )
                    raise ValueError(error_)
            elif isinstance(self.min_value, datetime) and isinstance(self.max_value, datetime):
                if self.min_value > self.max_value:
                    error_ = (
                        f"Minimum date {self.min_value} cannot be greater than "
                        f"maximum date {self.max_value} for column '{self.column_name}'."
                    )
                    raise ValueError(error_)
            else:
                error_ = (
                    f"Unsupported type for min_value and max_value: "
                    f"{type(self.min_value).__name__} for column '{self.column_name}'."
                )
                raise TypeError(error_)

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
            str: A string representation of the object.

        """
        return (
            f"CSVColumnValueLimits(column_name={self.column_name}, "
            f"min_value={self.min_value}, max_value={self.max_value})"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the object.

        Returns
        -------
            str: A user-friendly string representation of the object.

        """
        return f"Column: {self.column_name}, Min: {self.min_value}, Max: {self.max_value}"

    def _asdict(self) -> dict[str, float | datetime | str | None]:
        """Convert the object to a dictionary.

        Returns
        -------
            dict: A dictionary representation of the object.

        """
        return {
            "column_name": self.column_name,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }

    @staticmethod
    def _convert_values_from_string(
        value: float | datetime | str | None,
    ) -> float | datetime | None:
        """Convert string values to appropriate types.

        Parameters
        ----------
        value (float | datetime | str | None):
            The value to convert. Can be a string to convert,
            an already converted float/datetime, or None.

        Returns
        -------
        float | datetime | None:
            The converted value, or None if the input is None.
            - String numbers are converted to float
            - ISO format strings are converted to datetime
            - Existing float/datetime values are returned as-is

        Raises
        ------
        TypeError
            If the string value cannot be converted to float or datetime,
            or if the input type is not supported.

        Examples
        --------
        >>> _convert_values_from_string("123.45")
        123.45
        >>> _convert_values_from_string("2023-01-01")
        datetime(2023, 1, 1)
        >>> _convert_values_from_string(None)
        None

        """
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return datetime.fromisoformat(value)
        elif isinstance(value, (datetime, float)):
            return value
        else:
            error_: str = f"Unsupported type for value: {type(value).__name__}."
            raise TypeError(error_)


class CSVColumnComparatorConstraint:
    """Class to define column comparison constraints for CSV validation.

    This class validates that comparison operations between columns can be performed
    and stores the constraint information for later use in validation.

    Parameters
    ----------
        left_column (str): The name of the left column in the comparison.
        operator (str): The comparison operator (==, !=, <, <=, >, >=).
        right_column (str): The name of the right column in the comparison.

    Usage:
        >>> constraint = CSVColumnComparatorConstraints(
        ...     left_column="MATURITY_DATE",
        ...     operator=">=",
        ...     right_column="NEXT_INTEREST_PAY_DATE",
        ...     column_names=["MATURITY_DATE", "NEXT_INTEREST_PAY_DATE"],
        ...     data_types=["date", "date"]
        ... )
        >>> print(constraint)
        Column Comparison: MATURITY_DATE >= NEXT_INTEREST_PAY_DATE

    """

    VALID_OPERATORS: ClassVar[set[str]] = {"==", "!=", "<", "<=", ">", ">="}
    COMPARABLE_TYPE_GROUPS: ClassVar[list[set[str]]] = [
        {"int", "float"},
        {"date", "datetime"},
        {"str", "category"},
    ]

    def __init__(
        self,
        left_column: str,
        operator: str,
        right_column: str,
        column_names: list[str],
        data_types: list[str],
    ) -> None:
        """Initialise the column comparator constraints.

        Parameters
        ----------
        left_column : str
            The name of the left column in the comparison.
        operator : str
            The comparison operator (==, !=, <, <=, >, >=).
        right_column : str
            The name of the right column in the comparison.
        column_names : list[str]
            List of all column names in the dataset.
        data_types : list[str]
            List of data types corresponding to column_names.

        Raises
        ------
        InvalidComparisonOperatorError
            If the operator is not one of the valid comparison operators.
        MissingColumnError
            If either the left or right column does not exist in the dataset.
        ColumnComparisonDataTypeError
            If the data types of the left and right columns are not comparable.

        """
        self.left_column: str = left_column
        self.operator: str = operator
        self.right_column: str = right_column

        if operator not in self.VALID_OPERATORS:
            raise InvalidComparisonOperatorError(operator=operator)

        if left_column not in column_names:
            raise MissingColumnError(column=left_column)
        if right_column not in column_names:
            raise MissingColumnError(column=right_column)

        left_column_index: int = column_names.index(left_column)
        right_column_index: int = column_names.index(right_column)
        left_data_type: str = data_types[left_column_index]
        right_data_type: str = data_types[right_column_index]

        if not self._are_types_comparable(left_data_type, right_data_type):
            raise ColumnComparisonDataTypeError(
                left_column=left_column,
                left_type=left_data_type,
                right_column=right_column,
                right_type=right_data_type,
            )

        self.left_data_type: str = left_data_type
        self.right_data_type: str = right_data_type

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
        str
            A string representation of the object.

        """
        return (
            f"CSVColumnComparatorConstraints(left_column={self.left_column}, "
            f"operator={self.operator}, right_column={self.right_column})"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the object.

        Returns
        -------
        str
            A user-friendly string representation of the object.

        """
        return f"Column Comparison: {self.left_column} {self.operator} {self.right_column}"

    def _are_types_comparable(self, left_type: str, right_type: str) -> bool:
        """Check if two data types are comparable.

        Parameters
        ----------
        left_type : str
            The data type of the left column.
        right_type : str
            The data type of the right column.

        Returns
        -------
        bool
            True if the types are comparable, False otherwise.

        """
        if left_type == right_type:
            return True

        for type_group in self.COMPARABLE_TYPE_GROUPS:
            if left_type in type_group and right_type in type_group:
                return True

        return False

    def _asdict(self) -> dict[str, str]:
        """Convert the object to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the object.

        """
        return {
            "left_column": self.left_column,
            "operator": self.operator,
            "right_column": self.right_column,
            "left_data_type": self.left_data_type,
            "right_data_type": self.right_data_type,
        }


class ComparisonFailure(TypedDict):
    """TypedDict for storing comparison failure details.

    This class is used to represent a failure in a column comparison operation.

    Parameters
    ----------
        comparator (CSVColumnComparatorConstraints): The comparator constraints that failed.
        failed_rows (list[int]): List of row indices where the comparison failed.

    """

    comparator: CSVColumnComparatorConstraint
    failed_rows: list[int]


class InputDataTypeOverride:
    """Initialise the object.

    Parameters
    ----------
    column : str
        The column name.
    data_type : str
        The data type for the column.

    Raises
    ------
    ValueError
        If the data_type is not in VALID_DTYPES.
    """

    VALID_DTYPES: ClassVar[set[str]] = {
        "str",
        "int",
        "bool",
        "float",
        "date",
        "timedatetime",
        "timedelta",
        "list",
        "tuple",
        "dict",
        "set",
        "None",
    }

    def __init__(
        self,
        column: str,
        data_type: str,
    ) -> None:
        self.column: str = column
        self.data_type: str = data_type

        if data_type not in self.VALID_DTYPES:
            raise UnsupportedDataTypeError(column=self.column, data_type=self.data_type)

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
        str
            A string representation of the object.

        """
        return f"PlatformXDataTypeOverride(column={self.column}, data_type={self.data_type})"

    def __str__(self) -> str:
        """Return a user-friendly string representation of the object.

        Returns
        -------
        str
            A user-friendly string representation of the object.

        """
        return f"Data Type Override: {self.column} : {self.data_type}"
