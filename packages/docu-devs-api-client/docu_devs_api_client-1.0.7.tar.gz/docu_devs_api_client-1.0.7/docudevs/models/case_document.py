import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.document_status import DocumentStatus, check_document_status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.case_document_metadata_type_1 import CaseDocumentMetadataType1


T = TypeVar("T", bound="CaseDocument")


@_attrs_define
class CaseDocument:
    """
    Attributes:
        case_id (int):
        organization_id (int):
        document_id (str):
        filename (str):
        blob_path (str):
        processing_status (DocumentStatus):
        id (Union[None, Unset, int]):
        user_id (Union[None, Unset, int]):
        content_type (Union[None, Unset, str]):
        size_bytes (Union[None, Unset, int]):
        metadata (Union['CaseDocumentMetadataType1', None, Unset]):
        processing_job_id (Union[None, Unset, int]):
        created_at (Union[None, Unset, datetime.datetime]):
        updated_at (Union[None, Unset, datetime.datetime]):
    """

    case_id: int
    organization_id: int
    document_id: str
    filename: str
    blob_path: str
    processing_status: DocumentStatus
    id: Union[None, Unset, int] = UNSET
    user_id: Union[None, Unset, int] = UNSET
    content_type: Union[None, Unset, str] = UNSET
    size_bytes: Union[None, Unset, int] = UNSET
    metadata: Union["CaseDocumentMetadataType1", None, Unset] = UNSET
    processing_job_id: Union[None, Unset, int] = UNSET
    created_at: Union[None, Unset, datetime.datetime] = UNSET
    updated_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.case_document_metadata_type_1 import CaseDocumentMetadataType1

        case_id = self.case_id

        organization_id = self.organization_id

        document_id = self.document_id

        filename = self.filename

        blob_path = self.blob_path

        processing_status: str = self.processing_status

        id: Union[None, Unset, int]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        user_id: Union[None, Unset, int]
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        content_type: Union[None, Unset, str]
        if isinstance(self.content_type, Unset):
            content_type = UNSET
        else:
            content_type = self.content_type

        size_bytes: Union[None, Unset, int]
        if isinstance(self.size_bytes, Unset):
            size_bytes = UNSET
        else:
            size_bytes = self.size_bytes

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, CaseDocumentMetadataType1):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        processing_job_id: Union[None, Unset, int]
        if isinstance(self.processing_job_id, Unset):
            processing_job_id = UNSET
        else:
            processing_job_id = self.processing_job_id

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
                "caseId": case_id,
                "organizationId": organization_id,
                "documentId": document_id,
                "filename": filename,
                "blobPath": blob_path,
                "processingStatus": processing_status,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if content_type is not UNSET:
            field_dict["contentType"] = content_type
        if size_bytes is not UNSET:
            field_dict["sizeBytes"] = size_bytes
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if processing_job_id is not UNSET:
            field_dict["processingJobId"] = processing_job_id
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.case_document_metadata_type_1 import CaseDocumentMetadataType1

        d = dict(src_dict)
        case_id = d.pop("caseId")

        organization_id = d.pop("organizationId")

        document_id = d.pop("documentId")

        filename = d.pop("filename")

        blob_path = d.pop("blobPath")

        processing_status = check_document_status(d.pop("processingStatus"))

        def _parse_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_user_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        user_id = _parse_user_id(d.pop("userId", UNSET))

        def _parse_content_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        content_type = _parse_content_type(d.pop("contentType", UNSET))

        def _parse_size_bytes(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        size_bytes = _parse_size_bytes(d.pop("sizeBytes", UNSET))

        def _parse_metadata(data: object) -> Union["CaseDocumentMetadataType1", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_1 = CaseDocumentMetadataType1.from_dict(data)

                return metadata_type_1
            except:  # noqa: E722
                pass
            return cast(Union["CaseDocumentMetadataType1", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_processing_job_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        processing_job_id = _parse_processing_job_id(d.pop("processingJobId", UNSET))

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

        case_document = cls(
            case_id=case_id,
            organization_id=organization_id,
            document_id=document_id,
            filename=filename,
            blob_path=blob_path,
            processing_status=processing_status,
            id=id,
            user_id=user_id,
            content_type=content_type,
            size_bytes=size_bytes,
            metadata=metadata,
            processing_job_id=processing_job_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        case_document.additional_properties = d
        return case_document

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
