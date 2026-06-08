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
      category is present with the conversion command.
- [ ] The default gesture is **NVDA+shift+o**.
- [ ] The command can be reassigned to another gesture, and the new gesture
      works after saving.

## Convert selected text (single press)

With the direction set to `s2twp`:

- [ ] In an editable document, type `软件内存`, select it, and press
      **NVDA+shift+o once**. NVDA speaks **軟體記憶體**.
- [ ] The clipboard now contains **軟體記憶體** (paste with Ctrl+V to confirm).
- [ ] The **original selected text is unchanged** in the document (no in-place
      replacement).
- [ ] Select `头发` and press once → NVDA speaks **頭髮**.
- [ ] Select `发展` and press once → NVDA speaks **發展**.
- [ ] With nothing selected, press once → NVDA reports that there is no
      selection (no crash).

## Convert clipboard text (double press)

- [ ] Copy `简体字` to the clipboard (Ctrl+C). Press **NVDA+shift+o twice
      quickly**. NVDA speaks **簡體字** and the clipboard now holds **簡體字**.
- [ ] Copy `内存` to the clipboard and double-press → NVDA speaks **記憶體**.
- [ ] Confirm that a double press converts the **clipboard** (not the current
      selection): select some text, copy *different* text, then double-press;
      the **clipboard** text is the one that gets converted.
- [ ] With an empty / non-text clipboard, double-press → NVDA reports that the
      clipboard is empty (no crash).

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
