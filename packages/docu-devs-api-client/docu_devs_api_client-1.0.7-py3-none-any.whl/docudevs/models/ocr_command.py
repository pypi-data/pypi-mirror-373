from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ocr_type import OcrType, check_ocr_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="OcrCommand")


@_attrs_define
class OcrCommand:
    """
    Attributes:
        ocr (OcrType):
        ocr_format (Union[None, Unset, str]):
        mime_type (Union[None, Unset, str]):
        describe_figures (Union[None, Unset, bool]):
    """

    ocr: OcrType
    ocr_format: Union[None, Unset, str] = UNSET
    mime_type: Union[None, Unset, str] = UNSET
    describe_figures: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ocr: str = self.ocr

        ocr_format: Union[None, Unset, str]
        if isinstance(self.ocr_format, Unset):
            ocr_format = UNSET
        else:
            ocr_format = self.ocr_format

        mime_type: Union[None, Unset, str]
        if isinstance(self.mime_type, Unset):
            mime_type = UNSET
        else:
            mime_type = self.mime_type

        describe_figures: Union[None, Unset, bool]
        if isinstance(self.describe_figures, Unset):
            describe_figures = UNSET
        else:
            describe_figures = self.describe_figures

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ocr": ocr,
            }
        )
        if ocr_format is not UNSET:
            field_dict["ocrFormat"] = ocr_format
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type
        if describe_figures is not UNSET:
            field_dict["describeFigures"] = describe_figures

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ocr = check_ocr_type(d.pop("ocr"))

        def _parse_ocr_format(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        ocr_format = _parse_ocr_format(d.pop("ocrFormat", UNSET))

        def _parse_mime_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mime_type = _parse_mime_type(d.pop("mimeType", UNSET))

        def _parse_describe_figures(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        describe_figures = _parse_describe_figures(d.pop("describeFigures", UNSET))

        ocr_command = cls(
            ocr=ocr,
            ocr_format=ocr_format,
            mime_type=mime_type,
            describe_figures=describe_figures,
        )

        ocr_command.additional_properties = d
        return ocr_command

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
