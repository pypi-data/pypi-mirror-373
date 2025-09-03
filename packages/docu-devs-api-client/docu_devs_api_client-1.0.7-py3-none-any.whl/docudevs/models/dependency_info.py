from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.processing_job import ProcessingJob


T = TypeVar("T", bound="DependencyInfo")


@_attrs_define
class DependencyInfo:
    """
    Attributes:
        guid (str):
        dependency_status (str):
        depends_on_guid (Union[None, Unset, str]):
        parent_job (Union[Unset, ProcessingJob]):
    """

    guid: str
    dependency_status: str
    depends_on_guid: Union[None, Unset, str] = UNSET
    parent_job: Union[Unset, "ProcessingJob"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        dependency_status = self.dependency_status

        depends_on_guid: Union[None, Unset, str]
        if isinstance(self.depends_on_guid, Unset):
            depends_on_guid = UNSET
        else:
            depends_on_guid = self.depends_on_guid

        parent_job: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parent_job, Unset):
            parent_job = self.parent_job.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "guid": guid,
                "dependencyStatus": dependency_status,
            }
        )
        if depends_on_guid is not UNSET:
            field_dict["dependsOnGuid"] = depends_on_guid
        if parent_job is not UNSET:
            field_dict["parentJob"] = parent_job

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.processing_job import ProcessingJob

        d = dict(src_dict)
        guid = d.pop("guid")

        dependency_status = d.pop("dependencyStatus")

        def _parse_depends_on_guid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        depends_on_guid = _parse_depends_on_guid(d.pop("dependsOnGuid", UNSET))

        _parent_job = d.pop("parentJob", UNSET)
        parent_job: Union[Unset, ProcessingJob]
        if isinstance(_parent_job, Unset):
            parent_job = UNSET
        else:
            parent_job = ProcessingJob.from_dict(_parent_job)

        dependency_info = cls(
            guid=guid,
            dependency_status=dependency_status,
            depends_on_guid=depends_on_guid,
            parent_job=parent_job,
        )

        dependency_info.additional_properties = d
        return dependency_info

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
