#!/usr/bin/env python3
"""Update the zh_TW store-changelog entry in nvda.po from changelog.md.

The add-on store shows ``addon_changelog`` translated through gettext, which
only works when the .po entry's msgid matches the current English text exactly.
This script recomputes that text from the topmost changelog.md section (reusing
``sync_addon_changelog``) and rewrites the msgid/msgstr pair anchored by the
"#. Brief changelog for this version" comment, leaving the rest of the file
untouched.

``--check`` exits 1 when the entry is stale (msgid outdated or msgstr empty).
``--apply FILE`` replaces the entry, taking the zh_TW translation from FILE
("-" for stdin); the translation must have the same number of lines as the
English text.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sync_addon_changelog import latest_section, to_plain_text

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "changelog.md"
PO_FILE = ROOT / "addon" / "locale" / "zh_TW" / "LC_MESSAGES" / "nvda.po"
ANCHOR = "#. Brief changelog for this version"

_UNESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def _escape(text: str) -> str:
	return text.replace("\\", "\\\\").replace('"', '\\"')


def _unescape(text: str) -> str:
	out: list[str] = []
	i = 0
	while i < len(text):
		if text[i] == "\\" and i + 1 < len(text):
			out.append(_UNESCAPES.get(text[i + 1], text[i + 1]))
			i += 2
		else:
			out.append(text[i])
			i += 1
	return "".join(out)


def _format_block(keyword: str, text: str) -> list[str]:
	"""Render ``text`` as a multi-line .po ``msgid``/``msgstr`` block."""
	lines = text.split("\n")
	block = [f'{keyword} ""']
	for i, line in enumerate(lines):
		newline = "\\n" if i < len(lines) - 1 else ""
		block.append(f'"{_escape(line)}{newline}"')
	return block


def entry_span(lines: list[str]) -> tuple[int, int]:
	"""Line span [start, end) of the msgid/msgstr block following ANCHOR."""
	# Match the extracted comment as a substring rather than a whole line: the
	# source comment in buildVars.py may grow extra words, and xgettext can wrap
	# or re-pad it, without changing which entry this is.
	anchor = next((i for i, ln in enumerate(lines) if ANCHOR in ln), None)
	if anchor is None:
		raise SystemExit(f"anchor comment {ANCHOR!r} not found in nvda.po")
	start = next((i for i, ln in enumerate(lines[anchor:], anchor) if ln.startswith("msgid")), None)
	if start is None:
		raise SystemExit("no msgid found after the changelog anchor comment")
	end = next((i for i, ln in enumerate(lines[start:], start) if not ln.strip()), len(lines))
	return start, end


def parse_entry(block: list[str]) -> tuple[str, str]:
	"""Return the (msgid, msgstr) texts of a .po entry block, unescaped."""
	parts: dict[str, list[str]] = {"msgid": [], "msgstr": []}
	current: list[str] | None = None
	for raw in block:
		line = raw.strip()
		for keyword in parts:
			if line.startswith(f"{keyword} "):
				current = parts[keyword]
				line = line[len(keyword) + 1 :]
				break
		if current is None or len(line) < 2 or not (line.startswith('"') and line.endswith('"')):
			raise SystemExit(f"unexpected line in the changelog .po entry: {raw!r}")
		current.append(_unescape(line[1:-1]))
	return "".join(parts["msgid"]), "".join(parts["msgstr"])


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	group = parser.add_mutually_exclusive_group(required=True)
	_ = group.add_argument("--check", action="store_true", help="exit 1 if the .po entry is stale")
	_ = group.add_argument("--apply", metavar="FILE", help="translation file to write ('-' for stdin)")
	args = parser.parse_args()

	new_msgid = to_plain_text(latest_section(CHANGELOG.read_text(encoding="utf-8")))
	source = PO_FILE.read_text(encoding="utf-8")
	lines = source.splitlines()
	start, end = entry_span(lines)
	msgid, msgstr = parse_entry(lines[start:end])

	if args.check:
		if msgid != new_msgid:
			print("nvda.po changelog msgid is out of date with changelog.md", file=sys.stderr)
			return 1
		if not msgstr.strip():
			print("nvda.po changelog msgstr is empty", file=sys.stderr)
			return 1
		return 0

	if args.apply == "-":
		translation = sys.stdin.read().strip()
	else:
		translation = Path(args.apply).read_text(encoding="utf-8").strip()
	if not translation:
		raise SystemExit("translation is empty")
	if len(translation.split("\n")) != len(new_msgid.split("\n")):
		raise SystemExit("translation line count does not match the English changelog text")
	# Catch the degenerate case where the model echoes the English text back:
	# it would pass every other check, get committed, and never be retried.
	if not any("\u4e00" <= ch <= "\u9fff" for ch in translation):
		raise SystemExit("translation contains no Chinese characters")

	block = _format_block("msgid", new_msgid) + _format_block("msgstr", translation)
	updated = "\n".join(lines[:start] + block + lines[end:]) + "\n"
	if updated == source:
		return 0  # already up to date
	_ = PO_FILE.write_text(updated, encoding="utf-8")
	print("nvda.po changelog entry updated")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
