# OpenCC Converter

Offline Simplified ⇄ Traditional Chinese conversion for [NVDA](https://www.nvaccess.org/).

OpenCC Converter converts the **selected text** or the **clipboard text**
between Simplified and Traditional Chinese, speaks the result, and copies it to
the clipboard. The conversion runs **completely offline** using a bundled,
pure-Python [OpenCC](https://github.com/BYVoid/OpenCC) engine
([opencc-python-reimplemented](https://github.com/yichen0831/opencc-python)),
together with its dictionaries — no internet connection and no C extension are
required.

## Features

- Convert the **currently selected text** with a single press of the command.
- Convert the **clipboard text** by pressing the command **twice quickly**.
- The result is **spoken** (and brailled) and **copied to the clipboard**.
  The original text is **never replaced in place**.
- Six configurable conversion directions:

  | Code    | Direction                                                        |
  | ------- | ---------------------------------------------------------------- |
  | `s2t`   | Simplified → Traditional Chinese                                 |
  | `s2tw`  | Simplified → Traditional Chinese (Taiwan)                        |
  | `s2twp` | Simplified → Traditional Chinese (Taiwan, with phrases) *(default)* |
  | `t2s`   | Traditional → Simplified Chinese                                 |
  | `tw2s`  | Traditional Chinese (Taiwan) → Simplified Chinese                |
  | `tw2sp` | Traditional Chinese (Taiwan) → Simplified Chinese (with phrases) |

- Fully offline. All dictionaries are bundled with the add-on.

## Requirements

- NVDA **2023.1** or later (last tested with NVDA **2026.1**).

## Installation

1. Download `openccConverter-<version>.nvda-addon`.
2. Open it with NVDA (or use *NVDA menu → Tools → Add-on store → Install from
   external source*), and follow the prompts.
3. Restart NVDA when asked.

## Usage

The add-on registers one command, by default bound to **`NVDA+shift+o`**:

- **Press once** — converts the **selected text**.
- **Press twice quickly** — converts the **clipboard text** instead.

In both cases the converted text is spoken and placed on the clipboard; your
document is not modified.

The gesture can be changed in NVDA's *Input Gestures* dialog, under the
**OpenCC Converter** category.

## Settings

The conversion direction is configured in
*NVDA menu → Preferences → Settings → OpenCC Converter*. The selected direction
is saved in NVDA's configuration (`config.conf`) and persists across restarts.
The default direction is `s2twp` (Simplified → Traditional, Taiwan, with
phrases), which produces idiomatic Taiwanese vocabulary (for example
软件 → 軟體, 内存 → 記憶體).

## How it works

All conversion logic lives in `opencc_core.py`, a module with **no dependency on
NVDA**, so it can be unit-tested with a plain Python interpreter. The NVDA
global plugin (`__init__.py`) only handles gestures, the settings panel, speech,
and the clipboard, delegating the actual conversion to the core.

## Development

This project is built from the
[NVDA add-on template](https://github.com/nvaccess/AddonTemplate).

### Run the tests

```sh
uv pip install pytest
python -m pytest tests/ -s -v
```

The `-s` flag shows the printed conversion evidence.

### Build the add-on

```sh
uv pip install -e .          # install build dependencies (scons, Markdown, ...)
scons                        # produces openccConverter-<version>.nvda-addon
```

### Translations

User-visible strings go through NVDA's gettext (`_()`), and the add-on summary,
description, and changelog in `buildVars.py` are translatable too. Translations
live in `addon/locale/<lang>/LC_MESSAGES/nvda.po` and are compiled to `nvda.mo`
at build time; a translated manifest (summary/description/changelog) is also
generated per language.

A **Traditional Chinese (Taiwan), `zh_TW`** translation is included.

To update or add a translation:

```sh
scons pot                                  # regenerate openccConverter.pot
# new language:
msginit -i openccConverter.pot -o addon/locale/<lang>/LC_MESSAGES/nvda.po -l <lang>
# existing language (merge new/changed strings):
msgmerge -U addon/locale/<lang>/LC_MESSAGES/nvda.po openccConverter.pot
scons                                       # compiles nvda.mo into the add-on
```

## License

OpenCC Converter is licensed under the **GNU General Public License, version 2
or later**. See [COPYING.txt](COPYING.txt) for the full GPL v2 text.

This add-on bundles, unmodified, the pure-Python
[opencc-python-reimplemented](https://github.com/yichen0831/opencc-python)
engine and the [OpenCC](https://github.com/BYVoid/OpenCC) dictionary data, both
licensed under the **Apache License 2.0**. The Apache License is included with
the bundled engine at
`addon/globalPlugins/openccConverter/_vendor/opencc/LICENSE.txt`, and the
related attribution notice at `.../_vendor/opencc/NOTICE.txt`. The Apache
License 2.0 is compatible with GPL v3, which is why this add-on is offered under
GPL v2 *or later* rather than GPL v2 only.
