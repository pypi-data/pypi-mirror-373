import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProcessingJob")


@_attrs_define
class ProcessingJob:
    """
    Attributes:
        status (str):
        guid (str):
        job_type (str):
        organization_id (int):
        dependency_status (str):
        error (Union[None, Unset, str]):
        token_count (Union[None, Unset, int]):
        operation_type (Union[None, Unset, str]):
        depends_on_guid (Union[None, Unset, str]):
        created_at (Union[None, Unset, datetime.datetime]):
        updated_at (Union[None, Unset, datetime.datetime]):
    """

    status: str
    guid: str
    job_type: str
    organization_id: int
    dependency_status: str
    error: Union[None, Unset, str] = UNSET
    token_count: Union[None, Unset, int] = UNSET
    operation_type: Union[None, Unset, str] = UNSET
    depends_on_guid: Union[None, Unset, str] = UNSET
    created_at: Union[None, Unset, datetime.datetime] = UNSET
    updated_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        guid = self.guid

        job_type = self.job_type

        organization_id = self.organization_id

        dependency_status = self.dependency_status

        error: Union[None, Unset, str]
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        token_count: Union[None, Unset, int]
        if isinstance(self.token_count, Unset):
            token_count = UNSET
        else:
            token_count = self.token_count

        operation_type: Union[None, Unset, str]
        if isinstance(self.operation_type, Unset):
            operation_type = UNSET
        else:
            operation_type = self.operation_type

        depends_on_guid: Union[None, Unset, str]
        if isinstance(self.depends_on_guid, Unset):
            depends_on_guid = UNSET
        else:
            depends_on_guid = self.depends_on_guid

        created_at: Union[None, Unset, str]
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        updated_at: Union[None, Unset, str]
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "guid": guid,
                "jobType": job_type,
                "organizationId": organization_id,
                "dependencyStatus": dependency_status,
            }
        )
        if error is not UNSET:
            field_dict["error"] = error
        if token_count is not UNSET:
            field_dict["tokenCount"] = token_count
        if operation_type is not UNSET:
            field_dict["operationType"] = operation_type
        if depends_on_guid is not UNSET:
            field_dict["dependsOnGuid"] = depends_on_guid
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        guid = d.pop("guid")

        job_type = d.pop("jobType")

        organization_id = d.pop("organizationId")

        dependency_status = d.pop("dependencyStatus")

        def _parse_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_token_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        token_count = _parse_token_count(d.pop("tokenCount", UNSET))

        def _parse_operation_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        operation_type = _parse_operation_type(d.pop("operationType", UNSET))

        def _parse_depends_on_guid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        depends_on_guid = _parse_depends_on_guid(d.pop("dependsOnGuid", UNSET))

        def _parse_created_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = isoparse(data)

                return created_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        created_at = _parse_created_at(d.pop("createdAt", UNSET))

        def _parse_updated_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        updated_at = _parse_updated_at(d.pop("updatedAt", UNSET))

        processing_job = cls(
            status=status,
            guid=guid,
            job_type=job_type,
            organization_id=organization_id,
            dependency_status=dependency_status,
            error=error,
            token_count=token_count,
            operation_type=operation_type,
            depends_on_guid=depends_on_guid,
            created_at=created_at,
            updated_at=updated_at,
        )

        processing_job.additional_properties = d
        return processing_job

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
