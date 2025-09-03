from typing import Any, Dict, List, Tuple, Union

from pictorus.postcard.schema.core import Schema
from ..deserialize.core import PostcardData, PostcardList, PostcardContainer
from ..deserialize.varint import (
    SignedVarint,
    UnsignedVarint,
)
from ..deserialize.float import Float
from ..deserialize.vec import Vec
from ..deserialize.string import StaticString
from ..deserialize.option import Option
from ..deserialize.array import Array


class JsonSchema(Schema):
    """
    Maps a JSON object that is a Rust struct into the corresponding
    instructions for decoding a Rust Postcard byte stream.
    """

    def __init__(self, instructions: Dict[str, str]) -> None:
        self._struct_fields: List[Tuple[str, str]] = []
        self._postcard_instructions: List[
            Tuple[str, Union[PostcardData, PostcardList, PostcardContainer]]
        ] = []
        self.update_rust_struct_fields(instructions)

    def update_rust_struct_fields(self, instructions: Dict[str, str]) -> None:
        """
        Add or update a dictionary of JSON formatted struct fields and create
        deserialization instructions.

        Clears the existing instructions.
        """
        self._struct_fields.clear()
        for variable_name, instruction in instructions.items():
            self._struct_fields.append((variable_name, instruction))
        self._struct_fields_to_deserialize_instructions()

    def _struct_fields_to_deserialize_instructions(self):
        """
        Converts the list of struct fields into a list of Postcard deserialization instructions.
        """
        self._postcard_instructions.clear()
        for variable_name, instruction in self._struct_fields:
            if Option.is_type(instruction):
                # Handle Option type
                self._postcard_instructions.append((variable_name, Option.from_schema(instruction)))
            elif Array.is_type(instruction):
                # TODO: Array stuff
                array_instructions = Array.from_schema(instruction)
                self._postcard_instructions.append((variable_name, array_instructions))
            elif UnsignedVarint.is_type(instruction):
                # Handle Unsigned Varint type
                self._postcard_instructions.append(
                    (variable_name, UnsignedVarint.from_schema(instruction))
                )
            elif SignedVarint.is_type(instruction):
                # Handle Signed Varint type
                self._postcard_instructions.append(
                    (variable_name, SignedVarint.from_schema(instruction))
                )
            elif Float.is_type(instruction):
                # Handle f32
                self._postcard_instructions.append((variable_name, Float.from_schema(instruction)))
            elif StaticString.is_type(instruction):
                # Handle String type
                self._postcard_instructions.append((variable_name, StaticString()))
            elif Vec.is_type(instruction):
                # Handle Byte Array type
                vec_instructions = Vec.from_schema(instruction)
                self._postcard_instructions.append((variable_name, vec_instructions))
            else:
                raise ValueError(f"Unsupported instruction: {instruction}")

    def convert(self, bytes: bytearray) -> Dict[str, Any]:
        """
        Convert the byte array into a dictionary of variable names and their deserialized values.
        """
        output = {}
        for variable_name, flavor in self._postcard_instructions:
            if bytes:
                value = flavor.deserialize(bytes)
                output[variable_name] = value

        return output
