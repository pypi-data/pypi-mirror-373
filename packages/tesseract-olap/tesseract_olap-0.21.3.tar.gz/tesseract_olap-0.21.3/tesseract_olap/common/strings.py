from __future__ import annotations

from collections.abc import Mapping
from typing import Any, overload

import fnv_c
from typing_extensions import Literal

NAN_VALUES = frozenset(
    (
        "-1.#IND",
        "1.#QNAN",
        "1.#IND",
        "-1.#QNAN",
        "#N/A N/A",
        "#N/A",
        "N/A",
        "n/a",
        "#NA",
        "NULL",
        "null",
        "NaN",
        "-NaN",
        "nan",
        "-nan",
    ),
)

TRUTHY_STRINGS = frozenset(("1", "true", "t", "on", "y", "yes"))
FALSEY_STRINGS = frozenset(("0", "false", "f", "off", "n", "no", "none", "nope", ""))


@overload
def get_localization(
    dictionary: Mapping[str, str],
    locale: str,
) -> str | None: ...
@overload
def get_localization(
    dictionary: Mapping[str, str],
    locale: str,
    *,
    force: Literal[True],
) -> str: ...
def get_localization(
    dictionary: Mapping[str, str],
    locale: str,
    *,
    force: bool = False,
) -> str | None:
    """Return the value from a dictionary of terms, where the locale code is the key.

    If it doesn't find the specific locale, looks for the general locale code,
    and if it's not available either, returns the value for the default locale.
    """
    if locale not in dictionary:
        locale = locale[0:2]
    if locale not in dictionary:
        locale = "xx"
    return dictionary[locale] if force else dictionary.get(locale)


def shorthash(string: str) -> str:
    """Generate a short non-cryptographic hash for the provided string."""
    return fnv_c.fnv1_64(string.encode()).to_bytes(8, "little").hex()[:8]


def numerify(string: str | bytes) -> float | int:
    """Try to convert the provided string to a numeric value."""
    string = string if isinstance(string, str) else str(string)
    if string in NAN_VALUES:
        return float("nan")
    _f = float(string)
    return int(string) if string.isnumeric() and int(string) == _f else _f


def is_numeric(string: str | bytes) -> bool:
    """Guess if the provided string is a numeric value."""
    try:
        float(string)
    except ValueError:
        return string in NAN_VALUES
    else:
        return True


def stringify(obj: Any) -> str:
    """Return a string representation of any kind of object."""
    if isinstance(obj, (list, set, tuple)):
        return repr(sorted(obj))

    if isinstance(obj, Mapping):
        value = ", ".join(
            f"{key!r}: {value!r}" for key, value in sorted(obj.items(), key=lambda x: x[0])
        )
        return f"{{{value}}}"

    return repr(obj)
