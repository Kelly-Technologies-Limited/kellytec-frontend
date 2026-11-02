"""Unprotected login presentation; no authentication or redirect decisions."""

from functools import lru_cache
from html import escape
from string import Template
from kellytec_design_system.assets import ROOT


@lru_cache(maxsize=1)
def _styles() -> str:
    base = ROOT / "static" / "styles"
    return "\n".join(
        (base / name).read_text(encoding="utf-8")
        for name in (
            "tokens/palette.css",
            "tokens/colors.css",
            "tokens/typography.css",
            "tokens/borders.css",
            "primitives/login.css",
        )
    )


def render_login(
    *, app_name: str, favicon: str, instruction: str, form_html: str,
    error: str = "", scripts_html: str = "", brand_html: str = "",
) -> str:
    """Render login; form_html/scripts_html are trusted application markup.

    Authentication remains owned by the consuming application.
    """
    values = {
        key: escape(value, quote=True)
        for key, value in {
            "app_name": app_name,
            "favicon": favicon,
        }.items()
    }
    values["error"] = (
        '<p class="error" role="alert">' + escape(error) + "</p>" if error else ""
    )
    values["styles"] = _styles()
    values["instruction"] = escape(instruction)
    values["scripts_html"] = scripts_html
    values["brand"] = brand_html
    values["form_html"] = form_html
    return Template(
        (ROOT / "templates" / "login.html").read_text(encoding="utf-8")
    ).substitute(values)
