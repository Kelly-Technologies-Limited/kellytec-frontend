# kellytec-website

Public website product in `kellytec-frontend`. Edit the page, chrome, style and
browser-script sources here. Website-only imagery lives in `assets/`; shared
logos and favicon belong to `kellytec-design-system/static/`.

From the repository root, run `python -B scripts/build_site.py` and preview with
`python -m http.server --directory dist/site`. The public allowlist preserves
existing URLs and excludes source, tests and Python packages.

Run `python -B -m pytest kellytec-website/tests`. See the repository README for
the separate design-system build and chrome generation workflow.
