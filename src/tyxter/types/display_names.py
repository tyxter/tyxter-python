from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import TypedDict

# Advisory codes are stable; messages are informational, not Meta review results.
DisplayNameWarningCode: TypeAlias = Literal[
    "display_name_promotional_word",
    "display_name_symbols",
    "display_name_phone_digits",
    "display_name_all_caps",
    "display_name_personal_name_suffix",
    "display_name_mismatch_business",
    "display_name_format",
]


class DisplayNameWarning(TypedDict):
    """An advisory display-name suggestion.

    It does not block submission or predict Meta approval.
    """

    code: DisplayNameWarningCode
    field: Literal["display_name"]
    message: str
