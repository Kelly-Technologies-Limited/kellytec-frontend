"""Canonical shared components."""

from kellytec_design_system.contract import TabPanel, Tab

from .page import render_page
from .panels import render_notices, render_panels
from .tabs import render_tabs
from .toolbar import render_toolbar

__all__ = [
    "TabPanel", "Tab", "render_notices", "render_panels",
    "render_tabs", "render_toolbar", "render_page",
]
