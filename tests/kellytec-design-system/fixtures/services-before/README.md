# Services migration reference

These files are historical test inputs captured before extracting the shared
service table. They are never imported by an application or included in a wheel.
`manifest.json` records the Operations Git revision, original file paths, installed
Design System 1.0.0 bundle hashes and embedded font stylesheet hash. No test rewrites
the reference or its checksums.

The Design System CSS omits its embedded fonts to avoid duplicating binary font
data. The test verifies the exact 1.0.0 font stylesheet hash before using it in both
pages. Operations JavaScript and CSS are the original Git HEAD bytes. The fixture
contains no production data; six service names and synthetic status/time/reason
cases are declared in the test runner.

Run against an installed candidate, with Python 3.12, Playwright and local Chromium:

```sh
python tests/kellytec-design-system/check_service_parity.py \
  --browser-path /path/to/chromium \
  --operations-renderer ../project-algo3-monitors/src/algo3-monitor-operations/present/ui/cards/servers.js \
  --operations-css ../project-algo3-monitors/src/algo3-monitor-operations/present/ui/styles/operations.css \
  --output /tmp/service-parity
```

The browser blocks network access. At 390, 520, 521, 900 and 1440 CSS pixels it
renders the frozen reference and the installed component, and optionally the
Operations consumer, with the same data and container width. Geometry, typography,
colors, border, spacing, alignment, truncation styles and screenshot bytes must
match. Failures retain actual/reference images and computed metrics in the output
directory. Neither browser version nor rasterization is assumed to match another
machine: the independent reference is rendered in the same run as the candidate.
