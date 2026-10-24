# Suburb Fit source

- `artifact.html`: the main app as published on Claude (uses `window.claude` for storage, downloads and user).
- `standalone/build.py`: makes the public `index.html` (inlines jsPDF and qrcodejs, adds a localStorage shim for `window.claude`).
- `data/vg.py`: SA Valuer-General house medians (latest release). `data/gen.py` writes `suburbs.js`, which replaces the `const SUBURBS = [...]` line in the app.
- `tests/`: sample bank statements plus a Playwright regression test (`run_test.py`).

Paths in the scripts point at the original working folders, so adjust them before re-running.
