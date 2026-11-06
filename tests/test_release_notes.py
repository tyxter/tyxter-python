"""The publish workflow's CHANGELOG gate and GitHub release notes (scripts/release_notes.py).

Each expected section below is copied by hand from the fixture, following Keep a Changelog: a
version's section runs from its ``## [<version>]`` heading to the next ``## `` heading, and a
``## `` line inside a fenced code block is content, not a heading.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_notes.py"

CHANGELOG = """\
# Changelog

## [Unreleased]

- Pending entry.

## [0.9.0] - 2026-11-06

### Added

- Groups.

```markdown
## Not a release heading
```

- Entry after the fence.

## [0.8.2] - 2026-10-20

## [0.8.1] - 2026-10-10

### Fixed

## [0.8.0] - 2026-09-03

### Added

- Oldest entry.
"""

FENCED_SECTION = """\
### Added

- Groups.

```markdown
## Not a release heading
```

- Entry after the fence."""

DUPLICATED = "## [0.9.0] - 2026-11-06\n\n- One.\n\n## [0.9.0] - 2026-11-07\n\n- Two.\n"
UNCLOSED_FENCE = "## [0.9.0] - 2026-11-06\n\n- One.\n\n```text\n## [0.8.0]\n"


@pytest.mark.parametrize(
    ("changelog", "version", "section"),
    [
        pytest.param(CHANGELOG, "0.9.0", FENCED_SECTION, id="fenced-heading-is-content"),
        pytest.param(CHANGELOG, "0.8.0", "### Added\n\n- Oldest entry.", id="last-section"),
        pytest.param(CHANGELOG, "0.7.0", None, id="missing-version"),
        pytest.param(CHANGELOG, "0.9", None, id="no-prefix-match"),
        pytest.param(CHANGELOG, "0.8.2", None, id="empty-section"),
        pytest.param(CHANGELOG, "0.8.1", None, id="headings-without-entries"),
        pytest.param(DUPLICATED, "0.9.0", None, id="duplicated-section"),
        pytest.param(UNCLOSED_FENCE, "0.9.0", None, id="unclosed-fence"),
    ],
)
def test_release_notes_carry_exactly_the_version_section(
    tmp_path: Path, changelog: str, version: str, section: str | None
) -> None:
    path = tmp_path / "CHANGELOG.md"
    path.write_text(changelog, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), version, "--changelog", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )

    if section is None:
        assert result.returncode == 1
        assert result.stdout == ""
        assert result.stderr.startswith("error: ")
        return
    assert result.returncode == 0, result.stderr
    preamble, found, rest = result.stdout.partition(section)
    assert found, result.stdout
    assert not rest.strip()
    assert "#" not in preamble
    assert f"pip install tyxter=={version}" in preamble
    assert f"https://pypi.org/project/tyxter/{version}/" in preamble
