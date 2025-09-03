from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="GenerateSchemaBody")


@_attrs_define
class GenerateSchemaBody:
    """
    Attributes:
        document (File):
        instructions (Union[File, None, Unset]):
    """

    document: File
    instructions: Union[File, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document = self.document.to_tuple()

        instructions: Union[FileTypes, None, Unset]
        if isinstance(self.instructions, Unset):
            instructions = UNSET
        elif isinstance(self.instructions, File):
            instructions = self.instructions.to_tuple()

        else:
            instructions = self.instructions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document": document,
            }
        )
        if instructions is not UNSET:
            field_dict["instructions"] = instructions

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("document", self.document.to_tuple()))

        if not isinstance(self.instructions, Unset):
            if isinstance(self.instructions, File):
                files.append(("instructions", self.instructions.to_tuple()))
            else:
                files.append(("instructions", (None, str(self.instructions).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document = File(payload=BytesIO(d.pop("document")))

        def _parse_instructions(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                instructions_type_0 = File(payload=BytesIO(data))

                return instructions_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

        instructions = _parse_instructions(d.pop("instructions", UNSET))

        generate_schema_body = cls(
            document=document,
            instructions=instructions,
        )

        generate_schema_body.additional_properties = d
        return generate_schema_body

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
