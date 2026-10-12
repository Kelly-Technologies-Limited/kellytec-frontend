"""Canonical tab navigation component."""

from html import escape

from kellytec_design_system.contracts.tab import MonitorTab


def monitor_tabs(*, tabs: tuple[MonitorTab, ...], aria_label: str) -> str:
    buttons = []
    for index, tab in enumerate(tabs):
        badge = (
            '<span class="tab-badge" data-ui-type="badge-count" data-tab-badge="'
            + escape(tab.view, quote=True) + '" hidden></span>'
            if tab.badge else ""
        )
        buttons.append(
            '<button class="tab" data-ui="tab" data-ui-type="tab-label" type="button" data-view="'
            + escape(tab.view, quote=True) + '" aria-selected="'
            + ("true" if index == 0 else "false") + '">' + _tab_icon(tab)
            + '<span class="tab-label">' + escape(tab.label) + "</span>" + badge + "</button>"
        )
    return (
        '<nav class="tabs monitor-container" data-ui="tabs" style="--monitor-tab-count:'
        + str(len(tabs)) + '" aria-label="' + escape(aria_label, quote=True) + '">' + "".join(buttons) + "</nav>"
    )


def _tab_icon(tab: MonitorTab) -> str:
    status = (
        '<span class="tab-icon-status tab-icon-status-'
        + escape(tab.icon_status, quote=True) + '"></span>'
        if tab.icon_status else ""
    )
    return (
        '<span class="tab-icon tab-icon-' + escape(tab.icon, quote=True)
        + '" aria-hidden="true"><span class="tab-icon-glyph"></span>' + status + "</span>"
    )


__all__ = ["monitor_tabs"]
