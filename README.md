# kellytec-frontend

## Repository navigation

| Entry | Location or responsibility |
| --- | --- |
| Repository responsibility | Public website and shared presentation package. |
| Products and source | [Design system](src/kellytec-design-system/); [Website](src/kellytec-website/) |
| Installation | [Package setup](src/kellytec-design-system/README.md) |
| Tests | [Tests](tests/README.md) |
| Deployment and release | [Build and Pages workflow](.github/workflows/build-artifacts.yml) |
| Documentation | [Design system reference](src/kellytec-design-system/README.md) |

Directories are created only when needed. Source layouts retain their existing package and platform contracts.

Owns **kellytec-website**, the static website for **Kelly Technologies Limited**
(`kellytec.io`), and **kellytec-design-system**, the installable presentation package.

The [kellytec-design-system](src/kellytec-design-system/README.md) package is used
by Monitor and kellytec-research-platform. Build its wheel independently of the public
website. `python .github/automation/check-kellytec-website/scripts/build_website.py` produces `dist/site` from an
explicit public-file allowlist. On every push to `main`,
`.github/workflows/build-artifacts.yml` builds and tests the website and shared
UI wheel, then deploys only the `dist/site` artifact to GitHub Pages at
`https://kellytec.io/`. Pull requests build and test without deploying;
`workflow_dispatch` on `main` can repeat the build and deployment.

The repository's Pages publishing source is **GitHub Actions**, not a branch
directory. Source/package files are excluded from the public website artifact.
The published 0.2.0 release renames the package and keeps the existing display contracts;
see [its contract](src/kellytec-design-system/README.md).

The shared UI wheel is uploaded as a separate Actions artifact; deploying the
website does not publish that wheel to a Python package repository or update
Monitor or kellytec-research-platform automatically.

The served site is still plain HTML/CSS/JS on GitHub Pages. The editable
website source and exclusive imagery live under `src/kellytec-website/`, shared brand
assets under `src/kellytec-design-system/static/`, and
generated pages and runtime assets under `dist/site/` only.

## Mental model

The frontend follows the same presentation model as Monitor:

```text
page -> tab -> card -> cell
```

- **page**: one complete page. Current pages: `home` and `gp-login`.
- **tab**: one top-level area inside a page. On this public site a tab is a
  page section, not necessarily a visible tab control.
- **card**: one content or visual block inside a tab.
- **cell**: the smallest displayed value inside a card.

Current source mapping:

```text
home page
  hero tab
    hero_title card
      headline cell

  strategies tab
    strategy_statement card
      eyebrow cell
      title cell
    volatility_surface card
      surface cell

  team tab
    team_heading card
      eyebrow cell
    team_member_tianxin_song card
      initials, name, role, bio cells
    team_member_xinhai_xiong card
      initials, name, role, bio cells
    team_member_peiyu_xiong card
      initials, name, role, bio cells

  contact tab
    office_contact card
      eyebrow, address, email cells

gp-login page
  access tab
    intro card
      eyebrow, title, description cells
    operations card
      index, access, title, description, action cells
    data_availability card
      index, access, title, description, action cells
    security_note card
      mark, notice, return cells
```

Cells stay inside card files until a cell type earns its own deeper Module.
Do not add placeholder pages, tabs, cards, or cells for content that does not
exist yet.

## Stack

- Pure HTML / CSS / JS
- No framework and no browser-side fragment loading
- A tiny standard-library Python build script
- Google Fonts: Playfair Display and Noto Serif SC
- Hosted on GitHub Pages at `kellytec.io` via `CNAME`

## Build

Edit website source under `src/kellytec-website/` or shared images under `src/kellytec-design-system/static/`, then
build and preview the served files:

```bash
cd kellytec-frontend
python .github/automation/check-kellytec-website/scripts/build_website.py
python -m http.server --directory dist/site
```

The build writes these pages and stylesheet, and copies only explicitly listed
public assets into `dist/site/`:

- `dist/site/index.html`
- `dist/site/gp/index.html`
- `dist/site/gp/monitor/index.html`
- `dist/site/assets/styles.css`

Build artifacts are ignored by Git. There is no root `gp/` directory: GP Login
is a useful public launchpad for the protected ALGO3 Operations and Data
Availability monitors, with source in `src/kellytec-website/pages/gp/`. Its public URL remains
`/gp/`; `/gp/monitor/` still redirects there. The source directory layout does
not change public URLs.

Website behavior lives in `src/kellytec-website/scripts/` and is copied to the served
`assets/scripts/` URLs. Shared images are copied from `src/kellytec-design-system/static/` to served
`assets/` URLs. The generated stylesheet comes from `src/kellytec-website/styles/`.

## Project structure

```text
kellytec-website/palettes.html # palette study / retheming playground
.github/automation/check-kellytec-website/scripts/build_website.py       # builds allowlisted public artifact in dist/site/
.github/automation/check-and-build-kellytec-design-system/scripts/build_wheel.py # generates UI brand resources from source
kellytec-website/chrome/                 # document head, header, footer
kellytec-website/pages/home/page.html    # home page shell and tab order
kellytec-website/pages/home/tabs/        # current tab_*.html sections
kellytec-website/pages/home/cards/       # current card_*.html files with data-cell annotations
kellytec-website/pages/gp/               # GP Login page, tab, and card source
kellytec-website/redirects/              # legacy redirect source
kellytec-website/styles/                 # split CSS source
kellytec-website/scripts/                # website runtime behavior
kellytec-website/assets/                # website-only imagery
kellytec-design-system/static/          # canonical logos, favicon and UI resources
kellytec-design-system/                  # installable Monitor / kellytec-research-platform UI package
dist/site/                  # generated public website; ignored by Git
kellytec-website/CNAME
kellytec-website/.nojekyll
```

## Editing rules

- Edit source fragments and shared assets, not generated files under `dist/`.
- Generate UI brand resources directly from `src/kellytec-website/chrome/`, `src/kellytec-website/styles/`, and
  `src/kellytec-design-system/static/` with `python .github/automation/check-and-build-kellytec-design-system/scripts/build_wheel.py`; no website
  build is needed. The wheel carries those resources for installed consumers.
- Keep `site-header` and `site-footer` shapes stable unless you also check
  Monitor chrome extraction.
- Preserve the existing CSS classes and ids when refactoring. The `data-page`,
  `data-tab`, `data-card`, and `data-cell` attributes are the semantic editing
  Interface.
- Keep public behavior static-first. Do not add a framework or runtime HTML
  loader unless the site grows enough to justify a new architecture decision.

## Brand notes

The current brand palette is near-white canvas (`#FCFCFC`) over deep cool
charcoal ink (`#373545`), with muted lavender-gray accents:

- Accent 1: `#7F7B9A`
- Accent 2: `#67647E`
- Accent 3: `#4F4C61`

`palettes.html` remains the live palette study for future retheming.
