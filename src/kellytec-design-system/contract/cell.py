"""Canonical cell payload contract."""

from __future__ import annotations

from typing import Any


def cell(variant: str, **payload: Any) -> dict[str, Any]:
    if not isinstance(variant, str) or not variant.strip():
        raise ValueError("cell variant must be a non-empty str")
    result = dict(payload)
    result.setdefault("variant", variant)
    return result


__all__ = ["cell"]
