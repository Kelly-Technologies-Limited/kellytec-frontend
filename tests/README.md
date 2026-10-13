# Tests

## Shared test profiles

[`profiles.toml`](profiles.toml) owns the selections below. Workflow and local execution
use `kellytec_automation.testing.profiles.run_profile`; there is no legacy JSON fallback.
Run from the repository root after preparing the existing product dependencies,
installed Engine wheel, immutable test-source checkout and required fixtures.
The profile does not install dependencies, upload code or deploy resources.

| Profile | Ordered suites |
| --- | --- |
| `build-artifacts` | `frontend` |

Use the exact Platforms `tool_sha` from `.github/deploy/config.json`,
`.github/release/config.json` or `.github/test-tools.json`, whichever this repository owns.
Research uses the existing Registry `tools_sha`; Platforms uses this checkout.
Expose that checkout on `PYTHONPATH` (the Workflow uses `.automation-tools/`).
For example, with that environment prepared:

```sh
python -c "from pathlib import Path; from kellytec_automation.testing.profiles import run_profile; run_profile(Path.cwd(), 'build-artifacts')"
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

This refactor retains existing assertions, test inputs, parametrization, fixture
lifetimes, skips and runtime boundaries. Shared profiles now centralize selection;
there is no new CLI or product behavior. Run the same repository-owned checks as its workflow
before committing; a collected suite is not evidence of a passing execution.
