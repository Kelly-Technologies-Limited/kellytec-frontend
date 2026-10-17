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
    *, app_name: str, favicon: str, action: str, next_path: str, error: str = "",
    instruction: str = "Enter the administrator password to continue.",
    form_html: str | None = None, scripts_html: str = "", brand_logo: bool = False,
) -> str:
    """Render login; form_html/scripts_html are trusted application markup.

    Authentication remains owned by the consuming application.
    """
    values = {
        key: escape(value, quote=True)
        for key, value in {
            "app_name": app_name,
            "favicon": favicon,
            "action": action,
            "next_path": next_path,
        }.items()
    }
    values["error"] = (
        '<p class="error" role="alert">' + escape(error) + "</p>" if error else ""
    )
    values["styles"] = _styles()
    values["instruction"] = escape(instruction)
    values["scripts_html"] = scripts_html
    values["brand"] = '<p class="brand">Kelly Technologies</p>'
    if brand_logo:
        import re
        header = (ROOT / "generated" / "frontend_header.html").read_text(encoding="utf-8")
        values["brand"] = re.search(r'<a class="brand".*?</a>', header, re.S).group(0)
    values["form_html"] = form_html if form_html is not None else (
        '<form method="post" action="' + values["action"] + '">'
        '<input type="hidden" name="next" value="' + values["next_path"] + '"/>'
        '<label data-ui-type="login-label" for="password">Password</label>'
        '<input id="password" name="password" type="password" autocomplete="current-password" autofocus required/>'
        '<button type="submit">Open Monitor</button></form>'
    )
    return Template(
        (ROOT / "templates" / "login.html").read_text(encoding="utf-8")
    ).substitute(values)
