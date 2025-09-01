"""Definition of BaseValidator class."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from pydantic_core import ErrorDetails

from px_processor.errors import _ValidationError


class BaseValidator(ABC):
    """Base class for all validators."""

    def __init__(self) -> None:
        """Initialise the object."""
        super().__init__()
        self.__errors: list[_ValidationError | ErrorDetails | dict[str, Any]] = []
        self.error_message: str = ""

    @abstractmethod
    def validate(self) -> bool:
        """Validate the data."""
        ...

    @abstractmethod
    def validate_keys(self) -> bool | None:
        """Validate the keys of the data."""
        ...

    @abstractmethod
    def validate_values(self) -> bool | None:
        """Validate the values of the data."""
        ...

    @abstractmethod
    def validate_types(self) -> bool | None:
        """Validate the types of the data."""
        ...

    @property
    def errors(self) -> list[_ValidationError | ErrorDetails | dict[str, Any]]:
        """Return the list of errors."""
        return self.__errors

    @errors.setter
    def errors(self, new_error: _ValidationError | ErrorDetails | dict[str, Any]) -> None:
        self.__errors.append(new_error)

    @errors.deleter
    def errors(self) -> None:
        self.__errors.clear()

    def __str__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
            str: A string representation of the object.

        """
        return f"{self.__class__.__name__}({self.__dict__})"

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
            str: A string representation of the object.

        """
        return self.__str__()

    def __bool__(self) -> bool:
        """Return True if there are any errors, False otherwise.

        Returns
        -------
            bool: True if there are any errors, False otherwise.

        """
        return bool(self.__errors)

    def __len__(self) -> int:
        """Return the number of errors.

        Returns
        -------
            int: The number of errors.

        """
        return len(self.__errors)

    def __iter__(self) -> Iterator[_ValidationError | ErrorDetails | dict[str, Any]]:
        """Return an iterator for the errors.

        Returns
        -------
            Iterator[ValidationError]: An iterator for the errors.

        """
        return iter(self.__errors)

    def __contains__(self, error: _ValidationError | ErrorDetails | dict[str, Any]) -> bool:
        """Return True if error is in the list of errors, False otherwise.

        Args:
            error (ValidationError): The error to check.

        Returns
        -------
            bool: True if error is in the list of errors, False otherwise.

        """
        return error in self.__errors

    def __getitem__(self, index: int) -> _ValidationError | ErrorDetails | dict[str, Any]:
        """Return the error at the given index.

        Args:
            index (int): The index of the error to return.

        Returns
        -------
            ValidationError: The error at the given index.

        """
        return self.__errors[index]
