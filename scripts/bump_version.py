"""Keep the cliphop version in sync across every place it appears.

Usage:
    python scripts/bump_version.py --check        # verify all places, nonzero on drift
    python scripts/bump_version.py bump <version> # set every place, then run `uv lock`

`pyproject.toml` is the canonical source: `--check` reads the version from there
and compares every other place against it. Each place is a file plus a regex
with exactly one capture group (the version) and a replacement template that
reproduces the whole match with `{version}` inserted. A place that does not
match exactly once aborts the run.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Place:
    path: str
    pattern: str
    replacement: str  # whole-match replacement; `{version}` is the new version


# Canonical source first; the rest are compared against it.
PLACES: tuple[Place, ...] = (
    Place("pyproject.toml", r'^version = "([^"]+)"', 'version = "{version}"'),
    Place("Dockerfile", r"^ARG VERSION=(\S+)", "ARG VERSION={version}"),
    Place(
        "compose.yaml",
        r"image: oci\.rohwer\.sh/cliphop:(\S+)",
        "image: oci.rohwer.sh/cliphop:{version}",
    ),
    Place(
        "src/cliphop/__init__.py",
        r'^__version__ = "([^"]+)"',
        '__version__ = "{version}"',
    ),
    # The build example carries the version twice (ARG and image tag).
    Place(
        "docs/DEPLOYMENT.md",
        r"docker build --build-arg VERSION=(\S+) -t oci\.rohwer\.sh/cliphop:\S+ \.",
        "docker build --build-arg VERSION={version} -t oci.rohwer.sh/cliphop:{version} .",
    ),
    Place(
        "docs/DEPLOYMENT.md",
        r"docker push oci\.rohwer\.sh/cliphop:(\S+)",
        "docker push oci.rohwer.sh/cliphop:{version}",
    ),
    # uv.lock is derived, but checking it catches a forgotten `uv lock`.
    Place("uv.lock", r'(?<=name = "cliphop"\nversion = ")([^"]+)', "{version}"),
)

CANONICAL = "pyproject.toml"


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _write(path: str, text: str) -> None:
    (REPO_ROOT / path).write_text(text, encoding="utf-8")


def _matches(place: Place, text: str) -> list[re.Match[str]]:
    return list(re.finditer(place.pattern, text, re.MULTILINE))


def canonical_version() -> str:
    match = re.search(r'^version = "([^"]+)"', _read(CANONICAL), re.MULTILINE)
    if match is None:
        raise SystemExit(f"cannot read version from {CANONICAL}")
    return match.group(1)


def check() -> int:
    expected = canonical_version()
    problems: list[str] = []
    for place in PLACES:
        matches = _matches(place, _read(place.path))
        if len(matches) != 1:
            problems.append(
                f"{place.path}: pattern matched {len(matches)} times, expected exactly 1"
            )
            continue
        found = matches[0].group(1)
        if found != expected:
            problems.append(f"{place.path}: {found!r} != {expected!r}")
    if problems:
        print(
            f"version drift detected (canonical {expected!r} from {CANONICAL}):",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"version consistent: {expected}")
    return 0


def bump(version: str) -> int:
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z.+-]*", version):
        print(f"abort: {version!r} is not a valid version", file=sys.stderr)
        return 1
    for place in PLACES:
        replacement = place.replacement.format(version=version)
        text, count = re.subn(
            place.pattern, replacement, _read(place.path), flags=re.MULTILINE
        )
        if count != 1:
            print(
                f"abort: {place.path}: pattern matched {count} times, expected exactly 1",
                file=sys.stderr,
            )
            return 1
        _write(place.path, text)
    print(f"set version to {version!r} in {len(PLACES)} places; running `uv lock`")
    return subprocess.run(["uv", "lock"], cwd=REPO_ROOT).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize the cliphop version across the repo."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify every place against pyproject.toml (no writes)",
    )
    parser.add_argument("command", nargs="?", choices=["bump"], help="'bump' to set a version")
    parser.add_argument("version", nargs="?", help="version to set with 'bump'")
    ns = parser.parse_args(argv)

    if ns.check:
        if ns.command is not None or ns.version is not None:
            parser.error("--check takes no further arguments")
        return check()
    if ns.command == "bump" and ns.version is not None:
        return bump(ns.version)
    parser.error("use 'bump <version>' or '--check'")


if __name__ == "__main__":
    raise SystemExit(main())
