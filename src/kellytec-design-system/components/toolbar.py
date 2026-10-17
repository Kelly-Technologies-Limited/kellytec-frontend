"""Canonical toolbar component."""

from html import escape


def monitor_toolbar(
    *,
    title: str,
    updated_initial: str,
    title_lines: tuple[str, ...] = (),
    actions_html: str | None = None,
    aria_label: str = "Monitor controls",
) -> str:
    """Render text safely; optional actions_html is trusted application markup."""
    visible_title = title_lines or (title,)
    title_html = "".join(
        f'<span class="monitor-page-title-line">{escape(line)}</span>'
        for line in visible_title
    )
    if actions_html is None:
        actions_html = (
            '<span id="monitor-loading" class="monitor-request-status" '
            'data-ui-type="supporting" role="status" aria-live="polite" aria-hidden="true">'
            '<span class="monitor-loading-spinner" aria-hidden="true"></span>'
            '<span>Loading…</span></span>'
            '<span class="badge" id="monitor-status">Unknown</span>'
            '<button type="button" id="monitor-refresh">Refresh</button>'
        )
    return (
        '<section class="monitor-toolbar monitor-container" data-ui="toolbar" '
        'aria-label="' + escape(aria_label, quote=True) + '"><div><h1 data-ui-type="page-title" '
        'aria-label="'
        + escape(title, quote=True)
        + '">'
        + title_html
        + '</h1><div class="subtle" data-ui-type="page-subtitle" id="monitor-updated">'
        + escape(updated_initial)
        + '</div></div><div class="monitor-actions">'
        + actions_html + '</div></section>'
    )


__all__ = ["monitor_toolbar"]
