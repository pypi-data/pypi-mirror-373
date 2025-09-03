from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sort_order_direction import SortOrderDirection, check_sort_order_direction

T = TypeVar("T", bound="SortOrder")


@_attrs_define
class SortOrder:
    """
    Attributes:
        ignore_case (bool):
        direction (SortOrderDirection):
        property_ (str):
        ascending (bool):
    """

    ignore_case: bool
    direction: SortOrderDirection
    property_: str
    ascending: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ignore_case = self.ignore_case

        direction: str = self.direction

        property_ = self.property_

        ascending = self.ascending

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ignoreCase": ignore_case,
                "direction": direction,
                "property": property_,
                "ascending": ascending,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ignore_case = d.pop("ignoreCase")

        direction = check_sort_order_direction(d.pop("direction"))

        property_ = d.pop("property")

        ascending = d.pop("ascending")

        sort_order = cls(
            ignore_case=ignore_case,
            direction=direction,
            property_=property_,
            ascending=ascending,
        )

        sort_order.additional_properties = d
        return sort_order

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
