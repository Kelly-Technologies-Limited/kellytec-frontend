"""Typed descriptors for every user-visible monitor value."""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


DisplayKind = Literal[
    "text", "integer", "decimal", "quantity", "price", "money",
    "percent_ratio", "percent_points", "bytes", "gigabytes", "duration_ms",
    "duration_seconds", "ratio",
    "trading_date", "datetime_et", "time_et", "minute_et", "status",
]
DISPLAY_KINDS = frozenset(DisplayKind.__args__)
STATUS_VALUES = frozenset({"healthy", "warning", "critical", "unknown", "inactive"})


class DisplayValue(TypedDict):
    kind: DisplayKind
    value: object
    currency: NotRequired[str]
    label: NotRequired[str]
    show_plus: NotRequired[bool]
    show_timezone: NotRequired[bool]
    fraction_digits: NotRequired[int]
    fractional_seconds: NotRequired[Literal[3]]
    compact: NotRequired[Literal["millions"]]


def display_value(
    kind: DisplayKind,
    value: object,
    *,
    currency: str | None = None,
    label: str | None = None,
    show_plus: bool = False,
    show_timezone: bool = False,
    fraction_digits: int | None = None,
    fractional_seconds: Literal[3] | None = None,
    compact: Literal["millions"] | None = None,
) -> DisplayValue:
    """Build a strict semantic value without guessing business meaning."""

    if kind not in DISPLAY_KINDS:
        raise ValueError(f"unsupported display kind: {kind}")
    if kind == "money" and (not isinstance(currency, str) or not currency.strip()):
        raise ValueError("money display values require currency")
    if kind != "money" and currency is not None:
        raise ValueError("currency is only valid for money display values")
    if kind == "status" and value not in STATUS_VALUES:
        raise ValueError("status display values require a canonical status")
    if kind != "status" and label is not None:
        raise ValueError("label is only valid for status display values")
    if kind != "quantity" and show_plus:
        raise ValueError("show_plus is only valid for quantity display values")
    if fraction_digits is not None and (
        kind not in {"percent_points", "percent_ratio", "decimal", "quantity", "price", "money", "duration_seconds", "ratio"}
        or type(fraction_digits) is not int
        or not 0 <= fraction_digits <= 20
    ):
        raise ValueError("fraction_digits requires a supported numeric kind and an integer from 0 to 20")
    if fractional_seconds is not None and (kind not in {"datetime_et", "time_et"} or fractional_seconds != 3):
        raise ValueError("fractional_seconds requires a time display and millisecond precision")
    if show_timezone and kind not in {"datetime_et", "time_et", "minute_et"}:
        raise ValueError("show_timezone is only valid for NY time display values")
    if kind != "money" and compact is not None:
        raise ValueError("compact is only valid for money display values")

    result: DisplayValue = {"kind": kind, "value": value}
    if currency is not None:
        result["currency"] = currency.strip().upper()
    if label is not None:
        result["label"] = label
    if show_plus:
        result["show_plus"] = True
    if show_timezone:
        result["show_timezone"] = True
    if fraction_digits is not None:
        result["fraction_digits"] = fraction_digits
    if fractional_seconds is not None:
        result["fractional_seconds"] = fractional_seconds
    if compact is not None:
        result["compact"] = compact
    return result


__all__ = ["DISPLAY_KINDS", "DisplayKind", "DisplayValue", "display_value"]
