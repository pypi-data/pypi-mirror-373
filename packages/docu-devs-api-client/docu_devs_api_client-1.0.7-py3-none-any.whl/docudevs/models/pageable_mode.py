from typing import Literal, cast

PageableMode = Literal["CURSOR_NEXT", "CURSOR_PREVIOUS", "OFFSET"]

PAGEABLE_MODE_VALUES: set[PageableMode] = {
    "CURSOR_NEXT",
    "CURSOR_PREVIOUS",
    "OFFSET",
}


def check_pageable_mode(value: str) -> PageableMode:
    if value in PAGEABLE_MODE_VALUES:
        return cast(PageableMode, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAGEABLE_MODE_VALUES!r}")
