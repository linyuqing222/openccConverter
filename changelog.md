# Changelog

## [2.0.0](https://github.com/linyuqing222/openccConverter/compare/v1.0.1...v2.0.0) (2026-06-10)


### ⚠ BREAKING CHANGES

* require NVDA 2024.1 ([#6](https://github.com/linyuqing222/openccConverter/issues/6))

### Miscellaneous

* require NVDA 2024.1 ([#6](https://github.com/linyuqing222/openccConverter/issues/6)) ([d85212b](https://github.com/linyuqing222/openccConverter/commit/d85212bd659b8c0faf4893852b2281fe9f88a7cc))

## [1.0.1](https://github.com/linyuqing222/openccConverter/compare/v1.0.0...v1.0.1) (2026-06-09)


### Documentation

* add zh_TW readme and trim dev-only docs ([#3](https://github.com/linyuqing222/openccConverter/issues/3)) ([623b136](https://github.com/linyuqing222/openccConverter/commit/623b136fac538540665c0d9c2f10cb840e4f4f34))

## 1.0.0

- First release.
- Offline Simplified ⇄ Traditional Chinese conversion of the selected text or
  the clipboard, using a bundled OpenCC engine; no internet connection needed.
- Command layer: press NVDA+shift+c, then s (selection), c (clipboard) or
  w (swap direction).
- The result is copied to the clipboard and spoken; very large results are
  announced as a character count, and a progress tone sounds while converting.
- Configurable conversion direction in the add-on settings.
