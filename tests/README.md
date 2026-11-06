# Tests

## Shared test profiles

[`profiles.toml`](profiles.toml) owns the selections below. Workflow and local execution
use `kellytec_automation.qualification.checks.profiles.run_profile`; there is no legacy JSON fallback.
Run from the repository root after preparing the existing product dependencies,
installed Engine wheel, immutable test-source checkout and required fixtures.
The profile does not install dependencies, upload code or deploy resources.

| Profile | Ordered suites |
| --- | --- |
| `build-artifacts` | `frontend` |

Use the qualified Automation source SHA from the product run snapshot at
`.automation/<product>/snapshot.json`. Install that checkout from
`.automation-tools/kellytec-automation/`; Platforms tests its candidate source.
Installed Engine wheels and immutable Engine test checkouts remain separate inputs.
For example, with that environment prepared:

```sh
python -c "from pathlib import Path; from kellytec_automation.qualification.checks.profiles import run_profile; run_profile(Path.cwd(), 'build-artifacts')"
```

Consumer deployment entrypoints still prepare and verify the installed artifact and private
test-source identity before invoking the profile. Local standalone invocation requires the
same preparation; it does not certify a deployment. Real Lean requires Docker and the
existing locked data. Manual measurements remain explicit; no new default performance gate
is introduced. The detailed test boundaries and manual commands below continue to apply.

## Product ownership after the 2026-10-13 refactor

This repository has one test entry directory: `tests/`. Products: kellytec-design-system, kellytec-website.
`workloads/` owns build, setup, deployment and testing-tool verification where those
checks already exist. Product `fixtures/` contains test materials and fixed
expectations; `_support/` contains construction, loading and comparison code.
Use the names **sample data** and **simulated data** for data assets.

Product rendering behavior lives under its product; distribution contents, resources and package boundaries live under workloads/build/kellytec-design-system. The build workflow selects all three existing test groups.

## Design System browser prerequisites

The `frontend` suite includes mandatory real-browser dropdown tests. Prepare an
isolated Python 3.12 environment with the built Design System wheel and the
accepted Automation package and its dependencies before running the profile.
Install the test tools and the browser used by the Design System build workflow:

```sh
python -m pip install pytest==9.0.2 playwright==1.64.1
python -m playwright install --with-deps chromium
python -m pytest -q tests/kellytec-design-system tests/workloads/build
```

For an explicit local Chrome run, set `KELLYTEC_UI_BROWSER_PATH` to its executable
path before the pytest command. The browser version must be recorded with local
evidence. Missing Playwright or Chromium fails these tests; they are not skipped.
The tests exercise the installed wheel through clicks, search, keyboard input,
and reselection, with browser network requests blocked. The separate Services
parity check and its immutable reference are described in
[`fixtures/services-before/README.md`](kellytec-design-system/fixtures/services-before/README.md).
The website-only check selects `tests/kellytec-website` and does not require this
browser setup.

This refactor retains existing assertions, test inputs, parametrization, fixture
lifetimes, skips and runtime boundaries. Shared profiles now centralize selection;
there is no new CLI or product behavior. Run the same repository-owned checks as its workflow
before committing; a collected suite is not evidence of a passing execution.
