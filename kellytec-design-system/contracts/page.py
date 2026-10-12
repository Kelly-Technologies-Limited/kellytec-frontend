"""Canonical monitor page declaration."""

from __future__ import annotations

from dataclasses import dataclass
from .tab import MonitorPanel, MonitorTab


@dataclass(frozen=True)
class MonitorPage:
    title: str
    favicon_path: str
    stylesheet_path: str
    tabs_aria_label: str
    updated_initial: str
    tabs: tuple[MonitorTab, ...]
    panels: tuple[MonitorPanel, ...]
    scripts_html: str
    toolbar_title_lines: tuple[str, ...] = ()
    toolbar_actions_html: str | None = None
    toolbar_aria_label: str = "Monitor controls"

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("monitor page title is required")
        if any(not line.strip() for line in self.toolbar_title_lines):
            raise ValueError("toolbar title lines must be non-empty")
        for name in ("favicon_path", "stylesheet_path"):
            if not getattr(self, name).startswith("/"):
                raise ValueError(f"{name} must be an absolute application path")
        if not self.tabs:
            raise ValueError("monitor page requires tabs")
        if tuple(tab.view for tab in self.tabs) != tuple(
            panel.view for panel in self.panels
        ):
            raise ValueError("monitor tabs and panels must have identical ordered views")


__all__ = ["MonitorPage"]
