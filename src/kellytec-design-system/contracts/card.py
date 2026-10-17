"""Canonical card payload contract."""

from __future__ import annotations

from typing import Any


def card(card_id: str, title: str, kind: str, **payload: Any) -> dict[str, Any]:
    for name, value in (("card_id", card_id), ("title", title), ("kind", kind)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty str")
    result: dict[str, Any] = {
        "id": card_id,
        "title": title,
        "kind": kind,
        "renderer": payload.pop("renderer", kind),
    }
    result.update(payload)
    return result


def placeholder_card(card_id: str, title: str, *, description: str) -> dict[str, Any]:
    return card(card_id, title, "placeholder", renderer="placeholder", description=description, placeholder=True)


def cards_by_id(*cards: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(value["id"]): value for value in cards}


__all__ = ["card", "cards_by_id", "placeholder_card"]
