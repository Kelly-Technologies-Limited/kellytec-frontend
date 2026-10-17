"""Build the public website into dist/site using an explicit file allowlist."""

from __future__ import annotations

import base64
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src/kellytec-website"

CHROME = SRC / "chrome"
HOME = SRC / "pages" / "home"
CARDS = HOME / "cards"
TABS = HOME / "tabs"
GP = SRC / "pages" / "gp"
GP_CARDS = GP / "cards"
GP_TABS = GP / "tabs"
REDIRECTS = SRC / "redirects"
ASSETS = ROOT / "src/kellytec-design-system" / "static"

# Public URLs stay stable; source locations are independent of served paths.
PUBLIC_FILES = {
    "assets/hero-bg.jpg": SRC / "assets" / "hero-bg.jpg",
    ".nojekyll": SRC / ".nojekyll",
    "CNAME": SRC / "CNAME",
    "palettes.html": SRC / "palettes.html",
    **{
        f"assets/{name}": ASSETS / name
        for name in (
            "favicon.svg",
            "logo.svg",
            "logo-light.svg",
        )
    },
    **{
        f"assets/scripts/{name}": SRC / "scripts" / name
        for name in (
            "header_scroll.js",
            "reveal_on_scroll.js",
            "page_reveal.js",
            "language.js",
            "cards/card_volatility_surface.js",
        )
    },
}
GENERATED_FILES = (
    "index.html",
    "gp/index.html",
    "gp/monitor/index.html",
    "assets/styles.css",
)

CSS_SOURCES = (
    SRC / "styles" / "tokens.css",
    SRC / "styles" / "base.css",
    SRC / "styles" / "chrome.css",
    SRC / "styles" / "tabs" / "tab_hero.css",
    SRC / "styles" / "tabs" / "tab_strategies.css",
    SRC / "styles" / "tabs" / "tab_team.css",
    SRC / "styles" / "tabs" / "tab_contact.css",
    SRC / "styles" / "pages" / "page_gp.css",
    SRC / "styles" / "effects.css",
)

CARD_FILES = {
    "hero_title": "card_hero_title.html",
    "strategy_statement": "card_strategy_statement.html",
    "volatility_surface": "card_volatility_surface.html",
    "team_heading": "card_team_heading.html",
    "team_member_tianxin_song": "card_team_member_tianxin_song.html",
    "team_member_xinhai_xiong": "card_team_member_xinhai_xiong.html",
    "team_member_peiyu_xiong": "card_team_member_peiyu_xiong.html",
    "office_contact": "card_office_contact.html",
}

TAB_FILES = {
    "hero": "tab_hero.html",
    "strategies": "tab_strategies.html",
    "team": "tab_team.html",
    "contact": "tab_contact.html",
}

GP_CARD_FILES = {
    "intro": "card_intro.html",
    "operations": "card_operations.html",
    "data_availability": "card_data_availability.html",
    "security_note": "card_security_note.html",
}

GP_TAB_FILES = {
    "access": "tab_access.html",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def replace_all(text: str, values: dict[str, str]) -> str:
    result = text
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value.rstrip())
    leftovers = sorted({part.split("}}", 1)[0] for part in result.split("{{")[1:] if "}}" in part})
    if leftovers:
        raise ValueError("Unresolved include(s): " + ", ".join(leftovers))
    return result


def render_document_head(
    *, title: str, description: str, asset_prefix: str, noindex: bool, preload: str = ""
) -> str:
    return replace_all(
        read(CHROME / "document_head.html"),
        {
            "document.title": title,
            "document.description": description,
            "document.robots": (
                '<meta name="robots" content="noindex, nofollow" />' if noindex else ""
            ),
            "document.preload": preload,
            "asset.prefix": asset_prefix,
        },
    )


def render_header(
    *, asset_prefix: str, home_href: str, gp_current: bool, frontend_root: Path = ROOT
) -> str:
    return replace_all(
        read(frontend_root / "src/kellytec-website" / "chrome" / "header.html"),
        {
            "asset.prefix": asset_prefix,
            "navigation.home": home_href,
            "navigation.gp_current": " is-current" if gp_current else "",
        },
    )


def render_home_page() -> str:
    cards = {f"card.{name}": read(CARDS / filename) for name, filename in CARD_FILES.items()}
    tabs = {
        f"tab.{name}": replace_all(read(TABS / filename), cards)
        for name, filename in TAB_FILES.items()
    }
    page_values = {
        "chrome.document_head": render_document_head(
            title="Kelly Technologies",
            description="Kelly Technologies — an investment and technology firm.",
            asset_prefix="",
            noindex=False,
            preload='<link rel="preload" as="image" href="assets/hero-bg.jpg" fetchpriority="high" />',
        ),
        "chrome.header": render_header(asset_prefix="", home_href="#top", gp_current=False),
        "chrome.footer": read(CHROME / "footer.html"),
        **tabs,
    }
    return replace_all(read(HOME / "page.html"), page_values).rstrip() + "\n"


def render_gp_page() -> str:
    cards = {f"card.{name}": read(GP_CARDS / filename) for name, filename in GP_CARD_FILES.items()}
    tabs = {
        f"tab.{name}": replace_all(read(GP_TABS / filename), cards)
        for name, filename in GP_TAB_FILES.items()
    }
    page_values = {
        "chrome.document_head": render_document_head(
            title="GP Login | Kelly Technologies",
            description="Authorized access to Kelly Technologies monitoring systems.",
            asset_prefix="../",
            noindex=True,
        ),
        "chrome.header": render_header(asset_prefix="../", home_href="/", gp_current=True),
        "chrome.footer": read(CHROME / "footer.html"),
        **tabs,
    }
    return replace_all(read(GP / "page.html"), page_values).rstrip() + "\n"


def build_css(frontend_root: Path = ROOT) -> str:
    return (
        "\n\n".join(
            read(frontend_root / path.relative_to(ROOT)).rstrip() for path in CSS_SOURCES
        ).rstrip()
        + "\n"
    )


def build_public_site(destination: Path) -> None:
    """Copy only public assets and rendered pages, never repository directories."""
    destination = destination.resolve()
    if destination == ROOT or destination in ROOT.parents:
        raise ValueError("Site output must be a separate artifact directory")
    if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / "dist"):
        raise ValueError("Site output inside this repository must be under dist/")
    allowed = set(PUBLIC_FILES) | set(GENERATED_FILES)
    if destination.exists():
        unexpected = [
            p
            for p in destination.rglob("*")
            if p.is_file() and p.relative_to(destination).as_posix() not in allowed
        ]
        if unexpected:
            raise ValueError("Site output contains files outside the public allowlist")
    for name in allowed:
        target = destination / name
        if not target.resolve().is_relative_to(destination) or target.is_symlink():
            raise ValueError("Site output must not traverse symbolic links")
        target.parent.mkdir(parents=True, exist_ok=True)
    for name, source in PUBLIC_FILES.items():
        shutil.copyfile(source, destination / name)
    for name, contents in {
        "index.html": render_home_page(),
        "gp/index.html": render_gp_page(),
        "gp/monitor/index.html": read(REDIRECTS / "gp_monitor.html"),
        "assets/styles.css": build_css(),
    }.items():
        (destination / name).write_text(contents, encoding="utf-8", newline="\n")


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
    logo_svg = _read_svg_text(
        frontend_root / "src/kellytec-design-system" / "static" / "logo.svg"
    ).encode("utf-8")
    homepage_href = _frontend_homepage_href(frontend_root)

    source_header = render_header(
        asset_prefix="", home_href="#top", gp_current=False, frontend_root=frontend_root
    )
    footer = read(frontend_root / "src/kellytec-website" / "chrome" / "footer.html")

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
    generated_dir = frontend_root / "src/kellytec-design-system" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    (generated_dir / "frontend_header.html").write_text(chrome.header + "\n", encoding="utf-8")
    (generated_dir / "frontend_footer.html").write_text(chrome.footer + "\n", encoding="utf-8")
    (generated_dir / "frontend_chrome.css").write_text(chrome.css, encoding="utf-8")


def _read_svg_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _frontend_homepage_href(frontend_root: Path) -> str:
    cname = frontend_root / "src/kellytec-website" / "CNAME"
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
    body = body.replace("--font-mono", "--brand-font-mono").replace(
        "--font-sans", "--brand-font-sans"
    )
    return (
        "/* Generated from kellytec-frontend/src/kellytec-website/styles/. Run scripts/sync_frontend_chrome.py. */\n"
        + body
        + "\n"
    )


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
                selected.append(
                    prelude + " {\n" + "\n\n".join(_indent(block) for block in media_blocks) + "\n}"
                )
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
