import ast
import hashlib
import json
import re
import sys
from importlib import metadata
from pathlib import Path

from kellytec_design_system.assets import ROOT, design_system_css, shared_ui_script
from kellytec_design_system.components.login import render_login
from kellytec_design_system.components.toolbar import render_toolbar








def test_toolbar_requires_application_owned_actions():
    assert '<button' not in render_toolbar(title="Page", updated_initial="Now")
    html = render_toolbar(title="Compute", updated_initial="Logged in as <unsafe>", actions_html='<button id="sign-out">Sign out</button>')
    assert "&lt;unsafe&gt;" in html and "<unsafe>" not in html
    assert 'id="sign-out"' in html and 'id="refresh"' not in html


def test_body_buttons_share_toolbar_control_styles():
    css = design_system_css()
    rules = [(set(part.strip() for part in selectors.split(",")), body)
             for selectors, body in re.findall(r"([^{}]+)\{([^{}]+)\}", css)]
    for suffix in ("", ":hover"):
        matches = [body for selectors, body in rules
                   if '[data-ui="button"]' + suffix in selectors
                   and ".toolbar button" + suffix in selectors]
        assert len(matches) == 1
        assert "background:" in matches[0]
    # Existing native disabled and keyboard focus states also cover these controls.
    assert ":where(button, input, select):disabled" in css
    assert ":where(button, input, select, .tab, [tabindex]):focus-visible" in css


def test_login_supports_provider_form_without_password_or_auth_logic():
    html = render_login(app_name="Compute", favicon="/favicon.svg", instruction="Use your company account.", form_html='<button id="google">Sign in with Google</button>')
    assert 'id="google"' in html
    assert 'type="password"' not in html
    assert "Use your company account." in html
