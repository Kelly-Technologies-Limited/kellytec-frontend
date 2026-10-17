## 2026-10-17 - Checkpoint product src layout

- Move Design System and Website products under src/; update packaging, asset discovery, tests and workflow build paths.
- Verify local packages and a clean Design System wheel build. This checkpoint does not publish packages or deploy the website.

## 2026-10-16 - Version shared dependencies and adopt upgrades through PRs

- Adopt a committed Automation wheel lock and PR-based shared-dependency updates; verify release identity before preparing allowlisted files, preserve human commits, and keep PR checks separate from main operations. Version Design System at 1.0.0; publish the qualified wheel before notifying direct consumers.
- Local implementation only: initial real release locks, remote provisioning and production cutover require the documented first-release sequence. No package publication or deployment performed in this change.

## 2026-10-14 - Implement product Workflows and repository rename preparation

- Separate website Check/Pages Deploy from Design System Check and Build. Store Workflow entries in .github/automation and share actual brand inputs explicitly.
- Consume Design System by qualified source identity instead of a manually released version. Notify only direct product consumers; preserve immutable wheel/site artifacts and reuse them on retries.
- Align product directories and package mapping with hyphenated product names; keep Python import names valid.
- Local implementation and checks only; GitHub repository renames, remote qualification, IAM changes and deployments have not been performed.

## 2026-10-12 - Research composition primitives, candidate 0.3.0

## 2026-10-13 - Use shared test profiles and grouped automation

- Define repository test selections once in tests/profiles.toml and use the shared automation reader from local and Workflow entrypoints, preserving existing test arguments, exclusions and time budgets.
- Adopt automation modules grouped by function; remove old imports and duplicate deployment test configuration without compatibility aliases. Preserve repository-owned build, environment preparation and deployment admission.

## 2026-10-13 - Unify repository structure

- Unify root navigation for product source, installation, tests, release/deployment and documentation.

## 2026-10-13 - Organize tests by product ownership

- Consolidate existing tests under the repository root `tests/`, using canonical product names and engineering `workloads/`; update paths, imports and existing workflow selections without changing test assertions or product behavior.
- Product rendering behavior lives under its product; distribution contents, resources and package boundaries live under workloads/build/kellytec-design-system. The build workflow selects all three existing test groups.
- Use canonical product names in current documentation and release display; retain technical identifiers and immutable historical evidence.

- Add opt-in 26px control density, inset cell surfaces and semantic progress tones in new primitive stylesheets; existing Monitor style files and default navigation sizes are unchanged.
- Add disabled blank tab slots while retaining Monitor's existing tab defaults.
- Provide shared searchable checkbox selection, compact strategy choices, card status, date ranges and progress styling. Preserve keyboard focus and scroll position during selection.
- Verify the installed distribution with the existing 54 design-system tests; no website or cloud publication is included.

## 2026-10-12 - Publish design system 0.2.0 for coordinated consumers

- Verify private publication through Cloud Build `41da59c7-086d-4c31-9ca2-6d91185d5233`; published wheel SHA-256 is `de3bdf40dfa5f2a6d9d196c620f97b6febfd333c5daf3c7b8db7b1c90f4ca958`.
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

## 2026-10-13 - Clarify the test profile contract

- Update the earlier test-layout note to reflect the approved shared profiles while retaining the no-new-CLI and unchanged-product-behavior boundaries.

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

## 2026-10-14 Automation behavior modules

- Migrate workflow imports to the shared Check, Build, Publish, Release, Push and Deployment modules; declare product dependencies, Registry selections and operation configuration explicitly. Preserve qualified source/artifact identities and existing recovery and deployment gates.
