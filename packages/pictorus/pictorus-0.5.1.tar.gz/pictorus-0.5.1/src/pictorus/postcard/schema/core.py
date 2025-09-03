from abc import ABC
from typing import Any


class Schema(ABC):
    def convert(self, bytes: bytearray) -> Any:
        """
        Convert the Postcard bytearray into a Python object. How the Rust struct is
        represented in Python is up to the implementation of this class.
        """
        raise NotImplementedError("Subclasses must implement this method.")
