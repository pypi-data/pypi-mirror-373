from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OperationResultResponse")


@_attrs_define
class OperationResultResponse:
    """
    Attributes:
        job_guid (str):
        parent_job_guid (str):
        operation_type (str):
        status (str):
        created_at (str):
        updated_at (str):
        result_available (bool):
        error (Union[None, Unset, str]):
        result (Union[None, Unset, str]):
    """

    job_guid: str
    parent_job_guid: str
    operation_type: str
    status: str
    created_at: str
    updated_at: str
    result_available: bool
    error: Union[None, Unset, str] = UNSET
    result: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_guid = self.job_guid

        parent_job_guid = self.parent_job_guid

        operation_type = self.operation_type

        status = self.status

        created_at = self.created_at

        updated_at = self.updated_at

        result_available = self.result_available

        error: Union[None, Unset, str]
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        result: Union[None, Unset, str]
        if isinstance(self.result, Unset):
            result = UNSET
        else:
            result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jobGuid": job_guid,
                "parentJobGuid": parent_job_guid,
                "operationType": operation_type,
                "status": status,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "resultAvailable": result_available,
            }
        )
        if error is not UNSET:
            field_dict["error"] = error
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_guid = d.pop("jobGuid")

        parent_job_guid = d.pop("parentJobGuid")

        operation_type = d.pop("operationType")

        status = d.pop("status")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        result_available = d.pop("resultAvailable")

        def _parse_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_result(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        result = _parse_result(d.pop("result", UNSET))

        operation_result_response = cls(
            job_guid=job_guid,
            parent_job_guid=parent_job_guid,
            operation_type=operation_type,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            result_available=result_available,
            error=error,
            result=result,
        )

        operation_result_response.additional_properties = d
        return operation_result_response

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
