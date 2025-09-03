from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="UploadFilesBody")


@_attrs_define
class UploadFilesBody:
    """
    Attributes:
        document (File):
        metadata (Union[File, None, Unset]):
        instructions (Union[File, None, Unset]):
        schema (Union[File, None, Unset]):
    """

    document: File
    metadata: Union[File, None, Unset] = UNSET
    instructions: Union[File, None, Unset] = UNSET
    schema: Union[File, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document = self.document.to_tuple()

        metadata: Union[FileTypes, None, Unset]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, File):
            metadata = self.metadata.to_tuple()

        else:
            metadata = self.metadata

        instructions: Union[FileTypes, None, Unset]
        if isinstance(self.instructions, Unset):
            instructions = UNSET
        elif isinstance(self.instructions, File):
            instructions = self.instructions.to_tuple()

        else:
            instructions = self.instructions

        schema: Union[FileTypes, None, Unset]
        if isinstance(self.schema, Unset):
            schema = UNSET
        elif isinstance(self.schema, File):
            schema = self.schema.to_tuple()

        else:
            schema = self.schema

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document": document,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if schema is not UNSET:
            field_dict["schema"] = schema

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("document", self.document.to_tuple()))

        if not isinstance(self.metadata, Unset):
            if isinstance(self.metadata, File):
                files.append(("metadata", self.metadata.to_tuple()))
            else:
                files.append(("metadata", (None, str(self.metadata).encode(), "text/plain")))

        if not isinstance(self.instructions, Unset):
            if isinstance(self.instructions, File):
                files.append(("instructions", self.instructions.to_tuple()))
            else:
                files.append(("instructions", (None, str(self.instructions).encode(), "text/plain")))

        if not isinstance(self.schema, Unset):
            if isinstance(self.schema, File):
                files.append(("schema", self.schema.to_tuple()))
            else:
                files.append(("schema", (None, str(self.schema).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document = File(payload=BytesIO(d.pop("document")))

        def _parse_metadata(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                metadata_type_0 = File(payload=BytesIO(data))

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

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

        def _parse_schema(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                schema_type_0 = File(payload=BytesIO(data))

                return schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

        schema = _parse_schema(d.pop("schema", UNSET))

        upload_files_body = cls(
            document=document,
            metadata=metadata,
            instructions=instructions,
            schema=schema,
        )

        upload_files_body.additional_properties = d
        return upload_files_body

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
