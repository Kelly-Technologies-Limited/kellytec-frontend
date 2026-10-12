## 2026-10-12 - Publish design system 0.2.0 for coordinated consumers

- Publish the renamed `kellytec-design-system==0.2.0` private package required by the current Monitor and Research Platform compositions.
- Build the wheel and source distribution from the canonical product and pass all 56 website/design-system tests before publishing. Keep the public website's existing file allowlist and display contracts.

## 2026-10-11 — Canonical repository names

## 2026-10-12 - Standardize frontend product identities

- Move the website to `kellytec-website` and the presentation package to flat
  `kellytec-design-system`; map the latter to `kellytec_design_system` 0.2.0.
- Give package versioning one source and keep build tooling/tests outside the
  wheel. Preserve chrome generation and the public asset allowlist.
- Update CI, documentation and resource owners. Local qualification: 56 tests
  pass; all 16 public website files match the pre-refactor bytes. This is an
  unpublished candidate; the website and package have not been deployed.

- Update shared UI generated-source attribution to kellytec-frontend. Preserve the kellytec.io domain, asset URLs and kellytec-ui distribution identity.

## 2026-10-09 — Shared UI 0.1.3 release

- Support explicit heading lines and the existing record-header typography in shared tables.
- Add opt-in equal-width tables with wrapping headings and responsive plot binding with renderer cleanup. Separate brand-purple/chart-blue dynamic series from existing categorical roles.

- Add explicit ratio and fixed-second display values and opt-in precision for money, prices, quantities and decimals, preserving existing defaults.
- Add shared numeric table alignment, label/value rows and dynamic category colors/patterns for an arbitrary observed catalog.
- Release the immutable 0.1.3 package for Monitor's four independent archive-statistics cards, preserving existing consumer defaults. Validate shared UI and website tests and compare the formal wheel payload with the qualified 0.1.3.dev4 candidate before publication.

## 2026-10-08 — Shared UI 0.1.2 release

- Add optional `fraction_digits` for percentage descriptors (integer 0–20), preserving existing formatting for callers that omit it.
- Make cards inside direct grid slots share the grid's spacing, without changing slots outside grids.
- Build/install the 0.1.2 wheel locally; 18 frontend/shared UI tests and 1136 Monitor consumer tests pass. Validate 15 cross-tab and 36 Order/Position browser cases. Publish the validated immutable wheel to the existing Python Artifact Registry before downstream Monitor builds.

## 2026-10-07 — Shared UI 0.1.1 release

- Release the opt-in New York EDT/EST time labels as an immutable kellytec-ui 0.1.1 wheel for Monitor, preserving default ET labels for existing callers.
- Validate the shared UI and website tests before publishing and coordinate downstream package pins.

## 2026-10-07 — Explicit New York DST labels

- Add `show_timezone` to shared NY date/time display values. Opted-in instant labels distinguish EST and EDT; existing callers retain ET and naive business times remain unshifted.
- Monitor Operations opts in at its display boundary; Data Availability defaults are unchanged.

# Changelog

## 2026-09-27

- Normalize bundled font license whitespace and line endings, retain original source checksums, and verify packaged checksums consistently on Windows and Linux.
- Move canonical images/logo/favicon to `shared/assets` and website JavaScript to `src/scripts`. Build the public website only into `dist/site`, removing root generated pages and `gp/` while preserving public URLs. Generate shared UI brand resources directly from source, without a prior website build.
- Package the existing Monitor presentation as `kellytec-ui==0.1.0` under `shared/ui`, preserving Page/Tab/Card/Cell and adding optional application toolbar/login content. Include generated brand resources and licensed offline fonts.
- Switch GitHub Pages from branch-root publishing to the tested `dist/site` artifact. Pushes to `main` automatically build, test and deploy to `kellytec.io`; pull requests only build and test. Preserve the custom domain and keep the shared UI wheel in a separate artifact, outside the public website.

## 2026-09-02

- Replaced both GP card Unicode arrow characters with deterministic inline SVG
  paths so mobile platforms cannot substitute emoji glyphs. Centered the
  security-note mark on the first mobile text line; the 430px Chrome regression
  measures a 0.04px center delta with zero horizontal overflow.
- Reframed both GP system cards as two-line product hierarchies: English uses
  `ALGO3 Monitor / Operations` and `ALGO3 Monitor / Data Availability`, while
  Chinese uses `ALGO3 监控台 / 运营` and `ALGO3 监控台 / 数据可用性`.

## 2026-09-01

- Standardized the GP landing browser-tab title in English regardless of the
  selected page language.
- Aligned both monitor-card titles with the GP Login serif weight and tracking.
- Corrected the public access navigation so the language switch renders
  `GP / LP` in English and `管理人 / 投资人` in Chinese.
- Compacted the GP landing page to fit standard desktop viewports without
  vertical scrolling while retaining responsive narrow-screen behavior.
- Moved the legacy GP redirect source under `src/redirects/`; root `gp/`
  remains generated output required by branch-based GitHub Pages.
- Replaced the public Monitor header action with the bilingual GP access link.
- Added a bilingual `/gp/` launchpad for the protected ALGO3 Operations and
  Data Availability monitors.
- Preserved `/gp/monitor/` as a redirect to the new launchpad and marked the
  launchpad `noindex, nofollow`.
- Extended the static build around the existing page → tab → card → cell
  presentation model so both public pages share the same chrome and assets.
