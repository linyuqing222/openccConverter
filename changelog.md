# Changelog

## [2.1.0](https://github.com/linyuqing222/openccConverter/compare/v2.0.0...v2.1.0) (2026-06-12)


### Features

* auto-translate the store changelog to zh_TW ([#13](https://github.com/linyuqing222/openccConverter/issues/13)) ([09cd565](https://github.com/linyuqing222/openccConverter/commit/09cd5654b6854aebe9ceb4a226503e2c78da0b43))
* pick the default conversion direction from NVDA's UI language ([#15](https://github.com/linyuqing222/openccConverter/issues/15)) ([10c2c17](https://github.com/linyuqing222/openccConverter/commit/10c2c175e19f43d82c372cf70b3068fbd475473f))


### Bug Fixes

* remove extra trailing newline in Claude workflow files ([#11](https://github.com/linyuqing222/openccConverter/issues/11)) ([73cee14](https://github.com/linyuqing222/openccConverter/commit/73cee142dc82bcb647bc6dbe7d6810500c43ed95))

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
