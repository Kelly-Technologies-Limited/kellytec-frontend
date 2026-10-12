"""Canonical tab and panel declarations."""

from __future__ import annotations

from dataclasses import dataclass


def _valid_view(value: str) -> bool:
    return bool(value) and value.replace("-", "").isalnum()


@dataclass(frozen=True)
class MonitorTab:
    view: str
    label: str
    icon: str
    badge: bool = False
    icon_status: str | None = None

    def __post_init__(self) -> None:
        if not _valid_view(self.view):
            raise ValueError("monitor tab view is invalid")
        if not self.label.strip() or not self.icon.strip():
            raise ValueError("monitor tab label and icon are required")
        if self.icon_status not in {None, "active", "closed"}:
            raise ValueError("monitor tab icon status is invalid")


@dataclass(frozen=True)
class MonitorPanel:
    view: str

    def __post_init__(self) -> None:
        if not _valid_view(self.view):
            raise ValueError("monitor panel view is invalid")


__all__ = ["MonitorPanel", "MonitorTab"]
