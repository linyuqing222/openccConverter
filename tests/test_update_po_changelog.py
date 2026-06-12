# -*- coding: utf-8 -*-
# Tests for scripts/update_po_changelog.py.
# This file is covered by the GNU General Public License, version 2 or later.

"""Exercise the .po changelog updater: escaping round-trips, entry location,
``--check`` semantics, and ``--apply`` rewriting/idempotency."""

import os
import sys

import pytest

sys.path.insert(
	0,
	os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")),
)

import update_po_changelog as upc  # noqa: E402

CHANGELOG_MD = """# Changelog

## [2.0.0](https://example.com/compare) (2026-06-10)

### Bug Fixes

* fix thing ([#1](https://example.com/1)) ([abc1234](https://example.com/c))
"""

# to_plain_text(latest_section(CHANGELOG_MD)) renders to this:
EN_TEXT = "2.0.0 (2026-06-10)\nBug Fixes:\n- fix thing"

PO_TEMPLATE = """msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

#. Add-on summary
msgid "Something"
msgstr "東西"

#. Brief changelog for this version
#. Translators: what's new content for the add-on version to be shown in the add-on store
msgid ""
{msgid}
msgstr ""
{msgstr}

#. A trailing entry that must stay untouched
msgid "Tail"
msgstr "尾"
"""

STALE_PO = PO_TEMPLATE.format(
	msgid='"1.0.0 (2026-06-09)\\n"\n"- old line"',
	msgstr='"1.0.0 (2026-06-09)\\n"\n"- 舊行"',
)


@pytest.fixture
def fake_files(tmp_path, monkeypatch):
	changelog = tmp_path / "changelog.md"
	changelog.write_text(CHANGELOG_MD, encoding="utf-8")
	po = tmp_path / "nvda.po"
	po.write_text(STALE_PO, encoding="utf-8")
	monkeypatch.setattr(upc, "CHANGELOG", changelog)
	monkeypatch.setattr(upc, "PO_FILE", po)
	return po


def run_main(monkeypatch, *argv):
	monkeypatch.setattr(sys, "argv", ["update_po_changelog.py", *argv])
	return upc.main()


def test_escape_unescape_round_trip():
	for text in (
		"plain",
		'quotes "here" and back\\slash \\\\ two',
		"多行\n中文 ⚠ 警告\n- 項目",
		"tab\there",
	):
		assert upc._unescape(upc._escape(text)) == text


def test_format_block_and_parse_entry_round_trip():
	block = upc._format_block("msgid", EN_TEXT) + upc._format_block("msgstr", "譯文\n第二行\n第三行")
	msgid, msgstr = upc.parse_entry(block)
	assert msgid == EN_TEXT
	assert msgstr == "譯文\n第二行\n第三行"


def test_entry_span_finds_anchored_entry():
	lines = STALE_PO.splitlines()
	start, end = upc.entry_span(lines)
	msgid, msgstr = upc.parse_entry(lines[start:end])
	assert msgid == "1.0.0 (2026-06-09)\n- old line"
	assert msgstr == "1.0.0 (2026-06-09)\n- 舊行"


def test_entry_span_missing_anchor():
	with pytest.raises(SystemExit):
		upc.entry_span(['msgid "x"', 'msgstr "y"'])


def test_check_stale_msgid(fake_files, monkeypatch):
	assert run_main(monkeypatch, "--check") == 1


def test_check_empty_msgstr(fake_files, monkeypatch):
	current_msgid = "\n".join(upc._format_block("msgid", EN_TEXT)[1:])
	fake_files.write_text(
		PO_TEMPLATE.format(msgid=current_msgid, msgstr='""'),
		encoding="utf-8",
	)
	assert run_main(monkeypatch, "--check") == 1


def test_apply_then_check(fake_files, tmp_path, monkeypatch):
	translation = tmp_path / "zh.txt"
	translation.write_text("2.0.0 (2026-06-10)\n錯誤修正：\n- 修正問題\n", encoding="utf-8")
	assert run_main(monkeypatch, "--apply", str(translation)) == 0

	updated = fake_files.read_text(encoding="utf-8")
	lines = updated.splitlines()
	start, end = upc.entry_span(lines)
	msgid, msgstr = upc.parse_entry(lines[start:end])
	assert msgid == EN_TEXT
	assert msgstr == "2.0.0 (2026-06-10)\n錯誤修正：\n- 修正問題"
	# The rest of the file is untouched.
	assert '"Content-Type: text/plain; charset=UTF-8\\n"' in updated
	assert 'msgstr "東西"' in updated
	assert 'msgstr "尾"' in updated

	assert run_main(monkeypatch, "--check") == 0
	# Re-applying is a no-op.
	before = fake_files.read_text(encoding="utf-8")
	assert run_main(monkeypatch, "--apply", str(translation)) == 0
	assert fake_files.read_text(encoding="utf-8") == before


def test_apply_rejects_wrong_line_count(fake_files, tmp_path, monkeypatch):
	translation = tmp_path / "zh.txt"
	translation.write_text("只有一行\n", encoding="utf-8")
	with pytest.raises(SystemExit):
		run_main(monkeypatch, "--apply", str(translation))
	assert fake_files.read_text(encoding="utf-8") == STALE_PO


def test_apply_rejects_english_echo(fake_files, tmp_path, monkeypatch):
	translation = tmp_path / "zh.txt"
	translation.write_text(EN_TEXT + "\n", encoding="utf-8")
	with pytest.raises(SystemExit):
		run_main(monkeypatch, "--apply", str(translation))
	assert fake_files.read_text(encoding="utf-8") == STALE_PO


def test_apply_rejects_empty_translation(fake_files, tmp_path, monkeypatch):
	translation = tmp_path / "zh.txt"
	translation.write_text("\n\n", encoding="utf-8")
	with pytest.raises(SystemExit):
		run_main(monkeypatch, "--apply", str(translation))
