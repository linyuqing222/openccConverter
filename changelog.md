# Changelog

## 1.2.0

- Replaced the bundled conversion engine with the faster pure-Python
  [opencc-purepy](https://github.com/laisuk/opencc_purepy) (about twice as fast
  on large text); conversions remain fully offline. Output for the default
  direction and every Taiwan-standard direction is unchanged. A couple of
  non-default directions (`s2t`, `tw2sp`) may now produce slightly different but
  equivalent characters, reflecting the newer OpenCC dictionary data.
