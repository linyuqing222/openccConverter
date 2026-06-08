# -*- coding: utf-8 -*-
# openccConverter: offline Simplified/Traditional Chinese conversion for NVDA.
# Copyright (C) 2026 Kevin Lin
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""NVDA global plugin offering offline Simplified <-> Traditional Chinese
conversion of the selected text (single press) or the clipboard (double press).

The full result is always copied to the clipboard (the source is never replaced
in place); short results are spoken, while large results are announced as a
character count.  Conversion runs on a background thread with an audible progress
tone, and is delegated to :mod:`opencc_core`, a NVDA-independent module wrapping
the bundled, fully offline OpenCC engine.
"""

import threading

import globalPluginHandler
import scriptHandler
from scriptHandler import script
import api
import ui
import config
import core
import queueHandler
import textInfos
import tones
import browseMode
import addonHandler
import wx
from gui import guiHelper, settingsDialogs
from logHandler import log

from . import opencc_core

addonHandler.initTranslation()


#: Configuration section / key used in ``nvda.ini`` (``config.conf``).
CONFIG_SECTION = "openccConverter"

# Register the configuration specification.  The selected conversion direction
# is persisted here.
config.conf.spec[CONFIG_SECTION] = {
	"conversion": 'string(default="%s")' % opencc_core.DEFAULT_CONVERSION,
}


#: Human-readable, translatable labels for each conversion direction, keyed by
#: the OpenCC config code.  Mirrors :data:`opencc_core.CONVERSIONS`.
CONVERSION_LABELS = {
	# Translators: A conversion direction shown in the settings panel.
	"s2t": _("Simplified Chinese → Traditional Chinese"),
	# Translators: A conversion direction shown in the settings panel.
	"s2tw": _("Simplified Chinese → Traditional Chinese (Taiwan)"),
	# Translators: A conversion direction shown in the settings panel.
	"s2twp": _("Simplified Chinese → Traditional Chinese (Taiwan, with phrases)"),
	# Translators: A conversion direction shown in the settings panel.
	"t2s": _("Traditional Chinese → Simplified Chinese"),
	# Translators: A conversion direction shown in the settings panel.
	"tw2s": _("Traditional Chinese (Taiwan) → Simplified Chinese"),
	# Translators: A conversion direction shown in the settings panel.
	"tw2sp": _("Traditional Chinese (Taiwan) → Simplified Chinese (with phrases)"),
}


def _currentConversion() -> str:
	"""Return the configured conversion code, falling back to the default."""
	conversion = config.conf[CONFIG_SECTION]["conversion"]
	if not opencc_core.is_supported(conversion):
		conversion = opencc_core.DEFAULT_CONVERSION
	return conversion


class OpenCCSettingsPanel(settingsDialogs.SettingsPanel):
	# Translators: Title of the openccConverter category in NVDA's settings dialog.
	title = _("OpenCC Converter")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Keep a stable ordering of codes that matches the choice control.
		self._codes = list(opencc_core.CONVERSION_CODES)
		labels = [CONVERSION_LABELS[code] for code in self._codes]
		# Translators: Label for the conversion direction combo box in the settings panel.
		self._conversionChoice = sHelper.addLabeledControl(
			_("Conversion &direction:"), wx.Choice, choices=labels
		)
		current = _currentConversion()
		self._conversionChoice.SetSelection(self._codes.index(current))

	def onSave(self):
		config.conf[CONFIG_SECTION]["conversion"] = self._codes[self._conversionChoice.GetSelection()]


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: Input gestures category for this add-on.
	scriptCategory = _("OpenCC Converter")

	#: How long, in milliseconds, to wait before treating a press as a final
	#: single press.  It must exceed NVDA's ~0.5s multi-press window so a second
	#: press can cancel the deferred single-press (selection) conversion.
	_MULTI_PRESS_DEFER_MS = 600

	#: Tone (Hz, ms) played the moment a conversion starts, as an immediate cue.
	_START_BEEP = (660, 80)
	#: Tone (Hz, ms) repeated while a conversion is still running.
	_PROGRESS_BEEP = (500, 100)
	#: Gap, in milliseconds, between progress beeps.
	_PROGRESS_INTERVAL_MS = 800
	#: Results no longer than this are spoken verbatim; longer results are
	#: announced as a character count instead, to avoid flooding the speech
	#: buffer (e.g. when converting a whole book from the clipboard).
	_MAX_CHARS_TO_SPEAK = 1000

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._pendingTimer = None
		self._progressTimer = None
		self._converting = False
		self._terminated = False
		settingsDialogs.NVDASettingsDialog.categoryClasses.append(OpenCCSettingsPanel)

	def terminate(self):
		self._terminated = True
		self._cancelPending()
		self._cancelProgress()
		try:
			settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OpenCCSettingsPanel)
		except ValueError:
			pass
		super().terminate()

	# --- gesture handling ----------------------------------------------------

	@script(
		# Translators: Description of the conversion command shown in Input Gestures.
		description=_(
			"Converts the selected text between Simplified and Traditional Chinese. "
			"Press twice quickly to convert the text on the clipboard instead. "
			"The result is copied to the clipboard; short results are spoken, while "
			"large results are announced as a character count."
		),
		gesture="kb:NVDA+shift+o",
	)
	def script_convert(self, gesture):
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 0:
			# Either a single press or the first of a double press.  Defer the
			# selection conversion; a second press will cancel it.
			self._cancelPending()
			self._pendingTimer = core.callLater(self._MULTI_PRESS_DEFER_MS, self._convertSelection)
		elif repeatCount == 1:
			# Second press inside the multi-press window: convert the clipboard.
			self._cancelPending()
			self._convertClipboard()
		# Higher repeat counts are ignored.

	def _cancelPending(self):
		if self._pendingTimer is not None:
			try:
				self._pendingTimer.Stop()
			except Exception:
				pass
			self._pendingTimer = None

	# --- conversion actions --------------------------------------------------

	def _convertSelection(self):
		self._pendingTimer = None
		text = self._getSelectedText()
		if text is None:
			# Translators: Reported when no text is selected.
			ui.message(_("No selection"))
			return
		self._beginConversion(text)

	def _convertClipboard(self):
		text = self._getClipboardText()
		if not text:
			# Translators: Reported when the clipboard contains no convertible text.
			ui.message(_("The clipboard is empty"))
			return
		self._beginConversion(text)

	def _beginConversion(self, text: str):
		"""Start converting ``text`` on a background thread, with audible cues.

		The conversion itself can take several seconds for very large inputs
		(e.g. a whole book), so it runs off the main thread to keep NVDA
		responsive.  An immediate tone acknowledges the request and a progress
		tone repeats until the conversion finishes.
		"""
		if not text or not text.strip():
			# Translators: Reported when there is no text to convert.
			ui.message(_("There is no text to convert"))
			return
		if self._converting:
			# A conversion is already running; ignore overlapping triggers.
			return
		self._converting = True
		tones.beep(*self._START_BEEP)
		self._progressTimer = core.callLater(self._PROGRESS_INTERVAL_MS, self._onProgressTick)
		conversion = _currentConversion()
		threading.Thread(target=self._conversionWorker, args=(text, conversion), daemon=True).start()

	def _onProgressTick(self):
		# Runs on the main thread; reschedules itself until conversion finishes.
		if not self._converting:
			return
		tones.beep(*self._PROGRESS_BEEP)
		self._progressTimer = core.callLater(self._PROGRESS_INTERVAL_MS, self._onProgressTick)

	def _conversionWorker(self, text: str, conversion: str):
		# Runs on a background thread.  Only the pure, NVDA-independent core runs
		# here; the result is handed back to the main thread for reporting.
		try:
			result, failed = opencc_core.convert(text, conversion), False
		except Exception:
			log.error("openccConverter: conversion failed", exc_info=True)
			result, failed = None, True
		queueHandler.queueFunction(queueHandler.eventQueue, self._finishConversion, result, failed)

	def _finishConversion(self, result, failed: bool):
		# Runs on the main thread (marshalled via queueHandler).
		self._cancelProgress()
		self._converting = False
		if self._terminated:
			return
		if failed:
			# Translators: Reported when conversion unexpectedly fails.
			ui.message(_("Conversion failed"))
			return
		# The full converted text is always copied; the source is never replaced
		# in place.  Short results are spoken; large ones are summarised so we do
		# not flood the speech buffer.
		api.copyToClip(result)
		if len(result) <= self._MAX_CHARS_TO_SPEAK:
			ui.message(result)
		else:
			count = len(result)
			ui.message(
				ngettext(
					# Translators: Announced after converting a large amount of text,
					# instead of speaking the whole result. {0} is the character count.
					"Converted and copied {0} character to the clipboard",
					"Converted and copied {0} characters to the clipboard",
					count,
				).format(count)
			)

	def _cancelProgress(self):
		if self._progressTimer is not None:
			try:
				self._progressTimer.Stop()
			except Exception:
				pass
			self._progressTimer = None

	# --- text retrieval helpers ----------------------------------------------

	def _getSelectedText(self):
		"""Return the currently selected text, or ``None`` if there is no selection."""
		obj = api.getFocusObject()
		treeInterceptor = obj.treeInterceptor
		if (
			isinstance(treeInterceptor, browseMode.BrowseModeDocumentTreeInterceptor)
			and not treeInterceptor.passThrough
		):
			obj = treeInterceptor
		try:
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError):
			return None
		if not info or info.isCollapsed:
			return None
		return info.text

	def _getClipboardText(self):
		"""Return the clipboard text, or ``None`` if it holds no text."""
		try:
			return api.getClipData()
		except Exception:
			return None
