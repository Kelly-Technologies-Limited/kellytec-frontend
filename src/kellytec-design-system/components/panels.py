"""Canonical notice and panel components."""

from html import escape

from kellytec_design_system.contract.tab_panel import TabPanel


def render_notices() -> str:
    return (
        '<div class="notices page-container" data-ui="notices">'
        '<div class="global-message" data-ui-type="supporting" id="message" '
        'role="status" aria-live="polite" hidden></div></div>'
    )


def render_panels(panels: tuple[TabPanel, ...]) -> str:
    if not panels:
        raise ValueError("page requires at least one panel")
    views = [panel.view for panel in panels]
    if len(set(views)) != len(views):
        raise ValueError("panel views must be unique")
    sections = [
        '<section class="view" data-ui="panel" id="view-' + escape(panel.view, quote=True)
        + '" data-view-panel="' + escape(panel.view, quote=True) + '"'
        + ("" if index == 0 else " hidden") + "></section>"
        for index, panel in enumerate(panels)
    ]
    return (
        '<main class="page-container page-body" data-ui="page-body">'
        + "".join(sections) + "</main>"
    )


__all__ = ["render_notices", "render_panels"]
