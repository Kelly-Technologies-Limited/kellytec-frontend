from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import urlsplit

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import GENERATED_FILES, PUBLIC_FILES, build_public_site


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in {"href", "src", "data-reveal-image"} or not value:
                continue
            url = urlsplit(value)
            if not url.scheme and not url.netloc and url.path:
                self.paths.append(url.path)


def test_public_artifact_preserves_pages_and_excludes_source(tmp_path):
    destination = tmp_path / "site"
    build_public_site(destination)
    assert {p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()} == set(PUBLIC_FILES) | set(GENERATED_FILES)
    # Check served URLs after the source move, including the legacy GP route.
    for name in ("index.html", "gp/index.html", "gp/monitor/index.html"):
        page = destination / name
        links = LocalLinks()
        links.feed(page.read_text(encoding="utf-8"))
        for path in links.paths:
            target = (destination / path.lstrip("/")) if path.startswith("/") else page.parent / path
            if path.endswith("/"):
                target /= "index.html"
            assert target.resolve().is_relative_to(destination)
            assert target.is_file(), (name, path)


def test_public_artifact_rejects_stale_private_files(tmp_path):
    (tmp_path / "factor.py").write_text("private")
    with pytest.raises(ValueError, match="outside the public allowlist"):
        build_public_site(tmp_path)
    assert (tmp_path / "factor.py").read_text() == "private"
