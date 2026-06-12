# -*- coding: utf-8 -*-
# openccConverter: offline Simplified/Traditional Chinese conversion core.
# Copyright (C) 2026 Kevin Lin
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pure conversion core for openccConverter.

This module deliberately has **no dependency on NVDA**, so it can be imported
and unit-tested on any platform with a plain Python interpreter.  All Chinese
conversion is performed fully offline by the bundled, pure-Python
``opencc-purepy`` engine (MIT License) under ``_vendor/opencc_purepy``, which
ships the OpenCC dictionaries (Apache License 2.0, see ``dicts/LICENSE``).

The engine is imported by injecting the ``_vendor`` directory onto ``sys.path``
and importing the top-level ``opencc_purepy`` package.  This keeps the import
working both when the file is loaded as part of the NVDA add-on package and
when it is imported as a stand-alone module by the test suite.
"""

import os
import sys
import threading

# --- Make the vendored, pure-Python OpenCC engine importable -----------------
_VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_vendor")
if _VENDOR_DIR not in sys.path:
	sys.path.insert(0, _VENDOR_DIR)


class _SerialPool:
	"""A serial, in-process stand-in for :class:`multiprocessing.Pool`.

	The bundled engine reaches for a ``Pool`` on very large inputs (text of
	~1,000,000 characters or more, e.g. converting a whole book).  Running that
	work serially in this process yields the same result -- NVDA is
	single-process anyway -- so the only thing lost is the parallelism.  An
	earlier stub *raised* here instead, which surfaced large conversions to the
	user as an untranslated "Conversion failed" error.
	"""

	def __init__(self, *args, **kwargs):
		pass

	def map(self, func, iterable, chunksize=None):
		return [func(item) for item in iterable]

	def close(self):
		pass

	def join(self):
		pass

	def terminate(self):
		pass

	def __enter__(self):
		return self

	def __exit__(self, *exc):
		return False


def _ensure_multiprocessing() -> None:
	"""Provide a minimal ``multiprocessing`` stand-in on runtimes that lack it.

	NVDA ships a stripped-down, frozen CPython that omits the
	``multiprocessing`` module.  ``opencc_purepy.core`` imports ``Pool`` and
	``cpu_count`` at module load time and reaches for a real ``Pool`` on very
	large inputs (~1,000,000 characters or more), which *can* happen -- e.g.
	converting a whole book from the clipboard.  Rather than patch the vendored
	engine -- which would be lost the next time it is re-synced from upstream --
	we install a tiny stub into ``sys.modules`` whose :class:`_SerialPool` runs
	the work serially, so large conversions still succeed instead of failing.

	On a normal Python interpreter (e.g. the test suite) the real module imports
	fine and this function does nothing.
	"""
	try:
		import multiprocessing  # noqa: F401

		return
	except ImportError:
		pass

	import types

	stub = types.ModuleType("multiprocessing")
	stub.cpu_count = lambda: 1
	stub.Pool = _SerialPool
	sys.modules["multiprocessing"] = stub


_ensure_multiprocessing()

from opencc_purepy import OpenCC  # noqa: E402  (import after sys.path injection)


#: The conversion directions exposed to the user, in the order they should
#: appear in the settings panel.  Keys are OpenCC config names (built-in
#: opencc-purepy configurations such as ``s2twp``); values are short English
#: descriptions used by the test-suite and as a fallback when NVDA's gettext
#: translations are unavailable.
CONVERSIONS: "dict[str, str]" = {
	"s2t": "Simplified Chinese to Traditional Chinese",
	"s2tw": "Simplified Chinese to Traditional Chinese (Taiwan)",
	"s2twp": "Simplified Chinese to Traditional Chinese (Taiwan, with phrases)",
	"t2s": "Traditional Chinese to Simplified Chinese",
	"tw2s": "Traditional Chinese (Taiwan) to Simplified Chinese",
	"tw2sp": "Traditional Chinese (Taiwan) to Simplified Chinese (with phrases)",
}

#: Ordered tuple of the supported conversion codes.
CONVERSION_CODES: "tuple[str, ...]" = tuple(CONVERSIONS.keys())

#: Default conversion direction.  ``s2twp`` is the most complete
#: Simplified -> Traditional (Taiwan) mapping and yields idiomatic Taiwanese
#: vocabulary (e.g. 软件 -> 軟體, 内存 -> 記憶體).
DEFAULT_CONVERSION = "s2twp"

#: Default conversion direction per UI language, for languages whose users are
#: better served by something other than :data:`DEFAULT_CONVERSION`.  Keys are
#: normalised language codes (lower case, ``_`` separator); matching is exact.
#:
#: Simplified-Chinese locales default to Traditional -> Simplified: ``tw2sp``
#: rather than plain ``t2s`` because it also normalises Taiwan variant forms
#: and maps Taiwanese vocabulary back (軟體 -> 软件), and is no worse than
#: ``t2s`` on non-Taiwan traditional text.  Hong Kong/Macau locales fall back
#: to plain ``s2t`` because the Taiwan-specific variants and vocabulary would
#: be wrong there and the ``hk`` configurations are not (yet) exposed.
#:
#: Bare ``zh`` is what NVDA reports for Chinese variants it ships no
#: translation for (e.g. a Windows display language of zh_SG/zh_CHS): it then
#: falls back to the zh_CN catalogue, so the interface the user actually sees
#: is Simplified Chinese and the Simplified default applies.
_LANGUAGE_DEFAULTS: "dict[str, str]" = {
	"zh": "tw2sp",
	"zh_cn": "tw2sp",
	"zh_sg": "tw2sp",
	"zh_hk": "s2t",
	"zh_mo": "s2t",
}


def default_for_language(language: "str | None") -> str:
	"""Return the default conversion direction for a UI language code.

	:param language: a language code such as ``zh_CN``, ``zh-TW`` or ``en``
		(case-insensitive, ``-``/``_`` interchangeable), or ``None``.
	:returns: one of :data:`CONVERSION_CODES`; :data:`DEFAULT_CONVERSION` for
		unknown or missing languages.
	"""
	if not language:
		return DEFAULT_CONVERSION
	normalized = language.strip().lower().replace("-", "_")
	return _LANGUAGE_DEFAULTS.get(normalized, DEFAULT_CONVERSION)


#: Maps each supported conversion to its reverse direction, used by the
#: "swap direction" command.  Every supported code has exactly one reverse, and
#: reversing twice yields the original (the mapping is an involution).  Phrase
#: handling is preserved across a swap (e.g. ``s2twp`` <-> ``tw2sp``).
REVERSALS: "dict[str, str]" = {
	"s2t": "t2s",
	"t2s": "s2t",
	"s2tw": "tw2s",
	"tw2s": "s2tw",
	"s2twp": "tw2sp",
	"tw2sp": "s2twp",
}

# Engines are cached and reused.  opencc-purepy builds each direction's
# dictionary union once and shares it process-wide, so construction is cheap;
# caching just avoids repeating even that small setup.  A lock guards the cache
# because NVDA may invoke conversion from more than one thread.
_engine_cache: "dict[str, OpenCC]" = {}
_cache_lock = threading.Lock()


def is_supported(conversion: str) -> bool:
	"""Return ``True`` if ``conversion`` is one of the supported directions."""
	return conversion in CONVERSIONS


def reverse(conversion: str) -> str:
	"""Return the reverse of ``conversion`` (e.g. ``s2twp`` -> ``tw2sp``).

	:raises ValueError: if ``conversion`` has no supported reverse direction.
	"""
	try:
		return REVERSALS[conversion]
	except KeyError:
		raise ValueError("No reverse for %r; expected one of %s" % (conversion, ", ".join(CONVERSION_CODES)))


def _get_engine(conversion: str) -> OpenCC:
	"""Return a cached :class:`OpenCC` engine for ``conversion``.

	:raises ValueError: if ``conversion`` is not a supported direction.
	"""
	if not is_supported(conversion):
		raise ValueError(
			"Unsupported conversion %r; expected one of %s" % (conversion, ", ".join(CONVERSION_CODES)),
		)
	engine = _engine_cache.get(conversion)
	if engine is None:
		with _cache_lock:
			# Re-check inside the lock in case another thread just built it.
			engine = _engine_cache.get(conversion)
			if engine is None:
				engine = OpenCC(conversion)
				_engine_cache[conversion] = engine
	return engine


def convert(text: str, conversion: str = DEFAULT_CONVERSION) -> str:
	"""Convert ``text`` between Simplified and Traditional Chinese, offline.

	:param text: the source text.
	:param conversion: one of :data:`CONVERSION_CODES`.
	:returns: the converted text.  Empty/whitespace-only input is returned
		unchanged without invoking the engine.
	:raises ValueError: if ``conversion`` is not supported.
	"""
	if not text:
		return text
	return _get_engine(conversion).convert(text)
