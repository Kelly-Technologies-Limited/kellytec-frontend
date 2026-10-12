"""The only HTML page renderer used by monitor applications."""

from __future__ import annotations

from functools import lru_cache
from html import escape
from pathlib import Path

from kellytec_design_system.contracts.page import MonitorPage

from .panels import monitor_notices, monitor_panels
from .tabs import monitor_tabs
from .toolbar import monitor_toolbar


ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def _template() -> str:
    return (ROOT / "templates" / "page.html").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _brand_header() -> str:
    return (ROOT / "generated" / "frontend_header.html").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _brand_footer() -> str:
    return (ROOT / "generated" / "frontend_footer.html").read_text(encoding="utf-8")


def render_monitor_page(page: MonitorPage) -> str:
    if not isinstance(page, MonitorPage):
        raise TypeError("page must be MonitorPage")
    return (
        _template().replace("__MONITOR_DOCUMENT_TITLE__", escape(page.title))
        .replace("__MONITOR_FAVICON_PATH__", escape(page.favicon_path, quote=True))
        .replace("__MONITOR_STYLESHEET_PATH__", escape(page.stylesheet_path, quote=True))
        .replace("<!-- __FRONTEND_HEADER__ -->", _brand_header())
        .replace(
            "<!-- __MONITOR_TOOLBAR__ -->",
            monitor_toolbar(
                title=page.title,
                updated_initial=page.updated_initial,
                title_lines=page.toolbar_title_lines,
                actions_html=page.toolbar_actions_html,
                aria_label=page.toolbar_aria_label,
            ),
        )
        .replace("<!-- __MONITOR_TABS__ -->", monitor_tabs(tabs=page.tabs, aria_label=page.tabs_aria_label))
        .replace("<!-- __MONITOR_NOTICES__ -->", monitor_notices())
        .replace("<!-- __MONITOR_PANELS__ -->", monitor_panels(page.panels))
        .replace("<!-- __FRONTEND_FOOTER__ -->", _brand_footer())
        .replace("<!-- __MONITOR_SCRIPTS__ -->", page.scripts_html)
    )


__all__ = ["render_monitor_page"]
