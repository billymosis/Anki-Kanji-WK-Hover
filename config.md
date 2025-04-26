# Configuration Options

This document describes all available configuration options for the Anki Kanji WK Hover add-on.

## Basic Options

### `kanji_filter` (string)

The name of the filter to use in your card templates. This is what you'll put before field names in your templates.

**Default:** `"my_kanji"`  
**Example usage in templates:** `{{my_kanji:Expression}}`

### `kanji_deck` (string)

The name of the deck containing your kanji information. The add-on will search this deck for kanji data.

**Default:** `"WaniKani Ultimate::Kanjis"`  
**Recommended deck:** [WaniKani Ultimate 2: Japanese Kanji](https://ankiweb.net/shared/info/369908962)

## Advanced Options

### `cache_size` (number)

The maximum number of kanji to keep in the memory cache. Higher values use more memory but reduce database lookups.

**Default:** `1000`

### `debug_mode` (boolean)

When enabled, detailed logs will be written to help troubleshoot issues.

**Default:** `false`

## Troubleshooting

If you're experiencing issues:

1. Enable `debug_mode` in the config
2. Restart Anki
3. Check the add-on log file in the add-on directory
4. If problems persist, please report them on [GitHub issues](https://github.com/billymosis/Anki-Kanji-WK-Hover/issues)

