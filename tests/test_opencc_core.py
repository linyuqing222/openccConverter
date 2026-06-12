# -*- coding: utf-8 -*-
# Tests for the openccConverter conversion core.
# This file is covered by the GNU General Public License, version 2 or later.

"""Unit tests for :mod:`opencc_core`.

These tests exercise the NVDA-independent conversion core directly, so they run
on any platform with a plain Python interpreter and require no network access
(the OpenCC dictionaries are bundled in the add-on).

Run with ``-s`` to see the printed conversion evidence, e.g.::

    pytest -s -v tests/
"""

import pytest

import opencc_core


# The exact cases required by the project's acceptance criteria.  All of these
# are produced by the ``s2twp`` (Simplified -> Traditional, Taiwan, with
# phrases) direction, which yields idiomatic Taiwanese vocabulary.
S2TWP_CASES = [
	("软件", "軟體"),
	("内存", "記憶體"),
	("简体字", "簡體字"),
	("头发", "頭髮"),
	("发展", "發展"),
]


@pytest.mark.parametrize("source, expected", S2TWP_CASES)
def test_s2twp_required_cases(source, expected):
	result = opencc_core.convert(source, "s2twp")
	print(f"[s2twp] {source} -> {result}  (expected {expected})")
	assert result == expected


def test_s2tw_and_s2twp_differ_for_same_input():
	"""The same input must produce different output under s2tw and s2twp."""
	for source in ("软件", "内存"):
		s2tw_out = opencc_core.convert(source, "s2tw")
		s2twp_out = opencc_core.convert(source, "s2twp")
		print(f"[s2tw vs s2twp] {source}: s2tw={s2tw_out}  s2twp={s2twp_out}")
		assert s2tw_out != s2twp_out

	# Pin the concrete values so a regression is obvious.
	assert opencc_core.convert("内存", "s2tw") == "內存"
	assert opencc_core.convert("内存", "s2twp") == "記憶體"
	assert opencc_core.convert("软件", "s2tw") == "軟件"
	assert opencc_core.convert("软件", "s2twp") == "軟體"


def test_print_acceptance_evidence():
	"""Print a consolidated evidence block for the acceptance criteria."""
	print("\n=== openccConverter conversion evidence ===")
	for source, expected in S2TWP_CASES:
		result = opencc_core.convert(source, "s2twp")
		status = "OK" if result == expected else "MISMATCH"
		print(f"s2twp: {source} -> {result}  (expected {expected}) [{status}]")
		assert result == expected
	sample = "软件"
	print(
		f"same input differs: {sample}: "
		f"s2tw={opencc_core.convert(sample, 's2tw')}  "
		f"s2twp={opencc_core.convert(sample, 's2twp')}",
	)


def test_all_six_directions_supported():
	expected = ("s2t", "s2tw", "s2twp", "t2s", "tw2s", "tw2sp")
	assert opencc_core.CONVERSION_CODES == expected
	# Every direction must build an engine and convert without error.
	for code in expected:
		assert opencc_core.is_supported(code)
		out = opencc_core.convert("测试", code)
		print(f"[{code}] 测试 -> {out}")
		assert isinstance(out, str) and out


def test_roundtrip_traditional_to_simplified():
	# tw2sp is the inverse-ish of s2twp for vocabulary.
	assert opencc_core.convert("軟體", "tw2sp") == "软件"
	assert opencc_core.convert("記憶體", "tw2sp") == "内存"


def test_empty_and_whitespace_input_unchanged():
	assert opencc_core.convert("", "s2twp") == ""
	assert opencc_core.convert("   ", "s2twp") == "   "


def test_default_conversion_is_s2twp():
	assert opencc_core.DEFAULT_CONVERSION == "s2twp"
	# Calling convert without an explicit direction uses the default.
	assert opencc_core.convert("内存") == "記憶體"


@pytest.mark.parametrize(
	"language, expected",
	[
		# Simplified-Chinese locales default to Traditional -> Simplified.
		("zh_CN", "tw2sp"),
		("zh_SG", "tw2sp"),
		# Bare "zh" is NVDA's fallback for unshipped Chinese variants; the UI it
		# shows is then Simplified Chinese (zh_CN catalogue).
		("zh", "tw2sp"),
		# Hong Kong/Macau get plain s2t (no Taiwan variants or vocabulary).
		("zh_HK", "s2t"),
		("zh_MO", "s2t"),
		# Taiwan and everything else keep the global default.
		("zh_TW", "s2twp"),
		("en", "s2twp"),
		("ja", "s2twp"),
		# Normalisation: case-insensitive, - and _ interchangeable.
		("ZH-cn", "tw2sp"),
		("zh-HK", "s2t"),
		# Missing/unknown languages fall back to the default.
		(None, "s2twp"),
		("", "s2twp"),
		("klingon", "s2twp"),
	],
)
def test_default_for_language(language, expected):
	result = opencc_core.default_for_language(language)
	print(f"default_for_language({language!r}) -> {result}")
	assert result == expected


def test_language_defaults_are_supported_directions():
	"""Every per-language default must be a direction the add-on exposes."""
	for language, code in opencc_core._LANGUAGE_DEFAULTS.items():
		assert opencc_core.is_supported(code), (language, code)


def test_unsupported_conversion_raises():
	with pytest.raises(ValueError):
		opencc_core.convert("测试", "does-not-exist")


def test_every_direction_has_a_supported_reverse():
	"""Each supported direction must reverse to another supported direction."""
	for code in opencc_core.CONVERSION_CODES:
		rev = opencc_core.reverse(code)
		print(f"reverse({code}) -> {rev}")
		assert opencc_core.is_supported(rev)


def test_reverse_is_an_involution():
	"""Reversing twice must return the original direction."""
	for code in opencc_core.CONVERSION_CODES:
		assert opencc_core.reverse(opencc_core.reverse(code)) == code


def test_reverse_concrete_pairs():
	assert opencc_core.reverse("s2twp") == "tw2sp"
	assert opencc_core.reverse("tw2sp") == "s2twp"
	assert opencc_core.reverse("s2tw") == "tw2s"
	assert opencc_core.reverse("s2t") == "t2s"
	# Phrase handling is preserved across the swap: the simplified->traditional
	# vocabulary mapping and its reverse round-trip.
	assert opencc_core.convert("内存", "s2twp") == "記憶體"
	assert opencc_core.convert("記憶體", opencc_core.reverse("s2twp")) == "内存"


def test_reverse_unsupported_raises():
	with pytest.raises(ValueError):
		opencc_core.reverse("does-not-exist")


def test_serial_pool_runs_work_serially():
	"""The multiprocessing fallback Pool must run work in-process via map().

	On NVDA's frozen Python (no multiprocessing) the engine reaches for this
	Pool on very large inputs; it must compute results rather than raise.
	"""
	pool = opencc_core._SerialPool(processes=4)
	with pool as p:
		assert p.map(lambda x: x * 2, [1, 2, 3]) == [2, 4, 6]
	# The lifecycle methods the engine may call must be safe no-ops.
	other = opencc_core._SerialPool()
	other.close()
	other.join()
	other.terminate()
