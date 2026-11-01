# kellytec-design-system

Source is directly in this product directory; there is no `python/` wrapper.
`setup.py` maps it to `kellytec_design_system` and excludes the build entrypoint
and tests from the wheel. `pyproject.toml` is the version source.

`kellytec-design-system` owns the shared presentation used by Data Platform,
Research Platform and Operations. Runtime Python dependencies are standard library only.
The package contains the original Page → Tab → Card → Cell contracts,
renderers, CSS tokens, JavaScript, templates, generated brand and fonts.
There is no application authentication, fetch loop or compute logic here.

Build from the frontend repository:

```sh
python .github/automation/check-and-build-kellytec-design-system/scripts/build_wheel.py
python -m build --wheel src/kellytec-design-system
python -m pip install --no-deps src/kellytec-design-system/dist/kellytec_design_system-1.0.1-py3-none-any.whl
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

`UI.dropdown(root, {label, items, value, searchable, placeholder, disabled,
onChange})` provides one single-select control for searchable and ordinary lists.
Items are `{id, label, disabled?}` with unique string IDs (the empty ID is allowed
for a choice such as All rows). Both modes use the shared select surface and a
26px trigger within compact density. Applications should use this component when
their choices need the same popup style; it uses no native select or datalist.
The label can target `${root.id}-trigger`. Committed state is available through
`controller.value()`, `root.dataset.value`, and the trigger's `value` property.
Search is transient: opening always shows all options, typing never changes the
selected ID, and a changed selection emits one bubbling host `change` event with
`event.detail.value` and calls `onChange(value)` once. Escape, Tab, and clicking
outside close without committing. Arrow keys and Enter select enabled choices.

The returned controller supports `setValue(id, {emit:false})`,
`replace(items, {value?, label?})`, `setDisabled(boolean)`, `close()`, and
`destroy()`. Programmatic values and replacements do not emit by default;
replacement retains a valid selected ID and otherwise clears it. An empty ID
displays its item label when present, or the placeholder when absent. Destroy
the controller when removing its host. Reinitializing the same host disposes its
previous controller. Products own item catalogs, fetching, and domain behavior.
The mandatory installed-wheel pytest run includes real-browser dropdown tests
covering reselection, search isolation, keyboard/disabled behavior, popup/trigger
consistency, long lists, empty IDs, and replacement/lifecycle behavior. Local
runs can set `KELLYTEC_UI_BROWSER_PATH`; CI uses installed Playwright Chromium.

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

The 1.0.1 candidate adds `UI.serviceTable(rows)` for the identical Services / Status /
Updated At / Reason presentation used by Operations and Data Platform. Each row is
`{name, status, tone, updatedAt: {short, full}, reason}`; every value is plain text
and escaped. The caller owns status interpretation, missing-value labels and time
formatting. The renderer does not fetch data or know about jobs, runtimes or factors.
The shared `.monitor-workloads`, `.monitor-workload-section` and
`.monitor-workload-head` classes provide the existing section layout; applications
choose section titles and whether an empty section has content. Applications must
not override the service row typography or column geometry.

`tests/kellytec-design-system/check_service_parity.py` compares the installed
candidate to an immutable, test-only Operations reference at five viewport widths.
It compares computed styles, geometry and rendered PNG bytes in the same browser;
it cannot record or accept a replacement reference. See the fixture README for
provenance and the local command. This candidate must be formally released before
consumer release locks can bind version 1.0.1.

The Check and Build workflow invokes that browser comparison after installing the
built wheel. `services-ui-v1` qualification retains the report and images, binds
them to the source snapshot and wheel SHA-256, and rejects restored qualifications
without this evidence. A normal check never rewrites the historical reference.

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

Interactive tables can opt into `keepHeaders`, `stickyHeader`, `stickyFirst`,
`className` and `scrollClass`. Header descriptors accept `action: {key, label,
active}` and `sort: "asc" | "desc"`; actions remain usable for zero matching rows.
`UI.popover(anchor, content, {label, width, onClose})` portals an interactive surface
to the document body, fits it inside the viewport and dismisses on Escape or
outside pointer interaction. Its `close()` and `reposition()` methods let the
consumer end the lifecycle or adjust after asynchronous content arrives. The
consumer retains all filtering and query semantics.
