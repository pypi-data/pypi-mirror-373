<div align="center">

# pyproject-scripts (`pps`)

Tiny, dependency‑free project‑local script runner for Python projects: declare scripts in `pyproject.toml` under `[tool.scripts.*]`, get instant `pps <name>` subcommands.

</div>

---
## Installation

```bash
# Install from PyPI
pip install pyproject-scripts

# editable / dev inside a cloned repo
pip install -e .
# or with uv
uv pip install -e .
```

---
## Defining Scripts

Define scripts in `pyproject.toml` under the `[tool.scripts]` table according to this schema:

```toml
[tool.scripts.<your-script-name>]
cmd = "<your command here>"
description = "<short description>"
cwd = "<optional working directory>"
env = { "<VAR>" = "<value>", ... }
shell = true | false
```

The meaning of each field is as follows:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `cmd` | Yes | string | Command to execute (interpreted by shell unless `shell=false`). |
| `description` | No | string | Short human description shown in help listing. |
| `cwd` | No | string | Working directory (relative to discovered project root) or absolute path. |
| `env` | No | table  | Extra environment vars (stringified) layered over current env. |
| `shell` | No | bool | `true`/omitted: run via shell. `false`: tokenize with `shlex.split` and exec directly. |

---
## Usage Examples

Here's an example `pyproject.toml` snippet defining two scripts, `lint` and `test`:

```toml
[tool.scripts.lint]
cmd = "ruff check . && ruff format --check ."
description = "Run ruff linter"
cwd = "src"
env = { "RUST_LOG" = "info" }
shell = true

[tool.scripts.test]
cmd = "pytest -q"
description = "Run test suite"
shell = false
```

To run the `lint` script, simply execute:

```bash
pps lint
```

Additional arguments can be passed, for example to run a specific test file. Every
argument after the script name is forwarded to the command:

```bash
pps test tests/test_special_case.py
```

---
## Supported Python Versions

Tested on CPython >= 3.11. Older versions are not targeted because `tomllib`, used for parsing `pyproject.toml`, is only in the standard library since 3.11.

---
## License

AGPL-3.0-or-later. See `LICENSE` for full text.
