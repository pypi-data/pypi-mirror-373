from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pageable_mode import PageableMode, check_pageable_mode

if TYPE_CHECKING:
    from ..models.sort import Sort
    from ..models.sort_order import SortOrder


T = TypeVar("T", bound="Pageable")


@_attrs_define
class Pageable:
    """
    Attributes:
        order_by (list['SortOrder']):
        number (int):
        size (int):
        mode (PageableMode):
        sort (Sort):
    """

    order_by: list["SortOrder"]
    number: int
    size: int
    mode: PageableMode
    sort: "Sort"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order_by = []
        for order_by_item_data in self.order_by:
            order_by_item = order_by_item_data.to_dict()
            order_by.append(order_by_item)

        number = self.number

        size = self.size

        mode: str = self.mode

        sort = self.sort.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "orderBy": order_by,
                "number": number,
                "size": size,
                "mode": mode,
                "sort": sort,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sort import Sort
        from ..models.sort_order import SortOrder

        d = dict(src_dict)
        order_by = []
        _order_by = d.pop("orderBy")
        for order_by_item_data in _order_by:
            order_by_item = SortOrder.from_dict(order_by_item_data)

            order_by.append(order_by_item)

        number = d.pop("number")

        size = d.pop("size")

        mode = check_pageable_mode(d.pop("mode"))

        sort = Sort.from_dict(d.pop("sort"))

        pageable = cls(
            order_by=order_by,
            number=number,
            size=size,
            mode=mode,
            sort=sort,
        )

        pageable.additional_properties = d
        return pageable

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
