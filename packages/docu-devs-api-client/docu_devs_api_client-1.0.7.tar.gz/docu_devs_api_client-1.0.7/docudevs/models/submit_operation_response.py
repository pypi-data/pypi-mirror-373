from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SubmitOperationResponse")


@_attrs_define
class SubmitOperationResponse:
    """
    Attributes:
        job_guid (str):
        operation_type (str):
        status (str):
        message (str):
    """

    job_guid: str
    operation_type: str
    status: str
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_guid = self.job_guid

        operation_type = self.operation_type

        status = self.status

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jobGuid": job_guid,
                "operationType": operation_type,
                "status": status,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_guid = d.pop("jobGuid")

        operation_type = d.pop("operationType")

        status = d.pop("status")

        message = d.pop("message")

        submit_operation_response = cls(
            job_guid=job_guid,
            operation_type=operation_type,
            status=status,
            message=message,
        )

        submit_operation_response.additional_properties = d
        return submit_operation_response

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
