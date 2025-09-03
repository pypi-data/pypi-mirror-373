from typing import Literal, cast

DocumentStatus = Literal["COMPLETED", "FAILED", "PENDING", "PROCESSING"]

DOCUMENT_STATUS_VALUES: set[DocumentStatus] = {
    "COMPLETED",
    "FAILED",
    "PENDING",
    "PROCESSING",
}


def check_document_status(value: str) -> DocumentStatus:
    if value in DOCUMENT_STATUS_VALUES:
        return cast(DocumentStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DOCUMENT_STATUS_VALUES!r}")
