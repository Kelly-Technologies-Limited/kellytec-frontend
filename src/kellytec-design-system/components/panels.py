"""Canonical notice and panel components."""

from html import escape

from kellytec_design_system.contracts.tab import MonitorPanel


def monitor_notices() -> str:
    return (
        '<div class="monitor-notices monitor-container" data-ui="notices">'
        '<div class="monitor-global-message" data-ui-type="supporting" id="monitor-message" '
        'role="status" aria-live="polite" hidden></div></div>'
    )


def monitor_panels(panels: tuple[MonitorPanel, ...]) -> str:
    if not panels:
        raise ValueError("monitor page requires at least one panel")
    views = [panel.view for panel in panels]
    if len(set(views)) != len(views):
        raise ValueError("monitor panel views must be unique")
    sections = [
        '<section class="view" data-ui="panel" id="view-' + escape(panel.view, quote=True)
        + '" data-view-panel="' + escape(panel.view, quote=True) + '"'
        + ("" if index == 0 else " hidden") + "></section>"
        for index, panel in enumerate(panels)
    ]
    return (
        '<main class="monitor-container monitor-page-body" data-ui="page-body">'
        + "".join(sections) + "</main>"
    )


__all__ = ["monitor_notices", "monitor_panels"]
