from typing import Literal, cast

LlmType = Literal["DEFAULT", "HIGH", "MINI"]

LLM_TYPE_VALUES: set[LlmType] = {
    "DEFAULT",
    "HIGH",
    "MINI",
}


def check_llm_type(value: str) -> LlmType:
    if value in LLM_TYPE_VALUES:
        return cast(LlmType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LLM_TYPE_VALUES!r}")
