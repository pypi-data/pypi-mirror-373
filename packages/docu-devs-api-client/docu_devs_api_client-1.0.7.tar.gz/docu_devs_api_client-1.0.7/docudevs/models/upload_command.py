from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.extraction_mode import ExtractionMode, check_extraction_mode
from ..models.llm_type import LlmType, check_llm_type
from ..models.ocr_type import OcrType, check_ocr_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadCommand")


@_attrs_define
class UploadCommand:
    """
    Attributes:
        ocr (Union[Unset, OcrType]):
        llm (Union[Unset, LlmType]):
        extraction_mode (Union[Unset, ExtractionMode]):
        schema (Union[None, Unset, str]):
        prompt (Union[None, Unset, str]):
        barcodes (Union[None, Unset, bool]):
        mime_type (Union[None, Unset, str]):
        describe_figures (Union[None, Unset, bool]):
    """

    ocr: Union[Unset, OcrType] = UNSET
    llm: Union[Unset, LlmType] = UNSET
    extraction_mode: Union[Unset, ExtractionMode] = UNSET
    schema: Union[None, Unset, str] = UNSET
    prompt: Union[None, Unset, str] = UNSET
    barcodes: Union[None, Unset, bool] = UNSET
    mime_type: Union[None, Unset, str] = UNSET
    describe_figures: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ocr: Union[Unset, str] = UNSET
        if not isinstance(self.ocr, Unset):
            ocr = self.ocr

        llm: Union[Unset, str] = UNSET
        if not isinstance(self.llm, Unset):
            llm = self.llm

        extraction_mode: Union[Unset, str] = UNSET
        if not isinstance(self.extraction_mode, Unset):
            extraction_mode = self.extraction_mode

        schema: Union[None, Unset, str]
        if isinstance(self.schema, Unset):
            schema = UNSET
        else:
            schema = self.schema

        prompt: Union[None, Unset, str]
        if isinstance(self.prompt, Unset):
            prompt = UNSET
        else:
            prompt = self.prompt

        barcodes: Union[None, Unset, bool]
        if isinstance(self.barcodes, Unset):
            barcodes = UNSET
        else:
            barcodes = self.barcodes

        mime_type: Union[None, Unset, str]
        if isinstance(self.mime_type, Unset):
            mime_type = UNSET
        else:
            mime_type = self.mime_type

        describe_figures: Union[None, Unset, bool]
        if isinstance(self.describe_figures, Unset):
            describe_figures = UNSET
        else:
            describe_figures = self.describe_figures

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ocr is not UNSET:
            field_dict["ocr"] = ocr
        if llm is not UNSET:
            field_dict["llm"] = llm
        if extraction_mode is not UNSET:
            field_dict["extractionMode"] = extraction_mode
        if schema is not UNSET:
            field_dict["schema"] = schema
        if prompt is not UNSET:
            field_dict["prompt"] = prompt
        if barcodes is not UNSET:
            field_dict["barcodes"] = barcodes
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type
        if describe_figures is not UNSET:
            field_dict["describeFigures"] = describe_figures

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _ocr = d.pop("ocr", UNSET)
        ocr: Union[Unset, OcrType]
        if isinstance(_ocr, Unset):
            ocr = UNSET
        else:
            ocr = check_ocr_type(_ocr)

        _llm = d.pop("llm", UNSET)
        llm: Union[Unset, LlmType]
        if isinstance(_llm, Unset):
            llm = UNSET
        else:
            llm = check_llm_type(_llm)

        _extraction_mode = d.pop("extractionMode", UNSET)
        extraction_mode: Union[Unset, ExtractionMode]
        if isinstance(_extraction_mode, Unset):
            extraction_mode = UNSET
        else:
            extraction_mode = check_extraction_mode(_extraction_mode)

        def _parse_schema(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        schema = _parse_schema(d.pop("schema", UNSET))

        def _parse_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        prompt = _parse_prompt(d.pop("prompt", UNSET))

        def _parse_barcodes(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        barcodes = _parse_barcodes(d.pop("barcodes", UNSET))

        def _parse_mime_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mime_type = _parse_mime_type(d.pop("mimeType", UNSET))

        def _parse_describe_figures(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        describe_figures = _parse_describe_figures(d.pop("describeFigures", UNSET))

        upload_command = cls(
            ocr=ocr,
            llm=llm,
            extraction_mode=extraction_mode,
            schema=schema,
            prompt=prompt,
            barcodes=barcodes,
            mime_type=mime_type,
            describe_figures=describe_figures,
        )

        upload_command.additional_properties = d
        return upload_command

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
