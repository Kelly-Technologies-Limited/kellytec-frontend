"""The only HTML page renderer used by applications."""

from __future__ import annotations

from functools import lru_cache
from html import escape
from pathlib import Path

from kellytec_design_system.contract.page import Page

from .panels import render_notices, render_panels
from .tabs import render_tabs
from .toolbar import render_toolbar


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


def render_page(
    page: Page, *, favicon_path: str, stylesheet_path: str,
    scripts_html: str = "", toolbar_actions_html: str = "",
) -> str:
    """Render a semantic page; HTML extensions belong to trusted application renderers."""
    if not isinstance(page, Page):
        raise TypeError("page must be Page")
    if any(not value.startswith("/") or value.startswith("//") for value in (favicon_path, stylesheet_path)):
        raise ValueError("Asset paths must be absolute paths on the application origin")
    return (
        _template().replace("__PAGE_DOCUMENT_TITLE__", escape(page.title))
        .replace("__PAGE_FAVICON_PATH__", escape(favicon_path, quote=True))
        .replace("__PAGE_STYLESHEET_PATH__", escape(stylesheet_path, quote=True))
        .replace("<!-- __FRONTEND_HEADER__ -->", _brand_header())
        .replace(
            "<!-- __PAGE_TOOLBAR__ -->",
            render_toolbar(
                title=page.title,
                updated_initial=page.updated_initial,
                title_lines=page.toolbar_title_lines,
                actions_html=toolbar_actions_html,
                aria_label=page.toolbar_aria_label,
            ),
        )
        .replace("<!-- __PAGE_TABS__ -->", render_tabs(tabs=page.tabs, aria_label=page.tabs_aria_label))
        .replace("<!-- __PAGE_NOTICES__ -->", render_notices())
        .replace("<!-- __PAGE_PANELS__ -->", render_panels(page.panels))
        .replace("<!-- __FRONTEND_FOOTER__ -->", _brand_footer())
        .replace("<!-- __PAGE_SCRIPTS__ -->", scripts_html)
    )


__all__ = ["render_page"]
