"""Canonical tab and panel declarations."""

from __future__ import annotations

from dataclasses import dataclass


def _valid_view(value: str) -> bool:
    return bool(value) and value.replace("-", "").isalnum()


@dataclass(frozen=True)
class Tab:
    view: str
    label: str
    icon: str
    badge: bool = False
    icon_status: str | None = None
    disabled: bool = False

    def __post_init__(self) -> None:
        if not _valid_view(self.view):
            raise ValueError("tab view is invalid")
        if not self.disabled and (not self.label.strip() or not self.icon.strip()):
            raise ValueError("tab label and icon are required")
        if self.icon_status not in {None, "active", "closed"}:
            raise ValueError("tab icon status is invalid")


__all__ = ["Tab"]
