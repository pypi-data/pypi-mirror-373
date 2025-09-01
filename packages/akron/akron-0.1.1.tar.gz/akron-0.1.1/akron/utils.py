"""Utility helpers for Akron."""

from typing import Any

_TYPE_MAP = {
    "int": "INTEGER",
    int: "INTEGER",
    "str": "TEXT",
    str: "TEXT",
    "float": "REAL",
    float: "REAL",
    "bool": "INTEGER",  # store bools as 0/1
    bool: "INTEGER",
}


def map_type(dtype: Any) -> str:
    """Map simple python type (or string) to SQLite SQL type."""
    if dtype in _TYPE_MAP:
        return _TYPE_MAP[dtype]
    # allow users to pass python types like typing.Optional[int]
    name = str(dtype).lower()
    if "int" in name:
        return "INTEGER"
    if "char" in name or "text" in name or "str" in name:
        return "TEXT"
    if "float" in name or "real" in name:
        return "REAL"
    return "TEXT"


def sanitize_identifier(name: str) -> str:
    """Very small sanitizer for identifiers (table/column names).

    Accepts simple alphanum + underscore names. Raises ValueError otherwise.

    (MVP: keep simple. In future, quote with driver-specific quoting.)
    """
    if not isinstance(name, str):
        raise ValueError("identifier must be a string")
    name = name.strip()
    if name == "":
        raise ValueError("identifier cannot be empty")
    # allow letters, numbers, underscore only
    for ch in name:
        if not (ch.isalnum() or ch == "_"):
            raise ValueError(f"invalid character in identifier: {ch}")
    return name
