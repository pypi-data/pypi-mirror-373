import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


@pytest.fixture()
def sample(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(f"""
            [tool.scripts.simple]
            cmd = 'echo simple'
                                    
            [tool.scripts.shell_true]
            cmd = 'echo hello | more'
            shell = true

            [tool.scripts.shell_false]
            cmd = 'python -c "print(\\"shell false\\")"'
            shell = false

            [tool.scripts.description]
            cmd = 'echo desc'
            description = 'A script with description'

            [tool.scripts.absolute_cwd]
            cmd = 'python -c "import os; print(os.getcwd())"'
            cwd = '{str(tmp_path)}'

            [tool.scripts.relative_cwd]
            cmd = 'python -c "import os; print(os.getcwd())"'
            cwd = 'subdir'

            [tool.scripts.without_cwd]
            cmd = 'python -c "import os; print(os.getcwd())"'

            [tool.scripts.env]
            cmd = 'python -c "import os; print(os.environ.get(\\"TOOL_SCRIPTS_ENV\\", \\"?\\"))"'
            env = {{ TOOL_SCRIPTS_ENV = 'yes' }}

            [tool.scripts.complete]
            cmd = 'python -c "import os; print(\\"cwd=\\" + os.getcwd())" | more'
            cwd = 'subdir'
            description = 'A complete script'
            env = {{ TOOL_SCRIPTS_ENV = 'complete' }}
            shell = true
            """),
        encoding="utf-8",
    )

    return tmp_path


def run_cli(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pyproject_scripts.cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_simple(sample: Path):
    result = run_cli(sample, "simple")
    assert result.returncode == 0
    assert result.stdout.strip() == "simple"
    assert result.stderr == ""


def test_shell_true(sample: Path):
    result = run_cli(sample, "shell_true")
    assert result.returncode == 0
    assert result.stdout.strip() == "hello"
    assert result.stderr == ""


def test_shell_false(sample: Path):
    result = run_cli(sample, "shell_false")
    assert result.returncode == 0
    assert result.stdout.strip() == "shell false"
    assert result.stderr == ""


def test_description(sample: Path):
    result = run_cli(sample, "--help")
    assert result.returncode == 0
    assert "A script with description" in result.stdout
    assert result.stderr == ""


def test_absolute_cwd(sample: Path):
    result = run_cli(sample, "absolute_cwd")
    assert result.returncode == 0
    assert result.stdout.strip() == str(sample)
    assert result.stderr == ""


def test_relative_cwd(sample: Path):
    (sample / "subdir").mkdir()
    result = run_cli(sample, "relative_cwd")
    assert result.returncode == 0
    assert result.stdout.strip() == str(sample / "subdir")
    assert result.stderr == ""


def test_without_cwd(sample: Path):
    result = run_cli(sample, "without_cwd")
    assert result.returncode == 0
    assert result.stdout.strip() == str(sample)
    assert result.stderr == ""


def test_env(sample: Path):
    result = run_cli(sample, "env")
    assert result.returncode == 0
    assert result.stdout.strip() == "yes"
    assert result.stderr == ""


def test_complete(sample: Path):
    (sample / "subdir").mkdir()
    result = run_cli(sample, "complete")
    assert result.returncode == 0
    assert result.stdout.strip() == f"cwd={sample / 'subdir'}"
    assert result.stderr == ""


def test_no_script_arg(sample: Path):
    result = run_cli(sample)
    assert result.returncode == 0
    assert "usage: pps [-h] <script> ..." in result.stdout
    assert result.stderr == ""


def test_unknown_script_arg(sample: Path):
    result = run_cli(sample, "unknown")
    assert result.returncode == 2
    assert "usage: pps [-h] <script> ..." in result.stderr


def test_no_scripts_section(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent("""
            [tool]
            key = "value"
            """),
        encoding="utf-8",
    )
    result = run_cli(tmp_path, "any")
    assert result.returncode == 1
    assert result.stderr.strip() == "error: [tool.scripts] section not found"


def test_no_scripts_defined(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent("""
            [tool.scripts]
            key = "value"
            """),
        encoding="utf-8",
    )
    result = run_cli(tmp_path)
    assert result.returncode == 1
    assert result.stderr.strip() == "error: Script 'key' is not a table"


def test_missing_cmd(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent("""
            [tool.scripts.no_cmd]
            description = 'This script has no cmd and cannot be run'
            """),
        encoding="utf-8",
    )
    result = run_cli(tmp_path, "no_cmd")
    assert result.returncode == 1
    assert (
        result.stderr.strip() == "error: Script 'no_cmd' missing required 'cmd' field"
    )


def test_empty_cmd(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent("""
            [tool.scripts.empty_cmd]
            cmd = '   '
            """),
        encoding="utf-8",
    )
    result = run_cli(tmp_path, "empty_cmd")
    assert result.returncode == 1
    assert result.stderr.strip() == "error: Script 'empty_cmd' has empty 'cmd' value"


def test_no_pyproject(tmp_path: Path):
    result = run_cli(tmp_path, "any")
    assert result.returncode == 1
    assert (
        result.stderr.strip()
        == "error: No pyproject.toml found in current or parent directories"
    )
