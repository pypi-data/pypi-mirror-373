from typing import Literal, cast

ExtractionMode = Literal["OCR", "SIMPLE", "STEPS"]

EXTRACTION_MODE_VALUES: set[ExtractionMode] = {
    "OCR",
    "SIMPLE",
    "STEPS",
}


def check_extraction_mode(value: str) -> ExtractionMode:
    if value in EXTRACTION_MODE_VALUES:
        return cast(ExtractionMode, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {EXTRACTION_MODE_VALUES!r}")
