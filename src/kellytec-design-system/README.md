# kellytec-design-system

Source is directly in this product directory; there is no `python/` wrapper.
`setup.py` maps it to `kellytec_design_system` and excludes the build entrypoint
and tests from the wheel. `version.py` is the single version source.

`kellytec-design-system==0.2.0` owns the Monitor presentation used by both Monitor apps
and kellytec-research-platform. Runtime Python dependencies are standard library only.
The package contains the original Page → Tab → Card → Cell contracts,
renderers, CSS tokens, JavaScript, templates, generated brand and fonts.
There is no application authentication, fetch loop or compute logic here.

Build from the frontend repository:

```sh
python .github/automation/check-and-build-kellytec-design-system/scripts/build_wheel.py
python -m build --wheel kellytec-design-system
python -m pip install --no-deps kellytec-design-system/dist/kellytec_design_system-0.2.0-py3-none-any.whl
python -m pytest -q tests/kellytec-design-system tests/kellytec-website
```

Publish the reviewed, immutable wheel through the existing approved Python
package repository before releasing Monitor. Monitor's two pinned requirements
files feed its existing dependency download, vendor and offline Docker install
steps. kellytec-research-platform bundles the same wheel. Consumers never read a sibling checkout.
Do not reuse a version for changed release bytes.

Use `kellytec_design_system.assets.ROOT` for installed favicon/static resources, and
`design_system_css()` / `shared_ui_script()` for the canonical bundles.
Use `data-ui="button"` for application actions outside the toolbar; it selects
the same base and hover styles as Monitor toolbar buttons, with the shared
native disabled and keyboard-focus behavior.

Optional extensions preserve these defaults. Put data-ui-density="compact" on a
container to make buttons, text inputs, selects and selection rows exactly 26px
high; navigation tabs retain their existing size. The inset cell surface is
enabled by data-ui-surface="inset" on a canonical cell. Progress controls can
select healthy, critical or unknown through data-tone. Applications map their
domain states to these tones and use the existing statusBadge for status bubbles.

`MonitorPage.toolbar_actions_html=None` retains Monitor's existing status and
Refresh controls; a trusted application HTML string replaces only those actions.
`updated_initial` is escaped and can contain the current account/project text.
`toolbar_aria_label` supplies its accessible label.

`render_login` keeps the password form by default. Optional `instruction`,
`form_html`, `scripts_html`, and `brand_logo=True` allow browser authorization
without putting provider behavior inside shared UI. Apps must escape user values
in trusted HTML slots; labels passed as plain text are escaped by the renderer.

Fonts are downloaded production resources, not extracted from a test HAR.
Their original URLs, SHA-256 values and OFL licenses are in `static/fonts`.
IBM Plex Sans 400/500/600/700, Mono 400/500/600, and Playfair Display 400–700
are bundled; Noto Serif SC includes the existing Chinese copyright glyphs.
The logo is an SVG outline. English tool interfaces require no external fonts.
`font_stylesheet()` embeds these resources so applications need no font route
and can run offline. Other CJK text would require an explicit font subset update.

Canonical logos and imagery live in `src/kellytec-design-system/static/`. Brand generation reads
that directory and the website's `src/kellytec-website/chrome/` and `src/kellytec-website/styles/` directly;
it does not require generated website output. Generated package resources
remain bundled in the wheel, so consumers need no sibling asset directory.

Website output is built independently by `.github/automation/check-kellytec-website/scripts/build_website.py` into `dist/site/`.
The allowlist excludes Python, tests, wheel and build tooling. The GitHub Actions
workflow builds and tests both artifacts, then deploys only the public website on
pushes to `main`. Pull requests never deploy. Pages uses GitHub Actions publishing,
not the branch root. The separate wheel artifact still needs publication through
the approved Python package repository before a consumer release; a website
deployment does not update Monitor or kellytec-research-platform.

Version 0.1.2 adds explicit percentage precision. Percentage descriptors may
opt into `fraction_digits` (integer 0–20); both minimum and maximum fraction
digits then use that value. Omitting it preserves the existing 0–1 digit format.
Shared card grids also clear bottom
margins on cards directly inside grid slots, matching direct-child cards.

Version 0.1.3 extends `fraction_digits` to `decimal`, `quantity`,
`price`, `money`, `ratio`, and `duration_seconds`. Existing omitted-precision
defaults are unchanged. `ratio` appends × and `duration_seconds` always uses
seconds (both default to two decimals); rounded negative zero is displayed as
zero. Currency remains mandatory for money, and missing values remain `—`.

`UI.table` accepts either existing string headings or `{label, numeric: true}`
metadata. Numeric columns align right with tabular digits and fixed-unit values;
`UI.labelValues([{label, value: DisplayValue}, ...])` aligns multiple measurements
in one cell. Applications still own the row contents and their semantic units.
The optional fourth argument `{equalColumns: true}` uses equal-width columns
without a scroll-forcing minimum width, permits heading wraps, and preserves
numeric alignment. Existing callers retain their automatic column sizing.
The same options accept `headerType: 'table-header-record'` to match the 11px
Order/Position record headers. Heading metadata may provide `lines`, such as
`{label: 'Win Rate', lines: ['Win', 'Rate'], numeric: true}`, for explicit line
breaks. Each line is escaped and can wrap further when its column is narrow.

`UI.chartSeriesStyle(key, catalog)` assigns styles to opaque keys without a
business registry. Existing keys retain their style for the browser session;
new keys append. Shared categorical colors combine with stripe patterns after
the first four categories. Use the same descriptor with `chartSeriesFill`,
`chartSeriesDefinitions`, and `chartLegendItem({series, label})`. SVG definition
namespaces must be unique for each mounted chart. Card bindings continue to own
chart-text scaling and accessible tooltip cleanup.

Dynamic series start with the website brand purple (`--palette-brand-accent`,
available in the shared palette without the website chrome) and the existing
chart blue, followed by chart green and amber. They have separate `series-*`
roles, so the existing `categorical-*` roles used by other chart semantics keep
their colors.

`UI.bindResponsiveChart(root, selector, draw)` observes plot containers and calls
`draw(width)` with their actual pixel width. The returned SVG markup replaces
only the plot host. Shared card bindings refresh text and keyboard tooltips
after redraws. A renderer's `bind` may return a cleanup function; `bindCard`
disposes it before rebinding or removing that card. Hidden plots wait until
they have a positive width.
