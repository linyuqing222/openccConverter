# OpenCC Converter

Offline Simplified ⇄ Traditional Chinese conversion for [NVDA](https://www.nvaccess.org/).

OpenCC Converter converts the **selected text** or the **clipboard text** between
Simplified and Traditional Chinese, speaks the result, and copies it to the
clipboard. It runs **completely offline** — all dictionaries are bundled, so no
internet connection is needed.

## Features

- Convert the **selected text** or the **clipboard text** from a quick command
  layer, and **swap** the conversion direction on the fly.
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

Press **`NVDA+shift+c`** to open the command layer (you'll hear a tone), then
press one key:

- **`s`** — convert the **selected text**.
- **`c`** — convert the **clipboard text**.
- **`w`** — **swap** the conversion direction.

Any other key dismisses the layer. The full converted text is placed on the
clipboard; your document is never modified. The result is then spoken: short
results in full, large results as a character count (so a huge conversion isn't
read out in its entirety). A progress tone repeats while a long conversion is
still running — handy for large inputs such as a whole book.

Swapping the direction (**`w`**) announces the new direction and, if you have
text selected, converts that selection in the new direction. You can reassign
the layer gesture in NVDA's *Input Gestures* dialog, under the **OpenCC
Converter** category.

## Settings

Choose the conversion direction in
*NVDA menu → Preferences → Settings → OpenCC Converter*. Your choice is saved and
persists across restarts. The default is **Simplified → Traditional Chinese
(Taiwan, with phrases)**, which produces idiomatic Taiwanese vocabulary (for
example 软件 → 軟體, 内存 → 記憶體).

## License

OpenCC Converter is licensed under the **GNU General Public License, version 2 or
later** (see [COPYING.txt](COPYING.txt)). It bundles, unmodified, the pure-Python
[opencc-purepy](https://github.com/laisuk/opencc_purepy) engine (**MIT License**)
together with [OpenCC](https://github.com/BYVoid/OpenCC) dictionary data (**Apache
License 2.0**).

Developers: see [DEVELOPMENT.md](DEVELOPMENT.md) for building, testing, and
translating.
