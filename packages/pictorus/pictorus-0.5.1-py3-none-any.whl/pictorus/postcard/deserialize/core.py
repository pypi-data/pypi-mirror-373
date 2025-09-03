from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Union


class PostcardItem(ABC):
    """
    Base class for all Postcard serializable items.
    """

    @classmethod
    @abstractmethod
    def is_type(cls, schema_item: str) -> bool:
        """Check if the schema entry is of this PostcardItem type."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def deserialize(self, bytes: bytearray) -> Any:
        """
        Deserialize the given byte stream into a Python object.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    @abstractmethod
    def from_schema(cls, schema_item: str) -> Any:
        """
        Create an instance of PostcardData from a schema item.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class PostcardData(PostcardItem):
    """
    Base class for non-divisible data types like integers and floats.
    """

    def __init__(self):
        super().__init__()

    @classmethod
    @abstractmethod
    def get_type(cls, schema_item: str) -> Any:
        """
        Get the type of the PostcardData based on the schema item.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class PostcardList(PostcardItem):
    """Represents a list of PostcardData items, for example a Vec or a
    statically allocated array."""

    def __init__(self, inner: PostcardData):
        self._inner = inner


class PostcardContainer(PostcardItem):
    """Represents something like an Option that can contain a variety of objects."""

    def __init__(self, inner: Union[PostcardData, PostcardList, PostcardContainer]):
        self._inner = inner

    @classmethod
    @abstractmethod
    def from_schema(cls, schema_item: str) -> Union[PostcardContainer, PostcardData, PostcardList]:
        """
        Create an instance of PostcardContainer from a schema item.
        """
        raise NotImplementedError("Subclasses must implement this method.")
