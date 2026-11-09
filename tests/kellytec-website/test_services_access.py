"""Exercise service grants, blank placeholders and navigation in a real browser."""

import json
import mimetypes
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".github/automation/common/helpers"))
from brand_assets import build_public_site


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path=os.environ.get("KELLYTEC_UI_BROWSER_PATH")) as instance:
            yield instance


@pytest.fixture
def website(browser, tmp_path):
    build_public_site(tmp_path)
    page = browser.new_page()
    page.route("**/*", lambda route: route.abort())
    def public(route):
        path = urlsplit(route.request.url).path.lstrip("/")
        if not path or path.endswith("/"):
            path += "index.html"
        source = tmp_path / path
        if not source.resolve().is_relative_to(tmp_path) or not source.is_file():
            return route.fulfill(status=404)
        route.fulfill(path=source, content_type=mimetypes.guess_type(str(source))[0] or "application/octet-stream")
    page.route("https://kellytec.io/**", public)
    yield page
    page.close()


def identity(page, grants, *, status=200):
    calls = []
    def respond(route):
        calls.append(route.request)
        headers = {"Access-Control-Allow-Origin": "https://kellytec.io", "Access-Control-Allow-Credentials": "true",
                   "Access-Control-Allow-Headers": "content-type,x-csrf-token", "Access-Control-Allow-Methods": "GET,POST"}
        if route.request.method == "OPTIONS":
            return route.fulfill(status=200, headers=headers)
        value = {"user": {"name": "Researcher <safe>"}, "services": grants, "csrf": "browser-proof"}
        route.fulfill(status=status, content_type="application/json", headers=headers, body=json.dumps(value))
    page.route("https://auth.kellytec.io/**", respond)
    return calls


@pytest.mark.parametrize("width", [1440, 390])
@pytest.mark.parametrize("grants", [("data", "research", "investor", "monitor"), ("research", "monitor"), ()])
def test_authorized_cards_keep_six_slots_and_empty_cards_have_no_content(website, width, grants):
    page = website
    page.set_viewport_size({"width": width, "height": 1000})
    identity(page, list(grants))
    page.goto("https://kellytec.io/services/")
    expect(page.locator("body")).to_have_css("opacity", "1")
    expect(page.locator("#account-name")).to_have_text("Researcher <safe>")
    expect(page.locator(".service-slot")).to_have_count(6)
    expect(page.locator(".service-slot a")).to_have_count(len(grants))
    expect(page.locator(".service-slot:empty")).to_have_count(6-len(grants))
    assert page.locator(".service-slot:empty").evaluate_all("nodes=>nodes.every(n=>!n.innerText && n.getAttribute('aria-hidden')==='true' && !n.querySelector('a,button,[tabindex]'))")
    assert page.locator(".service-grid").evaluate("node=>getComputedStyle(node).gridTemplateColumns.split(' ').length") == (3 if width==1440 else 1)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    if len(grants)>1:
        page.locator(".service-slot a").first.focus()
        page.keyboard.press("Tab")
        expect(page.locator(".service-slot a").nth(1)).to_be_focused()
    assert page.locator(".service-slot").all_text_contents()[-2:] == ["", ""]


def test_anonymous_visitors_return_to_single_google_login(website):
    identity(website, [], status=401)
    website.goto("https://kellytec.io/services/")
    expect(website).to_have_url("https://kellytec.io/login/")
    expect(website.locator("body")).to_have_css("opacity", "1")
    expect(website.locator(".login-google")).to_have_attribute("href", "https://auth.kellytec.io/login")
    expect(website.locator('input[type="password"]')).to_have_count(0)


def test_identity_failure_leaves_all_cards_blank(website):
    identity(website, [], status=503)
    website.goto("https://kellytec.io/services/")
    expect(website.locator("#access-status")).not_to_be_empty()
    expect(website.locator(".service-slot:empty")).to_have_count(6)
    expect(website.locator(".service-slot a")).to_have_count(0)


def test_platform_login_passes_flow_and_fragment_to_google_link(website):
    identity(website, [], status=401)
    flow = 'a' * 43
    website.goto('https://kellytec.io/login/?flow=' + flow + '#nodes')
    expect(website.locator('.login-google')).to_have_attribute(
        'href', 'https://auth.kellytec.io/login?flow=' + flow + '#nodes')
    website.locator('.login-google').click()
    expect(website).to_have_url('https://auth.kellytec.io/login?flow=' + flow + '#nodes')


def test_signed_in_platform_login_resumes_flow_instead_of_services(website):
    identity(website, ['research'])
    flow = 'b' * 43
    website.goto('https://kellytec.io/login/?flow=' + flow)
    expect(website).to_have_url('https://auth.kellytec.io/login?flow=' + flow)


@pytest.mark.parametrize('flow', ['https://attacker.example/', '//attacker.example/', 'short'])
def test_login_ignores_invalid_flow(website, flow):
    identity(website, [], status=401)
    website.goto('https://kellytec.io/login/?flow=' + flow)
    expect(website.locator('.login-google')).to_have_attribute('href', 'https://auth.kellytec.io/login')
