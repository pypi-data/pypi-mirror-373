from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.case_document import CaseDocument
    from ..models.pageable import Pageable


T = TypeVar("T", bound="PageCaseDocument")


@_attrs_define
class PageCaseDocument:
    """
    Attributes:
        content (list['CaseDocument']):
        pageable (Pageable):
        page_number (int):
        offset (int):
        size (int):
        empty (bool):
        number_of_elements (int):
        total_size (int):
        total_pages (int):
    """

    content: list["CaseDocument"]
    pageable: "Pageable"
    page_number: int
    offset: int
    size: int
    empty: bool
    number_of_elements: int
    total_size: int
    total_pages: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = []
        for content_item_data in self.content:
            content_item = content_item_data.to_dict()
            content.append(content_item)

        pageable = self.pageable.to_dict()

        page_number = self.page_number

        offset = self.offset

        size = self.size

        empty = self.empty

        number_of_elements = self.number_of_elements

        total_size = self.total_size

        total_pages = self.total_pages

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
                "pageable": pageable,
                "pageNumber": page_number,
                "offset": offset,
                "size": size,
                "empty": empty,
                "numberOfElements": number_of_elements,
                "totalSize": total_size,
                "totalPages": total_pages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.case_document import CaseDocument
        from ..models.pageable import Pageable

        d = dict(src_dict)
        content = []
        _content = d.pop("content")
        for content_item_data in _content:
            content_item = CaseDocument.from_dict(content_item_data)

            content.append(content_item)

        pageable = Pageable.from_dict(d.pop("pageable"))

        page_number = d.pop("pageNumber")

        offset = d.pop("offset")

        size = d.pop("size")

        empty = d.pop("empty")

        number_of_elements = d.pop("numberOfElements")

        total_size = d.pop("totalSize")

        total_pages = d.pop("totalPages")

        page_case_document = cls(
            content=content,
            pageable=pageable,
            page_number=page_number,
            offset=offset,
            size=size,
            empty=empty,
            number_of_elements=number_of_elements,
            total_size=total_size,
            total_pages=total_pages,
        )

        page_case_document.additional_properties = d
        return page_case_document

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
