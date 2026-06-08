# OpenCC Converter

Offline Simplified ⇄ Traditional Chinese conversion for [NVDA](https://www.nvaccess.org/).

OpenCC Converter converts the **selected text** or the **clipboard text** between
Simplified and Traditional Chinese, speaks the result, and copies it to the
clipboard. It runs **completely offline** — all dictionaries are bundled, so no
internet connection is needed.

## Features

- Convert the **selected text** with a single press, or the **clipboard text** by
  pressing **twice quickly**.
- The result is **spoken** and **copied to the clipboard**; your original text is
  **never replaced in place**.
- Convert in either direction — Simplified → Traditional or Traditional →
  Simplified, including Taiwan-standard and phrase-level variants — selectable in
  the add-on settings.

## Requirements

- NVDA **2023.1** or later (last tested with NVDA **2026.1**).

## Installation

1. Download `openccConverter-<version>.nvda-addon`.
2. Open it with NVDA (or use *NVDA menu → Tools → Add-on store → Install from
   external source*) and follow the prompts.
3. Restart NVDA when asked.

## Usage

The command is bound to **`NVDA+shift+o`** by default:

- **Press once** — converts the **selected text**.
- **Press twice quickly** — converts the **clipboard text** instead.

In both cases the result is spoken and placed on the clipboard; your document is
not modified. You can change the gesture in NVDA's *Input Gestures* dialog, under
the **OpenCC Converter** category.

## Settings

Choose the conversion direction in
*NVDA menu → Preferences → Settings → OpenCC Converter*. Your choice is saved and
persists across restarts. The default is **Simplified → Traditional Chinese
(Taiwan, with phrases)**, which produces idiomatic Taiwanese vocabulary (for
example 软件 → 軟體, 内存 → 記憶體).

## License

OpenCC Converter is licensed under the **GNU General Public License, version 2 or
later** (see [COPYING.txt](COPYING.txt)). It bundles, unmodified, the pure-Python
[opencc-python-reimplemented](https://github.com/yichen0831/opencc-python) engine
and [OpenCC](https://github.com/BYVoid/OpenCC) dictionary data, both under the
**Apache License 2.0**.

Developers: see [DEVELOPMENT.md](DEVELOPMENT.md) for building, testing, and
translating.
