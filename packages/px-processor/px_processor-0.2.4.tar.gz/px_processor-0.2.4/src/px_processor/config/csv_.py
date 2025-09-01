"""CSV configuration rules."""

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings


class PlatformXMapping(BaseModel):
    """Platform-X data type mapping."""

    model_config = ConfigDict(
        strict=False,
        extra="allow",
    )

    integer: str = "int"
    varchar: str = "str"
    character: str = "str"
    numeric: str = "float"
    double: str = "float"
    integer64: str = "int"


class PandasConfig(BaseSettings):
    """Pandas configuration rules."""

    pandas_engine: str = Field(default="pyarrow")
    date_format: str = Field(default="ISO8601")
    max_rows: int = Field(default=10)
    max_columns: int = Field(default=50)
    pandas_dtype_mapping: PlatformXMapping = Field(
        default_factory=PlatformXMapping,
        alias="PANDAS_DTYPE_MAPPING",
    )


class CSVConfig:
    """CSV configuration rules."""

    MAX_ROWS_TO_BE_SHOWN_IN_ERROR: int = 10
    MAX_COLUMNS_TO_BE_SHOWN_IN_ERROR: int = 10
