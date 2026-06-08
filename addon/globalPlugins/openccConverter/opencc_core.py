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

# Engines are cached and reused.  opencc-purepy builds each direction's
# dictionary union once and shares it process-wide, so construction is cheap;
# caching just avoids repeating even that small setup.  A lock guards the cache
# because NVDA may invoke conversion from more than one thread.
_engine_cache: "dict[str, OpenCC]" = {}
_cache_lock = threading.Lock()


def is_supported(conversion: str) -> bool:
	"""Return ``True`` if ``conversion`` is one of the supported directions."""
	return conversion in CONVERSIONS


def _get_engine(conversion: str) -> OpenCC:
	"""Return a cached :class:`OpenCC` engine for ``conversion``.

	:raises ValueError: if ``conversion`` is not a supported direction.
	"""
	if not is_supported(conversion):
		raise ValueError(
			"Unsupported conversion %r; expected one of %s" % (conversion, ", ".join(CONVERSION_CODES))
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
