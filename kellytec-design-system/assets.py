"""Deterministic shared monitor design-system assets."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parent

_STYLE_FILES = (
    "tokens/palette.css",
    "tokens/colors.css",
    "tokens/typography.css",
    "tokens/spacing.css",
    "tokens/sizing.css",
    "tokens/borders.css",
    "tokens/charts.css",
    "tokens/motion.css",
    "tokens/layers.css",
    "primitives/page.css",
    "primitives/toolbar.css",
    "primitives/tab.css",
    "primitives/card.css",
    "primitives/metric.css",
    "primitives/badge.css",
    "primitives/table.css",
    "primitives/state_matrix.css",
    "primitives/log_table.css",
    "primitives/controls.css",
    "primitives/feedback.css",
    "primitives/tooltip.css",
    "primitives/summary.css",
    "primitives/chart.css",
    "primitives/responsive.css",
)
_SCRIPT_FILES = (
    "runtime/dom.js",
    "formatters/value.js",
    "components/badge.js",
    "components/summary.js",
    "components/tooltip.js",
    "charts/svg.js",
    "charts/text.js",
    "charts/responsive.js",
    "charts/series.js",
    "charts/legend.js",
    "components/cell.js",
    "components/loading.js",
    "components/card.js",
    "components/table.js",
    "components/state_matrix.js",
    "components/log_table.js",
    "components/placeholder.js",
    "components/metric_grid.js",
)


@lru_cache(maxsize=1)
def design_system_css() -> str:
    """Return the exact token and primitive stylesheet used by every page."""

    frontend_css = (ROOT / "generated" / "frontend_chrome.css").read_text(
        encoding="utf-8"
    )
    parts = [
        font_stylesheet(),
        frontend_css,
        *(_read(ROOT / "static" / "styles" / name) for name in _STYLE_FILES),
    ]
    return "\n\n".join(part.rstrip() for part in parts) + "\n"


@lru_cache(maxsize=1)
def shared_ui_script() -> str:
    """Return shared runtime, value formatters and generic components in order."""

    root = ROOT / "static" / "js"
    return "\n;\n".join(_read(root / name).rstrip() for name in _SCRIPT_FILES) + "\n"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def font_stylesheet() -> str:
    """Self-contained licensed fonts, with no network or application URL coupling."""
    root = ROOT / "static" / "fonts"
    css = _read(root / "fonts.css")
    def inline(match: re.Match[str]) -> str:
        name = match.group(1)
        payload = base64.b64encode((root / name).read_bytes()).decode("ascii")
        return "url(data:font/ttf;base64," + payload + ")"
    return re.sub(r"url\((font-\d+\.ttf)\)", inline, css)


__all__ = ["ROOT", "design_system_css", "shared_ui_script", "font_stylesheet"]
