"""Print the GitHub release notes for one version of the ``tyxter`` package.

The notes are the version's ``CHANGELOG.md`` section, under a pinned install line and a link to
its PyPI page. A missing, duplicated or empty section is an error, so the publish workflow refuses
a release before the PyPI upload rather than publishing it without notes.

Usage: ``python scripts/release_notes.py 0.8.0``
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"


def changelog_section(changelog: str, version: str) -> str:
    """Return the body of the ``## [<version>]`` section, without its heading."""
    heading = re.compile(rf"^## \[{re.escape(version)}\]( |$)")
    lines = changelog.splitlines()
    starts = [index for index, line in enumerate(lines) if heading.match(line)]
    if not starts:
        raise ValueError(f"CHANGELOG.md has no '## [{version}]' section")
    if len(starts) > 1:
        raise ValueError(f"CHANGELOG.md has {len(starts)} '## [{version}]' sections")
    body: list[str] = []
    for line in lines[starts[0] + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    section = "\n".join(body).strip()
    if not section:
        raise ValueError(f"CHANGELOG.md section '## [{version}]' is empty")
    return section


def release_notes(changelog: str, version: str) -> str:
    section = changelog_section(changelog, version)
    return (
        f"Install: `pip install tyxter=={version}` "
        f"([PyPI](https://pypi.org/project/tyxter/{version}/))\n\n{section}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the GitHub release notes for a version.")
    parser.add_argument("version", help="package version, for example 0.8.0")
    parser.add_argument("--changelog", type=Path, default=CHANGELOG, help="changelog to read")
    args = parser.parse_args(argv)
    version: str = args.version
    changelog: Path = args.changelog
    try:
        notes = release_notes(changelog.read_text(encoding="utf-8"), version)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    sys.stdout.write(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
