import ast
import hashlib
import json
import sys
from importlib import metadata
from pathlib import Path

import tomllib
from kellytec_design_system.assets import ROOT, design_system_css, shared_ui_script


def test_distribution_identity_and_runtime_only_files() -> None:
    distribution = next(
        item
        for item in metadata.distributions(path=[str(ROOT.parent)])
        if item.metadata["Name"] == "kellytec-design-system"
    )
    frontend = Path(__file__).resolve().parents[4]
    declared = tomllib.loads(
        (frontend / "src/kellytec-design-system/pyproject.toml").read_text(encoding="utf-8")
    )
    assert distribution.version == declared["project"]["version"]
    for member in distribution.files:
        path = Path(str(member))
        assert not {"kellytec_ui", "tests", "build"}.intersection(path.parts)
        assert path.name != "setup.py"
    assert (ROOT / "static/logo.svg").is_file()
    assert (ROOT / "static/logo-light.svg").is_file()


def test_package_resources_and_font_hashes():
    assert (ROOT / "templates/page.html").is_file()
    assert (ROOT / "static/favicon.svg").is_file()
    assert "data:font/ttf;base64," in design_system_css()
    assert "https://fonts.googleapis.com" not in (ROOT / "templates/page.html").read_text()
    assert "UI.cell = function" in shared_ui_script()
    fonts = ROOT / "static/fonts"
    manifest = json.loads((fonts / "sources.json").read_text())
    for row in manifest["files"]:
        assert hashlib.sha256((fonts / row["file"]).read_bytes()).hexdigest() == row["sha256"]
    assert len(list(fonts.glob("*-OFL.txt"))) == 4


def test_shared_python_has_no_application_dependencies():
    for path in ROOT.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = (
                [n.name for n in node.names]
                if isinstance(node, ast.Import)
                else [node.module]
                if isinstance(node, ast.ImportFrom) and node.module and not node.level
                else []
            )
            assert all(
                name.split(".")[0] in sys.stdlib_module_names | {"kellytec_design_system"}
                for name in names
            ), path


def test_brand_is_generated_from_frontend_sources():
    frontend = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(frontend / ".github/automation/common/helpers"))
    from brand_assets import build_frontend_chrome

    chrome = build_frontend_chrome(frontend)
    assert (ROOT / "generated/frontend_header.html").read_text(
        encoding="utf-8"
    ).strip() == chrome.header
    assert (ROOT / "generated/frontend_footer.html").read_text(
        encoding="utf-8"
    ).strip() == chrome.footer
    assert (ROOT / "generated/frontend_chrome.css").read_text(encoding="utf-8") == chrome.css
    assert (ROOT / "static/favicon.svg").read_text(encoding="utf-8") == (
        frontend / "src/kellytec-design-system/static/favicon.svg"
    ).read_text(encoding="utf-8")
