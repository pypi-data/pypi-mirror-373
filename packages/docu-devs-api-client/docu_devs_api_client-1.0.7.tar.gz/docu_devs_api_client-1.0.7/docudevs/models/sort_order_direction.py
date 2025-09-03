from typing import Literal, cast

SortOrderDirection = Literal["ASC", "DESC"]

SORT_ORDER_DIRECTION_VALUES: set[SortOrderDirection] = {
    "ASC",
    "DESC",
}


def check_sort_order_direction(value: str) -> SortOrderDirection:
    if value in SORT_ORDER_DIRECTION_VALUES:
        return cast(SortOrderDirection, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SORT_ORDER_DIRECTION_VALUES!r}")
