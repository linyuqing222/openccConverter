# Development

This add-on is built with the
[NVDA add-on template](https://github.com/nvaccess/AddonTemplate) and `scons`.

## Architecture

All conversion logic lives in
`addon/globalPlugins/openccConverter/opencc_core.py`, a module with **no
dependency on NVDA**, so it can be unit-tested with a plain Python interpreter.
The NVDA global plugin (`__init__.py`) only handles gestures, the settings panel,
speech, and the clipboard, delegating the actual conversion to the core. The
pure-Python [opencc-purepy](https://github.com/laisuk/opencc_purepy) engine (MIT)
and its OpenCC dictionaries (Apache-2.0) are vendored, unmodified, under
`addon/globalPlugins/openccConverter/_vendor/opencc_purepy/`.

## Run the tests

```sh
uv pip install pytest
python -m pytest tests/ -s -v
```

The `-s` flag shows the printed conversion evidence.

Manual QA steps that cannot be automated are listed in
[manual-test-checklist.md](manual-test-checklist.md).

## Build the add-on

```sh
uv pip install -e .          # install build dependencies (scons, Markdown, ...)
scons                        # produces openccConverter-<version>.nvda-addon
```

## Translations

User-visible strings go through NVDA's gettext (`_()`), and the add-on summary,
description, and changelog in `buildVars.py` are translatable too. Translations
live in `addon/locale/<lang>/LC_MESSAGES/nvda.po` and are compiled to `nvda.mo`
at build time; a translated manifest (summary/description/changelog) is also
generated per language. A Traditional Chinese (Taiwan), `zh_TW` translation is
included.

To update or add a translation:

```sh
scons pot                                  # regenerate openccConverter.pot
# new language:
msginit -i openccConverter.pot -o addon/locale/<lang>/LC_MESSAGES/nvda.po -l <lang>
# existing language (merge new/changed strings):
msgmerge -U addon/locale/<lang>/LC_MESSAGES/nvda.po openccConverter.pot
scons                                       # compiles nvda.mo into the add-on
```
