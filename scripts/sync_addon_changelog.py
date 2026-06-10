#!/usr/bin/env python3
"""Sync ``addon_changelog`` in buildVars.py from the latest changelog.md entry.

release-please owns ``changelog.md`` (and bumps ``addon_version``), but it has no
way to write the generated notes into ``buildVars.py``. The store "What's new"
text therefore goes stale. This script reads the topmost version section from
``changelog.md``, turns it into readable plain text, and writes it back into the
``addon_changelog=_(\"\"\"...\"\"\")`` literal so the value stays a real gettext
string (and thus still translatable).

Run with ``--dry-run`` to print the extracted text without touching the file.
Exits non-zero with ``--check`` when buildVars.py would change.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "changelog.md"
BUILD_VARS = ROOT / "buildVars.py"

# Matches the inner text of `addon_changelog=_("""...""")`.
_CHANGELOG_FIELD = re.compile(r'(addon_changelog=_\(""")(.*?)("""\))', re.DOTALL)
# `([#3](url))` / `([623b136](url))` style trailing references.
_LINK_REF = re.compile(r"\s*\(\[[^\]]+\]\([^)]+\)\)")
# Inline markdown link `[text](url)` -> `text` (e.g. the version in the header).
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def latest_section(changelog: str) -> str:
	"""Return the first `## ...` section, version header included."""
	lines = changelog.splitlines()
	start = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), None)
	if start is None:
		raise SystemExit("no '## ' version section found in changelog.md")
	end = next(
		(i for i, ln in enumerate(lines[start + 1 :], start + 1) if ln.startswith("## ")),
		len(lines),
	)
	return "\n".join(lines[start:end])


def to_plain_text(section: str) -> str:
	"""Turn a release-please markdown section into plain store-friendly text."""
	out: list[str] = []
	for raw in section.splitlines():
		line = _MD_LINK.sub(r"\1", _LINK_REF.sub("", raw)).rstrip()
		if not line:
			continue
		if line.startswith("## "):  # "## 1.0.1 (2026-06-09)" -> "1.0.1 (2026-06-09)"
			out.append(line[3:].strip())
		elif line.startswith("### "):  # "### Bug Fixes" -> "Bug Fixes:"
			out.append(f"{line[4:].strip()}:")
		elif line.startswith("* "):  # "* foo" -> "- foo"
			out.append(f"- {line[2:].strip()}")
		else:
			out.append(line)
	return "\n".join(out).strip()


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	_ = parser.add_argument("--dry-run", action="store_true", help="print the text, don't write")
	_ = parser.add_argument("--check", action="store_true", help="exit 1 if buildVars.py is stale")
	args = parser.parse_args()

	new_text = to_plain_text(latest_section(CHANGELOG.read_text(encoding="utf-8")))

	if args.dry_run:
		print(new_text)
		return 0

	source = BUILD_VARS.read_text(encoding="utf-8")
	match = _CHANGELOG_FIELD.search(source)
	if match is None:
		raise SystemExit('could not find addon_changelog=_("""...""") in buildVars.py')
	if match.group(2) == new_text:
		return 0  # already in sync

	if args.check:
		print("buildVars.py addon_changelog is out of date with changelog.md", file=sys.stderr)
		return 1

	updated = f"{match.group(1)}{new_text}{match.group(3)}"
	_ = BUILD_VARS.write_text(source[: match.start()] + updated + source[match.end() :], encoding="utf-8")
	print("buildVars.py addon_changelog updated")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
