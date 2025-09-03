from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.operation_parameters import OperationParameters


T = TypeVar("T", bound="SubmitOperationRequest")


@_attrs_define
class SubmitOperationRequest:
    """
    Attributes:
        job_guid (str):
        type_ (str):
        parameters (Union[Unset, OperationParameters]):
    """

    job_guid: str
    type_: str
    parameters: Union[Unset, "OperationParameters"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_guid = self.job_guid

        type_ = self.type_

        parameters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jobGuid": job_guid,
                "type": type_,
            }
        )
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.operation_parameters import OperationParameters

        d = dict(src_dict)
        job_guid = d.pop("jobGuid")

        type_ = d.pop("type")

        _parameters = d.pop("parameters", UNSET)
        parameters: Union[Unset, OperationParameters]
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = OperationParameters.from_dict(_parameters)

        submit_operation_request = cls(
            job_guid=job_guid,
            type_=type_,
            parameters=parameters,
        )

        submit_operation_request.additional_properties = d
        return submit_operation_request

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
