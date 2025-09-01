"""Validator module for validating CSV files."""

import concurrent.futures
import operator
from collections.abc import Callable
from importlib import util
from typing import TYPE_CHECKING, Any
from warnings import warn

from px_processor.base import BaseValidator
from px_processor.config import (
    PandasConfig,
    PlatformXMapping,
)
from px_processor.csv import (
    CSVColumnComparatorConstraint,
    CSVColumnValueLimits,
    ComparisonFailure,
    InputDataTypeOverride,
)
from px_processor.errors import (
    ColumnComparisonError,
    ColumnComparisonNullValueError,
    ColumnValueLimitError,
    FixedValueColumnError,
    InvalidDateFormatError,
    InvalidEngineError,
    InvalidInputError,
    InvalidInputParameterError,
    MandatoryColumnError,
    MissingColumnError,
    MissingDataError,
    MissingPathsError,
    UniqueValueError,
)

_HAS_PANDAS: bool = util.find_spec(name="pandas") is not None
_HAS_POLARS: bool = util.find_spec(name="polars") is not None

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl
    from pandas import Series
    from polars import DataFrame, Expr, Schema


class CSVValidator(BaseValidator):
    """
    Validator for CSV files.

    This class validates CSV files for structure, data types, missing values, unique constraints,
    value limits, and column-to-column comparisons. It supports both pandas and polars engines.

    Parameters
    ----------
    csv_paths : list[str]
        List of CSV file paths to validate.
    data_types : list[str]
        List of data types for each column (e.g., "int", "str", "float").
        If any data-type is not provided, it will be set to "str" by default.
    column_names : list[str]
        List of column names to read from the CSV files.
        column_names order should match the order of data_types.
    date_column_suffix: str, optional
            Suffix for date columns. Default is "_date".
    mandatory_columns : list[str], optional
        Columns that must be present in the CSV files.
    unique_value_columns : list[str], optional
        Columns that must have unique values (e.g., primary keys).
    columns_with_no_missing_data : list[str], optional
        Columns that must not have missing values.
    missing_data_column_mapping : dict[str, list[str]], optional
        Mapping of columns to values considered as missing.
        (e.g., {column_name: [missing_value_1, missing_value_2]}).
    valid_column_values : dict[str, list[str]], optional
        Mapping of columns to lists of valid values.
    drop_columns : list[str], optional
        Columns to drop from the CSV files.
    strict_validation : bool, optional
        If True, raises an error if validation fails. Default is True.
    data_frame_engine : str, optional
        DataFrame engine to use: "pandas" or "polars". Auto-detected if not specified.
    pandas_config : PandasConfig, optional
        Configuration for pandas engine. Use only if you want to override the default configuration.
    platform_x_mapping : PlatformXMapping, optional
        Mapping for platform-specific data types.
        Use only if you want to override the default mapping.
    column_value_limits : list[CSVColumnValueLimits], optional
        List of value limits for columns.
        e.g., [CSVColumnValueLimits(column_name="age", min_value=18, max_value=75)].
    column_comparators : list[CSVColumnComparatorConstraint], optional
        List of column comparison constraints.
        e.g.,
        [
            CSVColumnComparatorConstraint(
                left_column="age", operator=">", right_column="yrs_of_experience"
            )
        ].
    input_datatype_overrides : list[InputDataTypeOverride], optional
        List of InputDataTypeOverride objects to override the default Input data type mappings.

    Raises
    ------
    InvalidInputError
        If the CSV data is invalid or validation fails with strict_validation enabled.
    InvalidEngineError
        If the specified dataframe engine is not 'pandas' or 'polars'.
    InvalidInputParameterError
        If the parameters provided are invalid.
    MissingPathsError
            If the list of CSV paths is empty.

    Example
    -------
    ```python

    from px_processor import CSVColumnComparatorConstraint, CSVColumnValueLimits, CSVValidator

    csv_paths = ["data1.csv", "data2.csv"]
    data_types = ["int", "str", "float"]
    column_names = ["id", "name", "age"]
    mandatory_columns = ["id", "name"]
    unique_value_columns = ["id"]
    columns_with_no_missing_data = ["id"]
    missing_data_column_mapping = {"name": ["", "NA"]}
    valid_column_values = {"name": ["Alice", "Bob", "Charlie"]}
    drop_columns = ["unused_column"]

    column_value_limits = [
        CSVColumnValueLimits(column_name="age", min_value=18, max_value=75)
    ]
    column_comparators = [
        CSVColumnComparatorConstraint(left_column="age", operator=">",
        right_column="yrs_of_experience")
    ]

    validator = CSVValidator(
        csv_paths=csv_paths,
        data_types=data_types,
        column_names=column_names,
        mandatory_columns=mandatory_columns,
        unique_value_columns=unique_value_columns,
        columns_with_no_missing_data=columns_with_no_missing_data,
        missing_data_column_mapping=missing_data_column_mapping,
        valid_column_values=valid_column_values,
        drop_columns=drop_columns,
        strict_validation=True,
        data_frame_engine="pandas",
        pandas_config=PandasConfig(),
        platform_x_mapping=PlatformXMapping(),
        column_value_limits=column_value_limits,
        column_comparators=column_comparators,
    )

    if validator.validate():
        print("CSV data is valid!")
    else:
        print("CSV data is invalid:")
        print(validator.error_message)
    ```

    """

    def __init__(
        self,
        *,
        csv_paths: list[str],
        data_types: list[str],
        column_names: list[str],
        date_column_suffix: str = "_date",
        mandatory_columns: list[str] | None = None,
        unique_value_columns: list[str] | None = None,
        columns_with_no_missing_data: list[str] | None = None,
        missing_data_column_mapping: dict[str, list[str]] | None = None,
        valid_column_values: dict[str, list[str]] | None = None,
        drop_columns: list[str] | None = None,
        strict_validation: bool = True,
        data_frame_engine: str | None = None,
        pandas_config: PandasConfig | None = None,
        platform_x_mapping: PlatformXMapping | None = None,
        column_value_limits: list[CSVColumnValueLimits] | None = None,
        column_comparators: list[CSVColumnComparatorConstraint] | None = None,
        input_datatype_overrides: list[InputDataTypeOverride] | None = None,
    ) -> None:
        """Initialise the object.

        Parameters
        ----------
        csv_paths: list[str]
            List of csv paths.
        data_types: list[str]
            List of data types of each columns in the table.
            If any data-type is not provided, it will be set to "str" by default.
        input_datatype_override :  InputDataTypeOverride, optional
            List of InputDataTypeOverride objects to override default Input data type mappings.
            e.g., {"tenor": "int", "cust_id": "str"}.
        column_names: list[str]
            List of column names that should be read from the table.
        date_column_suffix: str, optional
            Suffix for date columns. Default is "_date".
        mandatory_columns: list[str]
            List of mandatory columns that should be present in the table.
        unique_value_columns: list[str], optional
            List of unique value columns.
        columns_with_no_missing_data: list[str], optional
            List of columns with no missing data.
        missing_data_column_mapping: dict[str, list[str]], optional
            Mapping of columns with missing data.
            eg: {column_name: [missing_value1, missing_value2]}.
        valid_column_values: dict[str, list[str]], optional
            Mapping of valid column values.
        data_frame_engine: str, optional
            Dataframe engine to use. Supports 'pandas' and 'polars'.
        drop_columns: list[str], optional
            List of columns to be dropped from original table.
        strict_validation: bool, optional
            Whether to use strict validation. Default is True.
            If strict_validation is True, an error will be raised if validation fails.
            Else, it will just log the errors.
        pandas_config: PandasConfig, optional
            Pandas configuration.
        platform_x_mapping: PlatformXMapping, optional
            Platform-X to Python data-type mapping.
            Use only if you want to override the default mapping.
        column_value_limits: dict[str, tuple[float, float]] | None = None,
            Mapping of column names to their value limits (min, max).
        column_comparators: list[CSVColumnComparatorConstraints] | None = None,
            List of column comparator constraints.
        input_datatype_overrides : list[InputDataTypeOverride], optional
            List of InputDataTypeOverride objects to override the default Input data type mappings.

        Raises
        ------
        InvalidEngineError
            If the specified dataframe engine is not 'pandas' or 'polars'.
        InvalidInputError
            If the CSV data is invalid or validation fails with strict_validation enabled.
        InvalidInputParameterError
            If the parameters provided are invalid.
        MissingPathsError
            If the list of CSV paths is empty.

        """
        super().__init__()
        self._csv_paths: list[str] = csv_paths
        self._engine: str = data_frame_engine or self._auto_detect_engine()
        self._import_engine_module()
        self.platform_x_mapping: PlatformXMapping = platform_x_mapping or PlatformXMapping()
        self.column_value_limits: list[CSVColumnValueLimits] = column_value_limits or []
        self.column_comparators: list[CSVColumnComparatorConstraint] = column_comparators or []
        self._strict_validation: bool = strict_validation
        if not self._csv_paths:
            raise MissingPathsError
        self._data_types: list[str] = data_types
        self._unique_value_columns: list[str] = unique_value_columns or []
        self._drop_columns: list[str] = drop_columns or []
        self._column_names: list[str] = column_names
        self._date_column_suffix: str = date_column_suffix or "_date"
        self.mandatory_columns: list[str] = mandatory_columns or []
        if self.mandatory_columns and not set(self.mandatory_columns).issubset(
            set(self._column_names)
        ):
            missing_columns: list[str] = list(set(self.mandatory_columns) - set(self._column_names))
            self.errors.append(MandatoryColumnError(missing_columns=missing_columns))
        self._read_columns: list[str] = self._make_read_columns()
        self.input_datatype_overrides: list[InputDataTypeOverride] = input_datatype_overrides or []
        self.input_dtype_override_map: dict[str, str] = self._make_input_datatype_override_map()
        self._validate_input_datatype_overrides()
        self._column_schema: dict[str, str] = self._make_column_schema()
        self._date_columns: list[str] = self._make_date_columns()
        if self._engine == "pandas":
            self.data: pd.DataFrame
            self.pandas_config: PandasConfig = pandas_config or PandasConfig()
        elif self._engine == "polars":
            self.lazy_data: pl.LazyFrame
            self._polars_schema: dict[str, pl.DataType] = {}
            self._generate_column_schema_for_polars()
        else:
            raise InvalidEngineError(engine=self._engine)
        self._columns_with_no_missing_data: list[str] = columns_with_no_missing_data or []
        self._missing_data_column_mapping: dict[str, list[str]] = missing_data_column_mapping or {}
        if self._validate_missing_column_conflict():
            raise InvalidInputParameterError(
                message=(
                    "Columns with no missing data cannot be present in the missing data mapping."
                )
            )
        self._valid_column_values: dict[str, list[str]] = valid_column_values or {}
        self._category_columns: list[str] = [column for column in self._valid_column_values]
        self._add_category_columns_in_datatype_mapping()
        self._read()
        if self._engine == "pandas":
            self.number_of_rows: int = len(self.data)
        self.data_columns: set[str] = self._make_data_columns()
        self.__analyse()
        if self._engine == "polars":
            self.data = self.lazy_data.collect().to_pandas(
                use_pyarrow_extension_array=True,
                categories=self._category_columns,
                date_as_object=False,
            )
        self._generate_error_message()
        if not self.validate() and self._strict_validation:
            raise InvalidInputError(message=self.error_message)

    @staticmethod
    def _auto_detect_engine() -> str:
        """Pick the first available engine, or fail if none.

        Returns
        -------
        str
            The name of the engine to use. Either "polars" or "pandas".

        Raises
        ------
        ImportError
            If neither polars nor pandas is installed.
        """
        if _HAS_POLARS:
            return "polars"
        if _HAS_PANDAS:
            if not _HAS_POLARS:
                warning_message: str = """
                Polars is not installed, using pandas as the default engine.\n
                If you want to use polars, please install it with `pip install polars`.\n
                Polars provides better performance and compatibility.\n
                """
                warn(
                    message=warning_message,
                    category=RuntimeWarning,
                    stacklevel=2,
                )
            return "pandas"
        error_message: str = "You must install either 'pandas' or 'polars' to use CSVValidator."
        raise ImportError(error_message)

    def _import_engine_module(self) -> None:
        """Import the selected engine module (pandas or polars).

        Raises
        ------
        ImportError
            If neither polars nor pandas is installed.
        ValueError
            If the specified engine is not supported.
        """
        error_: str = ""
        if self._engine == "pandas":
            try:
                import pandas as pd  # noqa: PLC0415
            except ImportError as e:
                error_ = "Engine 'pandas' was selected, but pandas is not installed."
                raise ImportError(error_) from e
            self.pd = pd

        elif self._engine == "polars":
            try:
                import polars as pl  # noqa: PLC0415
            except ImportError as e:
                error_ = "Engine 'polars' was selected, but polars is not installed."
                raise ImportError(error_) from e
            self.pl = pl

        else:
            error_ = f"Engine {self._engine!r} was selected, but it is not supported."
            raise ValueError(error_)

    def _generate_column_schema_for_polars(self) -> None:
        """Modify the column schema for polars."""
        for column in self._column_schema:
            if self._column_schema[column] == "int":
                self._polars_schema[column] = self.pl.Int64()
            elif self._column_schema[column] == "float":
                self._polars_schema[column] = self.pl.Float64()
            elif self._column_schema[column] == "str":
                self._polars_schema[column] = self.pl.Utf8()
            elif self._column_schema[column] == "category":
                self._polars_schema[column] = self.pl.Categorical()

    def _add_category_columns_in_datatype_mapping(self) -> None:
        """Add category columns in datatype mapping."""
        for column in self._category_columns:
            self._column_schema[column] = "category"

    def _add_date_columns_in_polars_schema(self) -> None:
        """Add date columns in polars schema."""
        for column in self._date_columns:
            self._polars_schema[column] = self.pl.Date()

    def _validate_missing_column_conflict(self) -> bool:
        """Validate missing_column conflicts.

        Checks for conflicts between columns listed in
        both missing_data_column_mapping and columns_with_no_missing_data.

        Returns
        -------
        bool
            True if there is a conflict, False otherwise.
        """
        if self._columns_with_no_missing_data:
            for column in self._columns_with_no_missing_data:
                if column in self._missing_data_column_mapping:
                    return True
        return False

    def _make_read_columns(self) -> list[str]:
        """Make the list of columns to read from the CSV files.

        Returns
        -------
        list[str]
            List of columns to read from the CSV files.
        """
        return [
            column_name
            for column_name in self._column_names
            if column_name not in self._drop_columns
        ]

    def _make_date_columns(self) -> list[str]:
        """Make the list of date columns.

        Returns
        -------
        list[str]
            List of date columns.
        """
        return [
            column_name
            for column_name in self._column_names
            if self._date_column_suffix in column_name.lower()
        ]

    def _read(self) -> None:
        """Read the CSV data.

        This method reads the CSV data using the specified engine (pandas or polars).

        Raises
        ------
        ValueError
            If the engine is neither 'pandas' nor 'polars'.
        """
        if self._engine.lower() == "pandas":
            self.data = self._read_with_pandas()
        elif self._engine.lower() == "polars":
            self._read_with_polars()
        else:
            error_message: str = f"Invalid dataframe engine: {self._engine}"
            raise ValueError(error_message)

    def _read_with_pandas(self):  # noqa: ANN202
        """Read CSV files using pandas engine.

        Returns
        -------
        pd.DataFrame
            Combined dataframe from all CSV files

        """
        if len(self._csv_paths) > 1:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                dataframes = list(executor.map(self._read_single_file, self._csv_paths))
        else:
            dataframes = [self._read_single_file(self._csv_paths[0])]

        return self.pd.concat(dataframes, ignore_index=True)

    def _read_single_file(self, csv_path: str):  # noqa: ANN202
        """Read a single CSV file using pandas.

        Parameters
        ----------
        csv_path : str
            Path to the CSV file

        Returns
        -------
        pd.DataFrame
            DataFrame containing the CSV data

        Raises
        ------
        ValueError
            If pandas_engine is invalid

        """

        def _datetime_converter() -> dict[Any, Callable[[str], Any]]:
            """Convert the string column to datetime columns.

            Returns
            -------
                dict[Any, Callable[..., Any]]: Dictionary of date columns.

            """
            return {
                date_column: lambda element: self.pd.to_datetime(
                    arg=element,
                    errors="coerce",
                    format=self.pandas_config.date_format,
                )
                for date_column in self._date_columns
            }

        if self.pandas_config.pandas_engine == "c":
            return self.pd.read_csv(
                filepath_or_buffer=csv_path,
                engine=self.pandas_config.pandas_engine,
                dtype=self._column_schema,
                dtype_backend="pyarrow",
                date_format=self.pandas_config.date_format,
                parse_dates=self._date_columns,
                na_values=self._missing_data_column_mapping,
                converters=_datetime_converter(),
                memory_map=True,
                usecols=self._read_columns,
            )
        if self.pandas_config.pandas_engine == "pyarrow":
            return self.pd.read_csv(
                filepath_or_buffer=csv_path,
                engine=self.pandas_config.pandas_engine,
                dtype=self._column_schema,
                dtype_backend="pyarrow",
                date_format=self.pandas_config.date_format,
                parse_dates=self._date_columns,
                usecols=self._read_columns,
            )
        error_message: str = f"Invalid pandas engine: {self.pandas_config.pandas_engine}"
        raise ValueError(error_message)

    def _read_with_polars(self) -> None:
        """Read CSV files using polars engine."""
        self.lazy_data = self.pl.scan_csv(
            source=self._csv_paths,
            rechunk=True,
            schema_overrides=self._polars_schema,
        ).drop(self._drop_columns)

        if self._missing_data_column_mapping:
            self._handle_missing_data_polars()

    def _handle_missing_data_polars(self) -> None:
        """Handle missing data replacement in polars."""
        expressions = []
        for column, null_values in self._missing_data_column_mapping.items():
            if column in set(self._polars_schema.keys()).union(self._date_columns):
                expression = self.pl.col(column).map_elements(
                    lambda x, nvalues=null_values: None if x in nvalues else x,
                    return_dtype=(
                        self._polars_schema[column]
                        if column in self._polars_schema
                        else self.pl.Utf8()
                    ),
                )
                expressions.append(expression)

        if expressions:
            self.lazy_data = self.lazy_data.with_columns(expressions)

    def validate(self) -> bool:
        """Validate the CSV data.

        Returns
        -------
            bool: True if the data is valid, False otherwise.

        """
        return self.errors == []

    def _make_data_columns(self) -> set[str]:
        return (
            set(self.data.columns.tolist())
            if self._engine == "pandas"
            else set(self.lazy_data.collect_schema().names())
        )

    def __analyse(self) -> None:
        """Validate the CSV data."""
        if self._date_columns:
            self._check_date_format()
        if self._columns_with_no_missing_data:
            self._check_missing_data()
        if self._valid_column_values:
            self._check_fixed_column_values()
        if self._unique_value_columns:
            self._check_unique_values()
        if self.column_value_limits:
            self._check_column_value_limits()
        if self.column_comparators:
            self._check_column_comparisons()

    def validate_keys(self) -> bool | None:
        """Validate keys."""

    def validate_types(self) -> bool | None:
        """Validate types."""

    def validate_values(self) -> bool | None:
        """Validate values."""

    def _check_date_format(self) -> None:
        """Validate that date columns follow the expected ISO8601 format."""
        if self._engine == "pandas":
            self._check_date_format_pandas()
        elif self._engine == "polars":
            self._check_date_format_polars()

    def _check_date_format_pandas(self) -> None:
        """Check date format validation for pandas."""
        valid_dtypes: set[str] = {
            "datetime64[ns]",
            "datetime64[ns, tz]",
            "date32[day][pyarrow]",
        }
        for column in self._date_columns:
            if column not in self.data_columns:
                self.errors.append(MissingColumnError(column=column))
                continue
            if (
                self.data[column].dtype.name not in valid_dtypes
                and column in self._columns_with_no_missing_data
            ):
                self.errors.append(InvalidDateFormatError(column=column))

    def _check_date_format_polars(self) -> None:
        """Check date format validation for polars."""
        schema: Schema = self.lazy_data.collect_schema()
        for column in self._date_columns:
            if column not in schema:
                self.errors.append(MissingColumnError(column=column))
                continue
            missing_dataframe: DataFrame = (
                self.lazy_data.with_row_index(name="index")
                .filter(self.pl.col(name=column).is_null())
                .collect()
            )
            if column in self._columns_with_no_missing_data or missing_dataframe.height == 0:
                try:
                    self.lazy_data.with_columns(self.pl.col(column).str.to_date()).collect()
                except (
                    self.pl.exceptions.ComputeError,
                    self.pl.exceptions.InvalidOperationError,
                ):
                    self.errors.append(InvalidDateFormatError(column=column))
                else:
                    self.lazy_data = self.lazy_data.with_columns(self.pl.col(column).str.to_date())

    def _check_missing_data(self) -> None:
        """Validate the missing data."""
        if self._engine == "pandas":
            for column in self._columns_with_no_missing_data:
                if column in self.data_columns:
                    missing_mask = self.data[column].isna()
                    if missing_mask.any():
                        error_rows: list[Any] = self.data.index[missing_mask].tolist()
                        self.errors.append(
                            MissingDataError(
                                column=column,
                                rows=error_rows,
                            ),
                        )
                else:
                    self.errors.append(
                        MissingColumnError(
                            column=column,
                        ),
                    )
        elif self._engine == "polars":
            for column in self._columns_with_no_missing_data:
                if column in self.data_columns:
                    missing_dataframe: DataFrame = (
                        self.lazy_data.with_row_index(name="index")
                        .filter(self.pl.col(name=column).is_null())
                        .collect()
                    )
                    if missing_dataframe.height > 0:
                        error_rows = missing_dataframe["index"].to_list()
                        self.errors.append(
                            MissingDataError(
                                column=column,
                                rows=error_rows,
                            ),
                        )

    def _check_fixed_column_values(self) -> None:
        """Validate the fixed column values."""
        if self._engine == "pandas":
            for column, valid_values in self._valid_column_values.items():
                self._validate_single_column(column, valid_values)
        elif self._engine == "polars":
            for column, valid_values in self._valid_column_values.items():
                if column in self.data_columns:
                    invalid_rows: DataFrame = self.lazy_data.filter(
                        ~self.pl.col(name=column).is_in(other=valid_values)
                    ).collect()
                    if invalid_rows.height > 0:
                        self.errors.append(
                            FixedValueColumnError(
                                column=column,
                                valid_values=valid_values,
                            ),
                        )
                else:
                    self.errors.append(MissingColumnError(column=column))

    def _validate_single_column(
        self,
        column: str,
        valid_values: list[str],
    ) -> None:
        """Validate a single column.

        Parameters
        ----------
        column: tuple[str, list[str]]
            Tuple of column name and valid values.
        valid_values: list[str]
            List of valid values.

        """
        if column not in self.data_columns:
            self.errors.append(MissingColumnError(column=column))
            return

        if not self.data[column].isin(values=valid_values).all():
            self.errors.append(FixedValueColumnError(column=column, valid_values=valid_values))

    def _check_unique_values(self) -> None:
        """Validate the unique values."""
        if self._engine == "pandas":
            for column in self._unique_value_columns:
                if self.data[column].nunique() != self.number_of_rows:
                    self.errors.append(
                        UniqueValueError(column=column),
                    )
        elif self._engine == "polars":
            exprs = [
                self.pl.col(column).n_unique().alias(column)
                for column in self._unique_value_columns
            ]
            exprs.append(self.pl.len().alias("total_rows"))
            result = self.lazy_data.select(exprs).collect()
            total_rows = result["total_rows"][0]
            for column in self._unique_value_columns:
                if result[column][0] != total_rows:
                    self.errors.append(UniqueValueError(column=column))

    def _check_column_value_limits(self) -> None:
        """Validate the column value limits."""
        if self.column_value_limits:
            for column_value_limit in self.column_value_limits:
                if column_value_limit.column_name not in self.data_columns:
                    self.errors.append(MissingColumnError(column=column_value_limit.column_name))
                    continue

                if self._engine == "pandas":
                    column_data = self.data[column_value_limit.column_name]
                    min_value = column_data.min() or column_value_limit.min_value
                    max_value = column_data.max() or column_value_limit.max_value
                    if not column_data.between(
                        left=min_value,
                        right=max_value,
                        inclusive="both",
                    ).all():
                        self.errors.append(
                            InvalidInputError(
                                message=f"Values in '{column_value_limit.column_name}' "
                                f"should be between {column_value_limit.min_value} "
                                f"and {column_value_limit.max_value}.",
                            ),
                        )
                elif self._engine == "polars":
                    validation_result: DataFrame = self.lazy_data.select([
                        self.pl.col(column_value_limit.column_name).min().alias("computed_min"),
                        self.pl.col(column_value_limit.column_name).max().alias("computed_max"),
                        self.pl.col(column_value_limit.column_name)
                        .is_between(
                            lower_bound=(
                                column_value_limit.min_value
                                if column_value_limit.min_value is not None
                                else self.pl.col(column_value_limit.column_name).min()
                            ),
                            upper_bound=(
                                column_value_limit.max_value
                                if column_value_limit.max_value is not None
                                else self.pl.col(column_value_limit.column_name).max()
                            ),
                            closed="both",
                        )
                        .not_()
                        .sum()
                        .alias("out_of_range_count"),
                    ]).collect()

                    out_of_range_count = validation_result["out_of_range_count"][0]

                    if out_of_range_count > 0:
                        self.errors.append(
                            ColumnValueLimitError(
                                column=column_value_limit.column_name,
                                min_value=column_value_limit.min_value,
                                max_value=column_value_limit.max_value,
                            )
                        )

    def _check_column_comparisons(self) -> None:
        """Validate column comparisons."""
        self._comparison_operators = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
        }

        if self._engine == "pandas":
            self._check_column_comparisons_pandas()
        elif self._engine == "polars":
            self._check_column_comparisons_polars()

    def _check_column_comparisons_pandas(self) -> None:
        """Process column comparisons for pandas engine."""
        columns_with_nulls: dict[str, list[int]] = {}
        comparison_failures: list[ComparisonFailure] = []

        for comparator in self.column_comparators:
            null_info: dict[str, Series[Any] | Series[bool]] = self._check_nulls_pandas(
                comparator=comparator,
                columns_with_nulls=columns_with_nulls,
            )
            self._evaluate_comparison_pandas(
                comparator=comparator,
                null_info=null_info,
                comparison_failures=comparison_failures,
            )

        self._generate_comparison_errors(
            columns_with_nulls=columns_with_nulls,
            comparison_failures=comparison_failures,
        )

    def _check_nulls_pandas(
        self,
        comparator: CSVColumnComparatorConstraint,
        columns_with_nulls: dict[str, list[int]],
    ) -> dict[str, "Series[Any] | Series[bool]"]:
        """Check for null values in comparison columns.

        Parameters
        ----------
        comparator: CSVColumnComparatorConstraints
            The comparator object containing the left and right column names.
        columns_with_nulls: dict[str, list[int]]
            Dictionary to store columns with null values and their respective row indices.

        Returns
        -------
        dict[str, Series[Any] | Series[bool]]
            Dictionary containing the left and right columns as Series, and a mask for
            non-null rows.

        """
        left_column = self.data[comparator.left_column]
        right_column = self.data[comparator.right_column]

        left_null_mask: Series[bool] = left_column.isna()
        right_null_mask: Series[bool] = right_column.isna()

        if left_null_mask.any():
            columns_with_nulls.setdefault(comparator.left_column, []).extend(
                self.data.index[left_null_mask].tolist()
            )

        if right_null_mask.any():
            columns_with_nulls.setdefault(comparator.right_column, []).extend(
                self.data.index[right_null_mask].tolist()
            )

        return {
            "left_col": left_column,
            "right_col": right_column,
            "non_null_mask": ~(left_null_mask | right_null_mask),
        }

    def _evaluate_comparison_pandas(
        self,
        comparator: CSVColumnComparatorConstraint,
        null_info: dict[str, "Series[Any] | Series[bool]"],
        comparison_failures: list[ComparisonFailure],
    ) -> None:
        """Evaluate comparison for non-null rows."""
        if not null_info["non_null_mask"].any():
            return

        comparison_result = self._comparison_operators[comparator.operator](
            null_info["left_col"][null_info["non_null_mask"]],
            null_info["right_col"][null_info["non_null_mask"]],
        )

        failed_indices = self.data.index[null_info["non_null_mask"]][~comparison_result]

        if len(failed_indices) > 0:
            comparison_failures.append({
                "comparator": comparator,
                "failed_rows": failed_indices.tolist(),
            })

    def _check_column_comparisons_polars(self) -> None:
        """Process column comparisons for polars engine."""
        expressions: list[Expr] = self._build_comparison_expressions_polars()
        result: DataFrame = self.lazy_data.select(expressions).collect()

        columns_to_check: set[str] = {
            col for comp in self.column_comparators for col in [comp.left_column, comp.right_column]
        }

        columns_with_nulls: dict[str, list[int]] = self._extract_null_rows_polars(
            result, columns_to_check
        )
        comparison_failures: list[ComparisonFailure] = self._extract_comparison_failures_polars(
            result
        )

        self._generate_comparison_errors(
            columns_with_nulls=columns_with_nulls,
            comparison_failures=comparison_failures,
        )

    def _build_comparison_expressions_polars(self) -> list["Expr"]:
        """Build polars expressions for all comparisons.

        Returns
        -------
        list[Expr]
            List of polars expressions for the comparisons.

        """
        expressions: list[Expr] = [self.pl.int_range(self.pl.len()).alias("row_idx")]
        columns_to_check: set[str] = set()

        for index, comparator in enumerate(self.column_comparators):
            left: Expr = self.pl.col(comparator.left_column)
            right: Expr = self.pl.col(comparator.right_column)

            columns_to_check.add(comparator.left_column)
            columns_to_check.add(comparator.right_column)

            null_check: Expr = (left.is_null() | right.is_null()).alias(f"has_null_{index}")
            comparison: Expr = self._comparison_operators[comparator.operator](left, right)
            comp_fail: Expr = (~null_check & ~comparison).alias(f"comp_fail_{index}")

            expressions.extend([null_check, comp_fail])

        expressions.extend([
            self.pl.col(col).is_null().alias(f"null_{col}") for col in columns_to_check
        ])

        return expressions

    def _extract_null_rows_polars(
        self,
        result: "DataFrame",
        columns_to_check: set[str],
    ) -> dict[str, list[int]]:
        """Extract null row information from polars result.

        Parameters
        ----------
        result: DataFrame
            Polars DataFrame containing the results of the comparisons.
        columns_to_check: set[str]
            Set of columns to check for null values.

        Returns
        -------
        dict[str, list[int]]
            Dictionary mapping column names to lists of row indices where null values were found.

        """
        columns_with_nulls = {}
        for col in columns_to_check:
            null_rows = result.filter(self.pl.col(f"null_{col}"))["row_idx"].to_list()
            if null_rows:
                columns_with_nulls[col] = null_rows
        return columns_with_nulls

    def _extract_comparison_failures_polars(self, result: "DataFrame") -> list[ComparisonFailure]:
        """Extract comparison failure information from polars result.

        Parameters
        ----------
        result: DataFrame
            Polars DataFrame containing the results of the comparisons.

        Returns
        -------
        list[dict[str, list[int] | CSVColumnComparatorConstraints]]
            List of dictionaries containing comparator and failed rows.
            Each dictionary has the structure:
            {
                "comparator": CSVColumnComparatorConstraints,
                "failed_rows": list[int]
            }

        """
        comparison_failures: list[ComparisonFailure] = []
        for index, comparator in enumerate(self.column_comparators):
            failed_rows = result.filter(self.pl.col(f"comp_fail_{index}"))["row_idx"].to_list()
            if failed_rows:
                comparison_failures.append(
                    ComparisonFailure(comparator=comparator, failed_rows=failed_rows)
                )
        return comparison_failures

    def _generate_comparison_errors(
        self,
        columns_with_nulls: dict[str, list[int]],
        comparison_failures: list[ComparisonFailure],
    ) -> None:
        """Generate error objects for null values and comparison failures."""
        if columns_with_nulls:
            columns_with_nulls = {
                column: sorted(set(rows)) for column, rows in columns_with_nulls.items()
            }

            self.errors.append(
                ColumnComparisonNullValueError(columns_with_nulls=columns_with_nulls)
            )

        for failure in comparison_failures:
            self.errors.append(
                ColumnComparisonError(
                    left_column=failure["comparator"].left_column,
                    operator=failure["comparator"].operator,
                    right_column=failure["comparator"].right_column,
                    failed_rows=failure["failed_rows"],
                )
            )

    def _generate_error_message(self) -> None:
        """Generate error message."""
        self.error_message = "\n".join(
            [f"{index}. {error_}" for index, error_ in enumerate(self.errors, start=1)],
        )

    def _get_integer_columns(self) -> list[str]:
        """Get integer columns.

        Returns
        -------
            list[str]: List of integer columns.

        """
        return self.data.select_dtypes(include="integer").columns.tolist()

    def _make_input_datatype_override_map(self) -> dict[str, str]:
        """Create a mapping of input data type overrides.

        Returns
        -------
        dict[str, str]
            A dictionary mapping column names to their overridden data types.
        """
        return {override.column: override.data_type for override in self.input_datatype_overrides}

    def _validate_input_datatype_overrides(self) -> None:
        """Validate input data type overrides.

        Raises
        ------
        InvalidInputParameterError
            If any column in input_datatype_override does not exist in column_names.
        """
        if self.input_dtype_override_map:
            invalid_keys: set[str] = set(self.input_dtype_override_map) - set(self._column_names)
            if invalid_keys:
                invalid_cols: str = ", ".join(f"'{col}'" for col in invalid_keys)
                raise InvalidInputParameterError(
                    message=(
                        f"Column(s) {invalid_cols} specified in input_dtype_override "
                        "are not present in column_names."
                    )
                )

    def _make_column_schema(self) -> dict[str, str]:
        """Create a mapping of column names to their data types.

        Returns
        -------
        dict[str, str]
            A dictionary mapping column names to their data types.
        """
        return {
            column_name: (
                self.input_dtype_override_map[column_name]
                if column_name in self.input_dtype_override_map
                else self.platform_x_mapping.model_dump().get(data_type, "str")
            )
            for column_name, data_type in zip(self._column_names, self._data_types, strict=True)
            if self._date_column_suffix not in column_name.lower()
            and column_name not in self._drop_columns
        }
