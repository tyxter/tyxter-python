"""Print the GitHub release notes for one version of the ``tyxter`` package.

The notes are the version's ``CHANGELOG.md`` section, under a pinned install line and a link to
its PyPI page. The section runs from its ``## [<version>]`` heading to the next ``## `` heading;
lines inside fenced code blocks never start or end a section. A missing or duplicated section, a
section with no entries (nothing but blank lines and headings), or an unclosed code fence is an
error, so the publish workflow refuses a release before the PyPI upload rather than publishing it
without notes.

Usage: ``python scripts/release_notes.py 0.8.0``
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}#{1,6}(\s|$)")


def _unfenced(lines: list[str]) -> list[bool]:
    """Mark each line that sits outside a fenced code block."""
    marks: list[bool] = []
    fence: str | None = None
    for line in lines:
        marks.append(fence is None)
        match = FENCE.match(line)
        if match is None:
            continue
        marker, rest = match.groups()
        if fence is None:
            fence = marker
        elif marker[0] == fence[0] and len(marker) >= len(fence) and not rest.strip():
            fence = None
    if fence is not None:
        raise ValueError("CHANGELOG.md has an unclosed code fence")
    return marks


def changelog_section(changelog: str, version: str) -> str:
    """Return the body of the ``## [<version>]`` section, without its heading."""
    heading = re.compile(rf"^## \[{re.escape(version)}\]( |$)")
    lines = changelog.splitlines()
    unfenced = _unfenced(lines)
    starts = [i for i, line in enumerate(lines) if unfenced[i] and heading.match(line)]
    if not starts:
        raise ValueError(f"CHANGELOG.md has no '## [{version}]' section")
    if len(starts) > 1:
        raise ValueError(f"CHANGELOG.md has {len(starts)} '## [{version}]' sections")
    start = starts[0] + 1
    end = next(
        (i for i in range(start, len(lines)) if unfenced[i] and lines[i].startswith("## ")),
        len(lines),
    )
    body = lines[start:end]
    if not any(
        line.strip() and not (unfenced[i] and HEADING.match(line))
        for i, line in enumerate(body, start)
    ):
        raise ValueError(f"CHANGELOG.md section '## [{version}]' has no entries")
    return "\n".join(body).strip()


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
