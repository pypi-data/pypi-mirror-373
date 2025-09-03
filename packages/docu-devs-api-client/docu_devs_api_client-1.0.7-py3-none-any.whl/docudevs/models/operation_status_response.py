from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.operation_info import OperationInfo


T = TypeVar("T", bound="OperationStatusResponse")


@_attrs_define
class OperationStatusResponse:
    """
    Attributes:
        parent_job_guid (str):
        operations (list['OperationInfo']):
        total_operations (int):
    """

    parent_job_guid: str
    operations: list["OperationInfo"]
    total_operations: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        parent_job_guid = self.parent_job_guid

        operations = []
        for operations_item_data in self.operations:
            operations_item = operations_item_data.to_dict()
            operations.append(operations_item)

        total_operations = self.total_operations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "parentJobGuid": parent_job_guid,
                "operations": operations,
                "totalOperations": total_operations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.operation_info import OperationInfo

        d = dict(src_dict)
        parent_job_guid = d.pop("parentJobGuid")

        operations = []
        _operations = d.pop("operations")
        for operations_item_data in _operations:
            operations_item = OperationInfo.from_dict(operations_item_data)

            operations.append(operations_item)

        total_operations = d.pop("totalOperations")

        operation_status_response = cls(
            parent_job_guid=parent_job_guid,
            operations=operations,
            total_operations=total_operations,
        )

        operation_status_response.additional_properties = d
        return operation_status_response

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
