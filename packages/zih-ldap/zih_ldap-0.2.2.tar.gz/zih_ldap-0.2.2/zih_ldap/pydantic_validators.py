"""validators for pydantic"""

from datetime import date, datetime
from typing import Any

from ldap3.utils.dn import parse_dn


def active_to_bool(value: Any) -> bool:
    """make string state to bool"""
    match value:
        case "active":
            return True
        case "inactive":
            return False
        case _:
            raise ValueError(f"unknown state '{value}'")


def group_dn_to_name(distinguished_names: list[str]) -> list[str]:
    """convert group-dn to just it's name (cn) part"""
    return [
        value
        for group_dn in distinguished_names
        for component, value, _ in parse_dn(group_dn)
        if component == "cn"
    ]


def string_to_date(value: str | None) -> date | None:
    """parse a "20120101" string to a date"""
    if not value:
        return None
    return datetime.strptime(value, "%Y%m%d").date()


def to_str(value: Any) -> str | None:
    """convert to str needed for mypy"""
    if value is None:
        return value
    return str(value)
