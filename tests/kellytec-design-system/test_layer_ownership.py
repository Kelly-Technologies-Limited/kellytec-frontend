"""Shared components must select defined semantic layers before publication."""

import os
import re

from playwright.sync_api import sync_playwright

from kellytec_design_system.assets import ROOT


def test_every_component_layer_uses_a_defined_semantic_token():
    with sync_playwright() as playwright:
        with playwright.chromium.launch(
            executable_path=os.environ.get("KELLYTEC_UI_BROWSER_PATH"),
        ) as browser:
            page = browser.new_page()
            page.route("**/*", lambda route: route.abort())
            # Website chrome has its own owner. Inspect every installed shared
            # component and token stylesheet, matching consumer theme checks.
            css = "\n".join(path.read_text() for path in sorted(
                (ROOT / "static/styles").rglob("*.css"),
            ))
            page.set_content("<style>" + css + "</style>")
            layers = page.evaluate(r"""() => {
                const result = [];
                const visit = rules => Array.from(rules).forEach(rule => {
                    if (rule.style?.zIndex) {
                        const value = rule.style.zIndex;
                        const token = value.match(/^var\((--layer-[a-z-]+)\)$/)?.[1];
                        result.push({selector: rule.selectorText, value, resolved: token
                            ? getComputedStyle(document.documentElement).getPropertyValue(token).trim()
                            : ''});
                    }
                    if (rule.cssRules) visit(rule.cssRules);
                });
                Array.from(document.styleSheets).forEach(sheet => visit(sheet.cssRules));
                return result;
            }""")
    assert layers, "The installed stylesheet must contain its component layer declarations"
    invalid = [row for row in layers if not re.fullmatch(
        r"var\(--layer-[a-z-]+\)", row["value"],
    ) or not re.fullmatch(r"-?\d+", row["resolved"])]
    assert invalid == [], f"Unowned or undefined component layers: {invalid}"
