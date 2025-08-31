import argparse
import os
import shlex
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

all = [
    "Script",
    "load_scripts",
    "discover_pyproject",
]


@dataclass
class Script:
    # Raw table from pyproject.toml
    raw: dict

    # Processed fields
    cmd: str
    cwd: Path
    description: str
    env: dict[str, str]
    name: str
    shell: bool

    def run(self, project_root: Path, extra_args: list[str]) -> int:
        if self.cwd.is_absolute():
            cwd = self.cwd
        else:
            cwd = project_root / self.cwd

        env = os.environ.copy()
        if self.env:
            env.update(self.env)

        if self.shell:
            quoted_args = " ".join(shlex.quote(a) for a in extra_args)
            proc = subprocess.run(
                f"{self.cmd} {quoted_args}", shell=True, cwd=cwd, env=env
            )
        else:
            cmd_with_args = shlex.split(self.cmd) + extra_args
            proc = subprocess.run(cmd_with_args, shell=False, cwd=cwd, env=env)

        return proc.returncode


def discover_pyproject(start: Path | str = ".") -> Path:
    path = Path(start).resolve()
    for parent in [path, *path.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    raise RuntimeError("No pyproject.toml found in current or parent directories")


def load_scripts(pyproject_path: Path | str) -> Dict[str, Script]:
    py_path = Path(pyproject_path)
    data = tomllib.loads(py_path.read_text(encoding="utf-8"))

    scripts_section = data.get("tool", {}).get("scripts")
    if scripts_section is None:
        raise RuntimeError("[tool.scripts] section not found")

    scripts: Dict[str, Script] = {}
    for name, raw in scripts_section.items():
        if not isinstance(raw, dict):
            raise RuntimeError(f"Script '{name}' is not a table")

        cmd = raw.get("cmd")
        if cmd is None:
            raise RuntimeError(f"Script '{name}' missing required 'cmd' field")

        cmd = cmd.strip()
        if cmd == "":
            raise RuntimeError(f"Script '{name}' has empty 'cmd' value")

        scripts[name] = Script(
            raw=raw,
            cmd=cmd,
            cwd=Path(raw.get("cwd", pyproject_path.parent)),
            description=raw.get("description", ""),
            env=raw.get("env", {}),
            name=name,
            shell=raw.get("shell", True),
        )

    return scripts


def build_parser(scripts) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pps",
        description="pyproject-scripts - run scripts from pyproject.toml",
        add_help=True,
    )

    sub = parser.add_subparsers(dest="script", metavar="<script>")
    for name, script in scripts.items():
        sub.add_parser(name, help=script.description, add_help=False)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    try:
        pyproject = discover_pyproject()
        scripts = load_scripts(pyproject)
        project_root = Path(pyproject).parent
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    parser = build_parser(scripts)

    ns, unknown = parser.parse_known_args(argv)

    if ns.script is None:
        # If script not provided, show help
        parser.print_help()
    else:
        return scripts[ns.script].run(project_root=project_root, extra_args=unknown)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
