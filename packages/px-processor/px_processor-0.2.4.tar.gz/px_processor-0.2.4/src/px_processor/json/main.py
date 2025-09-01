"""Validator module for validating JSON objects."""

from collections.abc import Hashable, Sequence
from typing import Any

from pydantic import BaseModel
from pydantic_core import ErrorDetails, ValidationError

from px_processor.base import BaseValidator
from px_processor.errors import InvalidInputError


class JSONValidator(BaseValidator):
    """Validator for JSON objects.

    Parameters
    ----------
        input_: dict[Hashable, Any]
            The JSON data to validate.

    Raises
    ------
        ValidationError: If the JSON data is invalid.

    """

    def __init__(self, model: type[BaseModel], input_: dict[Hashable, Any]) -> None:
        """Initialise the object.

        Parameters
        ----------
        model: type[BaseModel]
            The Pydantic model to validate the JSON data against.
        input_: dict[Hashable, Any]
            The JSON data that has to be validated.

        Raises
        ------
        InvalidInputError
            If the JSON data is invalid or doesn't match the Pydantic model schema.
        """
        super().__init__()
        self.input: dict[Hashable, Any] = input_
        try:
            string_key_data: dict[str, Any] = {str(key): value for key, value in input_.items()}
            self.data: BaseModel = model(**string_key_data)
        except ValidationError as e:
            self.__add_errors(errors=e.errors())
        self.__generate_error_message()
        if not self.validate():
            raise InvalidInputError(message=self.error_message)

    def __add_errors(self, errors: Sequence[ErrorDetails]) -> None:
        """Process errors."""
        for error in errors:
            self.errors.append(dict(error))

    def __generate_error_message(self) -> None:
        """Generate error message."""
        self.error_message = "\n".join(
            [
                f"{index}. {str(error['type']).title()}: Mandatory field {error['loc'][0]} in input."  # noqa: E501
                for index, error in enumerate(self.errors, start=1)
            ],
        )

    def validate(self) -> bool:
        """Validate JSON data.

        Returns
        -------
            bool: True if the data is valid, False otherwise

        """
        return self.errors == []

    def validate_keys(self) -> None:
        """Validate keys."""

    def validate_values(self) -> None:
        """Validate values."""

    def validate_schema(self) -> None:
        """Validate schema."""

    def validate_types(self) -> None:
        """Validate types."""
