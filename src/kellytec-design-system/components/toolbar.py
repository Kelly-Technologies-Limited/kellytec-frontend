"""Canonical toolbar component."""

from html import escape


def render_toolbar(
    *,
    title: str,
    updated_initial: str,
    title_lines: tuple[str, ...] = (),
    actions_html: str = "",
    aria_label: str = "Page controls",
) -> str:
    """Render text safely; optional actions_html is trusted application markup."""
    visible_title = title_lines or (title,)
    title_html = "".join(
        f'<span class="page-title-line">{escape(line)}</span>'
        for line in visible_title
    )
    return (
        '<section class="toolbar page-container" data-ui="toolbar" '
        'aria-label="' + escape(aria_label, quote=True) + '"><div><h1 data-ui-type="page-title" '
        'aria-label="'
        + escape(title, quote=True)
        + '">'
        + title_html
        + '</h1><div class="subtle" data-ui-type="page-subtitle" id="page-updated">'
        + escape(updated_initial)
        + '</div></div><div class="actions">'
        + actions_html + '</div></section>'
    )


__all__ = ["render_toolbar"]
