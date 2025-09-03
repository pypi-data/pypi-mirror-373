from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.sort_order import SortOrder


T = TypeVar("T", bound="Sort")


@_attrs_define
class Sort:
    """
    Attributes:
        order_by (list['SortOrder']):
    """

    order_by: list["SortOrder"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order_by = []
        for order_by_item_data in self.order_by:
            order_by_item = order_by_item_data.to_dict()
            order_by.append(order_by_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "orderBy": order_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sort_order import SortOrder

        d = dict(src_dict)
        order_by = []
        _order_by = d.pop("orderBy")
        for order_by_item_data in _order_by:
            order_by_item = SortOrder.from_dict(order_by_item_data)

            order_by.append(order_by_item)

        sort = cls(
            order_by=order_by,
        )

        sort.additional_properties = d
        return sort

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
