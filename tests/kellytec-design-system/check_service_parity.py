"""Compare the installed shared component to frozen Operations 1.0.0 presentation.

Run with Python 3.12, Playwright and an explicitly selected local Chromium binary.
This check never updates its reference and blocks every network request.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path

from kellytec_design_system.assets import design_system_css, font_stylesheet, shared_ui_script
from playwright.sync_api import sync_playwright


REFERENCE = Path(__file__).parent / "fixtures/services-before"
NAMES = [
    "historical-ingest-databento", "historical-ingest-thetadata",
    "historical-ingest-optionsdepth", "historical-standardize-databento",
    "historical-standardize-thetadata", "historical-standardize-optionsdepth",
]
STATES = ["success", "in_progress", "failed", "warning", "waiting", ""]
ROWS = [
    {"name": name, "kind": "job", "status": state,
     "status_at": "2026-10-31T08:54:44+00:00" if state else None,
     "reason": "Job deployment is ready; latest execution completed <successfully> & retained"}
    for name, state in zip(NAMES, STATES)
]
OLD_RENDER = """rows => {
  const renderer = window.MonitorUI.rendererFor({renderer:'servers'});
  const host = document.createElement('div');
  host.innerHTML = renderer.render({servers:[{project_id:'kellytec-data',
    workloads:{jobs:{rows}}}]}).html;
  return [...host.querySelectorAll('.monitor-workload-table, [data-ui="service-table"]')].at(-1).outerHTML;
}"""
NEW_RENDER = """rows => window.MonitorUI.serviceTable(rows.map(row => {
  const full = row.status_at ? window.MonitorUI.value({kind:'datetime_et',value:row.status_at}) : '—';
  const match = full.match(/(\\d{2}:\\d{2}:\\d{2}\\s+E[DS]?T)$/);
  return {name:row.name,status:row.status || '—',reason:row.reason,
    updatedAt:{short:match ? match[1] : full,full},
    tone:({success:'healthy',in_progress:'healthy',failed:'critical',warning:'warning'})[row.status] || 'unknown'};
}))"""
METRICS = """selector => [...document.querySelector(selector).querySelectorAll('*')].map(el => {
  const s=getComputedStyle(el), r=el.getBoundingClientRect();
  return {text:el.childElementCount ? null : el.textContent,
    box:[r.x,r.y,r.width,r.height],font:s.font,fontFamily:s.fontFamily,
    color:s.color,background:s.backgroundColor,border:s.border,
    padding:s.padding,gap:s.gap,radius:s.borderRadius,
    overflow:s.overflow,textOverflow:s.textOverflow,align:s.textAlign};
})"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-path", required=True)
    parser.add_argument("--operations-renderer", type=Path)
    parser.add_argument("--operations-css", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((REFERENCE / "manifest.json").read_text())
    for filename, entry in manifest["files"].items():
        assert hashlib.sha256((REFERENCE / filename).read_bytes()).hexdigest() == entry["sha256"]
    assert hashlib.sha256(font_stylesheet().encode()).hexdigest() == manifest["font_stylesheet_sha256"]
    report = {
        "reference": manifest, "cases": [], "network_requests": [],
        "python": platform.python_version(), "playwright": version("playwright"),
        "candidate_version": version("kellytec-design-system"),
        "candidate_css_sha256": hashlib.sha256(design_system_css().encode()).hexdigest(),
        "candidate_js_sha256": hashlib.sha256(shared_ui_script().encode()).hexdigest(),
        "operations_renderer_sha256": hashlib.sha256(args.operations_renderer.read_bytes()).hexdigest() if args.operations_renderer else None,
        "operations_css_sha256": hashlib.sha256(args.operations_css.read_bytes()).hexdigest() if args.operations_css else None,
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser_path, headless=True)
        report["browser"] = browser.version
        for width in (390, 520, 521, 900, 1440):
            context = browser.new_context(viewport={"width": width, "height": 800}, device_scale_factor=1)
            context.route("**/*", lambda route: (report["network_requests"].append(route.request.url), route.abort()))
            captures = []
            modes = ["reference", "component"]
            if args.operations_renderer:
                assert args.operations_css
                modes.append("operations")
            for mode in modes:
                page = context.new_page()
                css = font_stylesheet() + (REFERENCE / "design-system.css").read_text() if mode == "reference" else design_system_css()
                js = (REFERENCE / "design-system.js").read_text() if mode == "reference" else shared_ui_script()
                if mode == "reference":
                    css += (REFERENCE / "operations.css").read_text()
                elif mode == "operations":
                    css += args.operations_css.read_text()
                page.set_content('<style>' + css + '</style><div id="fixture" class="monitor-cell" style="width:calc(100vw - 32px);max-width:700px;margin:16px"></div>')
                page.add_script_tag(content=js)
                if mode != "component":
                    page.add_script_tag(content=(REFERENCE / "operations.js").read_text() if mode == "reference" else args.operations_renderer.read_text())
                html = page.evaluate(NEW_RENDER if mode == "component" else OLD_RENDER, ROWS)
                page.locator("#fixture").evaluate("(el,html) => el.innerHTML=html", html)
                page.evaluate("document.fonts.ready")
                image = page.locator("#fixture").screenshot(path=str(args.output / f"{mode}-{width}.png"))
                metrics = page.evaluate(METRICS, "#fixture")
                captures.append((mode, image, metrics))
                page.close()
            reference = captures[0]
            for mode, image, metrics in captures[1:]:
                (args.output / f"{mode}-{width}-metrics.json").write_text(json.dumps(metrics, indent=2))
                (args.output / f"reference-{width}-metrics.json").write_text(json.dumps(reference[2], indent=2))
                assert metrics == reference[2], f"Computed presentation differs: {mode} at {width}px"
                assert image == reference[1], f"Rendered pixels differ: {mode} at {width}px"
                report["cases"].append({"mode":mode,"viewport_width":width,"pixel_equal":True,"computed_styles_equal":True,"image_sha256":hashlib.sha256(image).hexdigest()})
            context.close()
        browser.close()
    assert not report["network_requests"], "Unexpected external resource requested"
    (args.output / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Service parity passed: {len(report['cases'])} cases")


if __name__ == "__main__":
    main()
