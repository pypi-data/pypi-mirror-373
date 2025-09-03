from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.llm_type import LlmType, check_llm_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.operation_parameters_custom_parameters_type_1 import OperationParametersCustomParametersType1


T = TypeVar("T", bound="OperationParameters")


@_attrs_define
class OperationParameters:
    """
    Attributes:
        llm_type (Union[Unset, LlmType]):
        custom_parameters (Union['OperationParametersCustomParametersType1', None, Unset]):
    """

    llm_type: Union[Unset, LlmType] = UNSET
    custom_parameters: Union["OperationParametersCustomParametersType1", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.operation_parameters_custom_parameters_type_1 import OperationParametersCustomParametersType1

        llm_type: Union[Unset, str] = UNSET
        if not isinstance(self.llm_type, Unset):
            llm_type = self.llm_type

        custom_parameters: Union[None, Unset, dict[str, Any]]
        if isinstance(self.custom_parameters, Unset):
            custom_parameters = UNSET
        elif isinstance(self.custom_parameters, OperationParametersCustomParametersType1):
            custom_parameters = self.custom_parameters.to_dict()
        else:
            custom_parameters = self.custom_parameters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if llm_type is not UNSET:
            field_dict["llmType"] = llm_type
        if custom_parameters is not UNSET:
            field_dict["customParameters"] = custom_parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.operation_parameters_custom_parameters_type_1 import OperationParametersCustomParametersType1

        d = dict(src_dict)
        _llm_type = d.pop("llmType", UNSET)
        llm_type: Union[Unset, LlmType]
        if isinstance(_llm_type, Unset):
            llm_type = UNSET
        else:
            llm_type = check_llm_type(_llm_type)

        def _parse_custom_parameters(data: object) -> Union["OperationParametersCustomParametersType1", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_parameters_type_1 = OperationParametersCustomParametersType1.from_dict(data)

                return custom_parameters_type_1
            except:  # noqa: E722
                pass
            return cast(Union["OperationParametersCustomParametersType1", None, Unset], data)

        custom_parameters = _parse_custom_parameters(d.pop("customParameters", UNSET))

        operation_parameters = cls(
            llm_type=llm_type,
            custom_parameters=custom_parameters,
        )

        operation_parameters.additional_properties = d
        return operation_parameters

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
