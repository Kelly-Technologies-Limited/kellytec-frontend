# Tests

## Product ownership after the 2026-10-13 refactor

This repository has one test entry directory: `tests/`. Products: kellytec-design-system, kellytec-website.
`workloads/` owns build, setup, deployment and testing-tool verification where those
checks already exist. Product `fixtures/` contains test materials and fixed
expectations; `_support/` contains construction, loading and comparison code.
Use the names **sample data** and **simulated data** for data assets.

Product rendering behavior lives under its product; distribution contents, resources and package boundaries live under workloads/build/kellytec-design-system. The build workflow selects all three existing test groups.

This refactor retains existing assertions, test inputs, parametrization, fixture
lifetimes, skips and runtime boundaries. It introduces no CLI, test profiles or
additional product behavior. Run the same repository-owned checks as its workflow
before committing; a collected suite is not evidence of a passing execution.
