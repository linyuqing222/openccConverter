# Manual test checklist — OpenCC Converter

These checks must be run inside a real NVDA installation, because they exercise
behaviour (gestures, speech, the clipboard, the settings GUI) that cannot be
covered by the automated `pytest` suite. The offline conversion logic itself is
verified automatically — see `tests/` and run `python -m pytest tests/ -s -v`.

## Environment

- NVDA version: ____________ (target: 2026.1; minimum supported: 2023.1)
- OpenCC Converter version: ____________
- Tester / date: ____________

## Setup

- [ ] Build the add-on (`scons`) and install
      `openccConverter-<version>.nvda-addon` into NVDA.
- [ ] Restart NVDA when prompted.
- [ ] Confirm no errors appear in the NVDA log (NVDA+F1) on startup related to
      `openccConverter`.

## Settings panel

- [ ] Open *NVDA menu → Preferences → Settings*. An **OpenCC Converter**
      category is present.
- [ ] The category contains a **Conversion direction** combo box listing all
      six directions: s2t, s2tw, s2twp, t2s, tw2s, tw2sp.
- [ ] The default selection on a fresh install is
      **Simplified → Traditional Chinese (Taiwan, with phrases)** (`s2twp`).
- [ ] Change the direction, press **OK**, reopen Settings, and confirm the new
      direction is remembered (persisted to `config.conf`).
- [ ] Restart NVDA and confirm the chosen direction is still selected.

## Input Gestures

- [ ] Open *NVDA menu → Preferences → Input Gestures*. An **OpenCC Converter**
      category is present, listing the command-layer gesture and (unassigned by
      default) the convert-selection, convert-clipboard and swap-direction
      commands.
- [ ] The default gesture for the command layer is **NVDA+shift+c**.
- [ ] The layer gesture can be reassigned to another gesture, and the new
      gesture works after saving.

## Command layer

- [ ] Press **NVDA+shift+c**: a short tone sounds (the layer is armed).
- [ ] While armed, press an **unrelated key** (e.g. `x` or an arrow): a low tone
      sounds, the layer is dismissed, and no conversion happens.
- [ ] After dismissing, normal typing/navigation works again (the layer does not
      stay stuck on).

## Convert selected text (layer, then `s`)

With the direction set to `s2twp`:

- [ ] In an editable document, type `软件内存`, select it, press
      **NVDA+shift+c** then **`s`**. NVDA speaks **軟體記憶體**.
- [ ] The clipboard now contains **軟體記憶體** (paste with Ctrl+V to confirm).
- [ ] The **original selected text is unchanged** in the document (no in-place
      replacement).
- [ ] Select `头发`, press the layer then `s` → NVDA speaks **頭髮**.
- [ ] Select `发展`, press the layer then `s` → NVDA speaks **發展**.
- [ ] With nothing selected, press the layer then `s` → NVDA reports that there
      is no selection (no crash).

## Convert clipboard text (layer, then `c`)

- [ ] Copy `简体字` to the clipboard (Ctrl+C). Press **NVDA+shift+c** then
      **`c`**. NVDA speaks **簡體字** and the clipboard now holds **簡體字**.
- [ ] Copy `内存`, press the layer then `c` → NVDA speaks **記憶體**.
- [ ] Confirm `c` converts the **clipboard** (not the current selection): select
      some text, copy *different* text, then press the layer + `c`; the
      **clipboard** text is the one that gets converted.
- [ ] With an empty / non-text clipboard, press the layer then `c` → NVDA
      reports that the clipboard is empty (no crash).

## Swap direction (layer, then `w`)

- [ ] Set direction to `s2twp`. Select `軟體`, press **NVDA+shift+c** then
      **`w`**. NVDA announces the new direction
      (**Traditional Chinese (Taiwan) → Simplified Chinese (with phrases)**) and
      then speaks **软件** (the selection converted in the new direction).
- [ ] Open Settings → the **Conversion direction** now shows the swapped
      direction (swap and the panel share the same setting).
- [ ] Press the layer + `w` again with no selection → NVDA only announces the
      direction (back to `s2twp`); it does **not** report "no selection".
- [ ] Swapping twice returns to the original direction.

## Progress tone and large inputs

- [ ] Convert any text: a short tone sounds the moment conversion starts.
- [ ] Copy a **whole novel** (~1 MB, hundreds of thousands of characters) to the
      clipboard, then press the layer + `c`. While it converts (several seconds):
  - [ ] A progress tone repeats roughly once per second.
  - [ ] NVDA stays responsive (you can still arrow around / read elsewhere).
  - [ ] On completion NVDA announces a count, e.g. **"Converted and copied
        912345 characters to the clipboard"** — it does **not** read the whole
        novel aloud.
  - [ ] Pasting (Ctrl+V) elsewhere yields the **full converted text**.
- [ ] Convert a **short** selection/clipboard (a word or sentence) → NVDA speaks
      the converted text itself (no character-count summary).
- [ ] Trigger another conversion **while a long one is still running** → the new
      trigger is ignored (no overlapping conversion, no crash).

## Direction-sensitive behaviour

- [ ] Set direction to `s2tw`, convert `软件` → NVDA speaks **軟件**.
- [ ] Set direction to `s2twp`, convert `软件` → NVDA speaks **軟體**.
      (Confirms the same input differs between `s2tw` and `s2twp`.)
- [ ] Set direction to `t2s`, convert `軟體` → NVDA speaks **软体**.

## Offline guarantee

- [ ] Disconnect from the network entirely, then repeat one conversion from each
      of the two sections above. Conversion still works (everything is bundled;
      no network access).

## Cleanup

- [ ] Disable/remove the add-on and confirm the **OpenCC Converter** category
      disappears from both Settings and Input Gestures, with no errors in the
      log.
