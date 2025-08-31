from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Module(ABC, Generic[T]):
    """A module is responsible for obtaining a part of the experiment data."""

    @abstractmethod
    def ui(self):
        """Renders the streamlit UI to obtain user-provided input."""
        pass

    @abstractmethod
    def validate(self):
        """Validates the user-provided input. Throws a ValidationError with a
        message if the input is invalid."""
        pass

    @abstractmethod
    def parse(self, *args, **kwargs) -> T:
        """Parses the input and returns a valid object. Throws a ValidationError
        with a message if parsing fails."""
        pass
