from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PDFField")


@_attrs_define
class PDFField:
    """
    Attributes:
        name (str):
        type_ (str):
        flags (list[str]):
        value (str):
        options (list[str]):
        tooltip (Union[None, Unset, str]):
        default_value (Union[None, Unset, str]):
        script (Union[None, Unset, str]):
    """

    name: str
    type_: str
    flags: list[str]
    value: str
    options: list[str]
    tooltip: Union[None, Unset, str] = UNSET
    default_value: Union[None, Unset, str] = UNSET
    script: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        flags = self.flags

        value = self.value

        options = self.options

        tooltip: Union[None, Unset, str]
        if isinstance(self.tooltip, Unset):
            tooltip = UNSET
        else:
            tooltip = self.tooltip

        default_value: Union[None, Unset, str]
        if isinstance(self.default_value, Unset):
            default_value = UNSET
        else:
            default_value = self.default_value

        script: Union[None, Unset, str]
        if isinstance(self.script, Unset):
            script = UNSET
        else:
            script = self.script

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "flags": flags,
                "value": value,
                "options": options,
            }
        )
        if tooltip is not UNSET:
            field_dict["tooltip"] = tooltip
        if default_value is not UNSET:
            field_dict["defaultValue"] = default_value
        if script is not UNSET:
            field_dict["script"] = script

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_ = d.pop("type")

        flags = cast(list[str], d.pop("flags"))

        value = d.pop("value")

        options = cast(list[str], d.pop("options"))

        def _parse_tooltip(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tooltip = _parse_tooltip(d.pop("tooltip", UNSET))

        def _parse_default_value(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        default_value = _parse_default_value(d.pop("defaultValue", UNSET))

        def _parse_script(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        script = _parse_script(d.pop("script", UNSET))

        pdf_field = cls(
            name=name,
            type_=type_,
            flags=flags,
            value=value,
            options=options,
            tooltip=tooltip,
            default_value=default_value,
            script=script,
        )

        pdf_field.additional_properties = d
        return pdf_field

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
