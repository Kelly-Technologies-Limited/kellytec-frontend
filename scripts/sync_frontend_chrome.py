"""Generate Monitor brand chrome from the frontend source.

The public frontend owns the Kelly Technologies brand assets and footer copy.
The UI wheel contains generated fragments; consumers need no frontend checkout.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from pathlib import Path

from build_site import build_css, read, render_header

CHROME_SELECTORS = (
    ":root",
    ".container",
    ".site-header",
    ".site-header.scrolled",
    ".nav",
    ".brand",
    ".brand-logo",
    ".site-footer",
    ".footer-disclaimer",
)


@dataclass(frozen=True)
class FrontendChrome:
    header: str
    footer: str
    css: str


def build_frontend_chrome(frontend_root: Path) -> FrontendChrome:
    styles_css = build_css(frontend_root)
    logo_svg = _read_svg_text(frontend_root / "kellytec-design-system" / "static" / "logo.svg").encode("utf-8")
    homepage_href = _frontend_homepage_href(frontend_root)

    source_header = render_header(
        asset_prefix="", home_href="#top", gp_current=False, frontend_root=frontend_root
    )
    footer = read(frontend_root / "kellytec-website" / "chrome" / "footer.html")

    logo_uri = "data:image/svg+xml;base64," + base64.b64encode(logo_svg).decode("ascii")
    header = _monitor_header(
        source_header=source_header,
        homepage_href=homepage_href,
        logo_uri=logo_uri,
    )

    css = _extract_chrome_css(styles_css)
    return FrontendChrome(header=header.strip(), footer=footer.strip(), css=css)


def write_frontend_chrome(frontend_root: Path) -> None:
    chrome = build_frontend_chrome(frontend_root)
    generated_dir = frontend_root / "kellytec-design-system" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    (generated_dir / "frontend_header.html").write_text(chrome.header + "\n", encoding="utf-8")
    (generated_dir / "frontend_footer.html").write_text(chrome.footer + "\n", encoding="utf-8")
    (generated_dir / "frontend_chrome.css").write_text(chrome.css, encoding="utf-8")


def _read_svg_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _frontend_homepage_href(frontend_root: Path) -> str:
    cname = frontend_root / "kellytec-website" / "CNAME"
    if cname.exists():
        domain = cname.read_text(encoding="utf-8").strip()
        if domain:
            return f"https://{domain}/"
    return "/"


def _monitor_header(*, source_header: str, homepage_href: str, logo_uri: str) -> str:
    brand_match = re.search(r'<a class="brand".*?</a>', source_header, flags=re.S)
    if not brand_match:
        raise ValueError("Could not find frontend brand link")
    brand = brand_match.group(0)
    brand = re.sub(r'href="[^"]*"', f'href="{homepage_href}"', brand, count=1)
    brand = brand.replace('src="assets/logo.svg"', f'src="{logo_uri}"')
    return f"""<header class="site-header" id="top">
    <div class="container nav">
      {brand}
    </div>
  </header>"""


def _extract_chrome_css(css_text: str) -> str:
    css_without_comments = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)
    blocks = _matching_blocks(css_without_comments)
    body = "\n\n".join(blocks).strip()
    body = body.replace("--font-mono", "--brand-font-mono").replace("--font-sans", "--brand-font-sans")
    return "/* Generated from kellytec-frontend/kellytec-website/styles/. Run scripts/sync_frontend_chrome.py. */\n" + body + "\n"


def _matching_blocks(css_text: str) -> list[str]:
    selected: list[str] = []
    for prelude, body, full in _iter_blocks(css_text):
        prelude = prelude.strip()
        if not prelude:
            continue
        if prelude.startswith("@media"):
            media_blocks = [
                inner_full
                for inner_prelude, _inner_body, inner_full in _iter_blocks(body)
                if _matches_selector(inner_prelude)
            ]
            if media_blocks:
                selected.append(prelude + " {\n" + "\n\n".join(_indent(block) for block in media_blocks) + "\n}")
            continue
        if _matches_selector(prelude):
            selected.append(full.strip())
    return selected


def _iter_blocks(css_text: str) -> list[tuple[str, str, str]]:
    blocks: list[tuple[str, str, str]] = []
    cursor = 0
    length = len(css_text)
    while cursor < length:
        open_idx = css_text.find("{", cursor)
        if open_idx < 0:
            break
        prelude = css_text[cursor:open_idx]
        depth = 1
        index = open_idx + 1
        while index < length and depth:
            char = css_text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            index += 1
        if depth:
            raise ValueError("Unbalanced CSS braces in frontend stylesheet")
        body = css_text[open_idx + 1 : index - 1]
        full = css_text[cursor:index]
        blocks.append((prelude, body, full))
        cursor = index
    return blocks


def _matches_selector(prelude: str) -> bool:
    selectors = [selector.strip() for selector in prelude.split(",")]
    return any(selector in CHROME_SELECTORS for selector in selectors)


def _indent(text: str) -> str:
    return "\n".join("  " + line if line else line for line in text.strip().splitlines())


def main() -> None:
    frontend_root = Path(__file__).resolve().parents[1]
    write_frontend_chrome(frontend_root)


if __name__ == "__main__":
    main()
