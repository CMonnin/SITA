# SITA Packaging Plan (UV Workspace)

## Current State

Flat repo, no `pyproject.toml`. Dependencies pinned in `requirements.txt` (Nov 2023-era pins). `runtime.txt` specifies Python 3.10. Runs as a Flask app via `gunicorn app:server` (Procfile), or `python app.py` for dev. Tests are hand-rolled in `test.py` (no pytest). Batch CLI lives in `parser_test.py`.

**Core library:** `SITA_module.py` — `LabelledCompound` class + isotope math. No Flask dependency.
**Web app:** `app.py` + `static/` + `templates/` — thin Flask wrapper around the core.
**Batch CLI:** `file_parser.py` + `parser_test.py` — CLI that uses the core library.
**Tests:** `test.py` — manual runner, tests the core algorithm against published paper values.

---

## Target Structure

UV workspace with two packages:

```
SITA/
  pyproject.toml              # workspace root (virtual, no own code)
  uv.lock                     # committed — single lockfile for entire workspace
  .python-version             # 3.10
  .gitignore
  Procfile
  README.md
  LICENSE

  packages/
    sita-core/
      pyproject.toml           # pure algorithm library
      src/
        sita_core/
          __init__.py          # expose LabelledCompound
          core.py              # LabelledCompound class (from SITA_module.py)
          isotope_data.py      # ISOTOPE_ABUNDANCE_DICT_UNIT_MASS constant
      tests/
        test_core.py           # from test.py, converted to pytest

    sita-web/
      pyproject.toml           # Flask app, depends on sita-core
      src/
        sita_web/
          __init__.py
          app.py               # Flask app factory (from current app.py)
          cli.py               # batch CLI entry point (from file_parser.py)
          static/
            app.js
            style.css
          templates/
            index.html
      tests/
        test_app.py            # Flask API tests
```

### Why workspace, not single package

- `sita-core` is a standalone library. Zero Flask/pandas/openpyxl dependencies. Usable from notebooks, pipelines, other services.
- `sita-web` is a thin HTTP/CLI layer. It depends on `sita-core` and adds Flask + pandas + gunicorn.
- UV workspaces share a single `uv.lock` at the repo root. One `uv sync` installs everything.
- Clean boundary. The core can be published to PyPI independently if desired.

---

## Phase 1: Workspace root

### 1.1 Create root `pyproject.toml`

```toml
[tool.uv.workspace]
members = ["packages/sita-core", "packages/sita-web"]

[tool.uv]
dev-dependencies = ["pytest>=8"]
```

The root is a virtual workspace — it has no `[project]` section and no code of its own. It exists only to tie the members together under one lockfile.

### 1.2 Create `.python-version`

```
3.10
```

### 1.3 Delete `runtime.txt`

Replaced by `.python-version`. Heroku-specific, no longer needed.

---

## Phase 2: `sita-core` package

### 2.1 `packages/sita-core/pyproject.toml`

```toml
[project]
name = "sita-core"
version = "0.1.0"
description = "Natural-abundance correction for GC-MS mass distribution vectors from 13C stable-isotope tracer experiments"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.26",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/sita_core"]
```

Only numpy. The core algorithm has no other runtime dependency. `math`, `itertools`, `re`, `collections`, `logging` are stdlib.

### 2.2 `src/sita_core/isotope_data.py`

Extract `ISOTOPE_ABUNDANCE_DICT_UNIT_MASS` from `SITA_module.py`. Pure data constant, no imports beyond stdlib.

### 2.3 `src/sita_core/core.py`

Move `LabelledCompound` from `SITA_module.py`. Changes required:

1. **Fix import-time logging side effect.** Current code runs `logging.FileHandler("log.log")` at module level. This creates a file in CWD on import — unacceptable for a library. Remove the file handler. Keep a module-level logger but let the application configure handlers/output:
   ```python
   logger = logging.getLogger("sita_core")
   ```
   No handlers added. The application (sita-web) configures logging.

2. **Import the isotope data:**
   ```python
   from sita_core.isotope_data import ISOTOPE_ABUNDANCE_DICT_UNIT_MASS
   ```

3. **Fix `save_to_text == True`** to `save_to_text is True` (linter nit, already works).

### 2.4 `src/sita_core/__init__.py`

```python
from sita_core.core import LabelledCompound

__all__ = ["LabelledCompound"]
```

### 2.5 Tests

Move `test.py` to `packages/sita-core/tests/test_core.py`. Changes:

- Update import: `from sita_core import LabelledCompound`.
- Replace `try/except/raise AssertionError` with `pytest.raises(ValueError)` in three tests.
- Remove the `TESTS` list and `main()` function — pytest discovers tests automatically.

---

## Phase 3: `sita-web` package

### 3.1 `packages/sita-web/pyproject.toml`

```toml
[project]
name = "sita-web"
version = "0.1.0"
description = "Flask web interface and CLI for SITA natural-abundance correction"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
dependencies = [
    "sita-core",
    "flask>=3.0",
    "pandas>=2.1",
    "openpyxl>=3.1",
    "gunicorn>=21.2",
]

[project.scripts]
sita-batch = "sita_web.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/sita_web"]
```

- `openpyxl` is missing from current `requirements.txt` but is required by `pandas.ExcelWriter` for `.xlsx` output.
- `gunicorn` is a runtime dependency here since the Procfile uses it.
- `requests` is in `requirements.txt` but never imported. Dropped.

### 3.2 `src/sita_web/app.py`

Move from current `app.py`. Changes:

1. **App factory pattern:**
   ```python
   from flask import Flask
   from pathlib import Path

   def create_app():
       app = Flask(
           __name__,
           template_folder=str(Path(__file__).parent / "templates"),
           static_folder=str(Path(__file__).parent / "static"),
       )
       # register routes...
       return app
   ```

2. **Update imports:**
   ```python
   from sita_core import LabelledCompound
   ```

3. **Configure logging** for the sita_core logger (add console handler, set level).

### 3.3 `src/sita_web/cli.py`

Merge `file_parser.py` + `parser_test.py`. The batch CLI becomes:

```python
from sita_core import LabelledCompound
# ... pandas/xlsx logic from file_parser.py
def main():
    # argparse for input CSV path, output path
    ...
```

Registered as `sita-batch` console script entry point.

### 3.4 Static and templates

Move `static/` and `templates/` into `src/sita_web/`. No content changes.

### 3.5 Tests

`packages/sita-web/tests/test_app.py` — Flask test client tests for `/api/matrix` and `/api/mdv-star`.

---

## Phase 4: Cleanup and configuration

### 4.1 Update `.gitignore`

Add:
```
# UV
.venv/
```

`uv.lock` is NOT gitignored — it's committed for reproducibility.

Remove Heroku-specific `runtime.txt` entry (file deleted).

### 4.2 Update `Procfile`

```
web: gunicorn "sita_web.app:create_app()"
```

### 4.3 Update `README.md`

```bash
# Install everything
uv sync

# Run tests
uv run pytest

# Run dev server
uv run python -m sita_web.app

# Batch CLI
uv run sita-batch template.csv -o output.xlsx
```

### 4.4 Delete old files

| File | Reason |
|---|---|
| `requirements.txt` | Replaced by `pyproject.toml` dependencies |
| `runtime.txt` | Replaced by `.python-version` |
| `SITA_module.py` | Moved to `packages/sita-core/src/sita_core/core.py` |
| `app.py` | Moved to `packages/sita-web/src/sita_web/app.py` |
| `file_parser.py` | Moved to `packages/sita-web/src/sita_web/cli.py` |
| `parser_test.py` | Merged into `sita_web.cli` |
| `test.py` | Moved to `packages/sita-core/tests/test_core.py` |
| `static/` | Moved to `packages/sita-web/src/sita_web/static/` |
| `templates/` | Moved to `packages/sita-web/src/sita_web/templates/` |

---

## Phase 5: Verification

```bash
uv sync                    # resolve + install all workspace deps
uv run pytest              # all tests pass (core + web)
uv run python -c "from sita_core import LabelledCompound; print('core OK')"
uv run python -m sita_web.app   # dev server starts
uv run sita-batch --help        # CLI works
uv build --package sita-core    # wheel builds
```

- [ ] `uv sync` completes clean
- [ ] `uv run pytest` — all tests pass
- [ ] `sita-core` importable without Flask installed
- [ ] Dev server serves UI
- [ ] Batch CLI produces valid xlsx
- [ ] `uv.lock` committed to git
- [ ] No lingering `SITA_module` / `file_parser` references
- [ ] No `log.log` created at import time

---

## Dependency map

```
sita-core          sita-web
   |                  |
   v                  v
 numpy            sita-core (workspace dep)
                  flask
                  pandas
                  openpyxl
                  gunicorn
```

Shared dev dependency at workspace root: `pytest`.

---

## Execution order

The phases are sequential — each depends on the previous:

1. **Workspace root** — `pyproject.toml`, `.python-version`
2. **sita-core** — must exist before sita-web can depend on it
3. **sita-web** — depends on sita-core
4. **Cleanup** — delete old files, update configs
5. **Verify** — run everything, confirm clean state
