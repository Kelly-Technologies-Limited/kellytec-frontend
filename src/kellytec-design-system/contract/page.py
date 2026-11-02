"""Canonical page declaration."""

from __future__ import annotations

from dataclasses import dataclass
from .tab import Tab
from .tab_panel import TabPanel


@dataclass(frozen=True)
class Page:
    title: str
    tabs_aria_label: str
    updated_initial: str
    tabs: tuple[Tab, ...]
    panels: tuple[TabPanel, ...]
    toolbar_title_lines: tuple[str, ...] = ()
    toolbar_aria_label: str = "Page controls"

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("page title is required")
        if any(not line.strip() for line in self.toolbar_title_lines):
            raise ValueError("toolbar title lines must be non-empty")
        if not self.tabs:
            raise ValueError("page requires tabs")
        if self.tabs[0].disabled:
            raise ValueError("the initial tab must be enabled")
        if len({tab.view for tab in self.tabs}) != len(self.tabs):
            raise ValueError("tab views must be unique")
        if tuple(tab.view for tab in self.tabs if not tab.disabled) != tuple(
            panel.view for panel in self.panels
        ):
            raise ValueError("tabs and panels must have identical ordered views")


__all__ = ["Page"]
