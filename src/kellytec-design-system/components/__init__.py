"""Canonical shared monitor components."""

from kellytec_design_system.contracts import MonitorPanel, MonitorTab

from .page import render_monitor_page
from .panels import monitor_notices, monitor_panels
from .tabs import monitor_tabs
from .toolbar import monitor_toolbar

__all__ = [
    "MonitorPanel", "MonitorTab", "monitor_notices", "monitor_panels",
    "monitor_tabs", "monitor_toolbar", "render_monitor_page",
]
