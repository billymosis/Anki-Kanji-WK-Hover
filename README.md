# Anki Kanji WK Hover

An Anki add-on that provides interactive kanji tooltips when hovering over Japanese characters. When you hover over kanji characters in your Anki cards, you'll see helpful information including meanings, readings, mnemonics, and radicals.

![Kanji Hover Example](/images/screenshot.png)

## Features

- 🔍 **Instant Kanji Information**: See meanings, readings, and mnemonics without leaving your review session
- 🚀 **Performance Optimized**: Efficient caching system for fast lookups
- 🧩 **Works with WaniKani Format**: Designed to work with WaniKani-style kanji decks
- ⚙️ **Customizable**: Change the filter name, tooltip appearance, and more

## Installation

### Manual Installation from GitHub

1. Download this repository as a ZIP file
2. Extract the ZIP file
3. Place the extracted folder in your Anki add-ons folder:
   - Windows: `%APPDATA%\Anki2\addons21\`
   - Mac: `~/Library/Application Support/Anki2/addons21/`
   - Linux: `~/.local/share/Anki2/addons21/`
4. Rename the folder to `anki_kanji_wk_hover` or another simple name without spaces
5. Restart Anki

## Setup

### Required Kanji Deck

This add-on is designed to work with the [WaniKani Ultimate 2: Japanese Kanji](https://ankiweb.net/shared/info/369908962) deck. Please install this deck before using the add-on.

### Adding the Filter to Your Cards

To add hover tooltips to kanji in your cards:

1. Go to Browse → select a note type → Cards...
2. Add the filter to any field where you want kanji tooltips to appear:
   ```
   {{my_kanji:FieldName}}
   ```
   Where `my_kanji` is the filter name (configurable) and `FieldName` is the field containing Japanese text.

## Configuration

You can configure the add-on by going to Tools → Add-ons → select "Anki Kanji WK Hover" → Config.

### Options

- `kanji_filter`: The name of the filter to use in your card templates (default: `my_kanji`)
- `kanji_deck`: The name of the deck containing kanji data (default: `WaniKani Ultimate::Kanjis`)
- `cache_size`: Maximum number of kanji to keep in memory cache (default: `1000`)
- `debug_mode`: Enable detailed logging for troubleshooting (default: `false`)

### Styling

The HTML/CSS styling of the tooltips can be customized by:

1. Editing `static.py` in the add-on directory directly
2. Adding custom CSS for the tooltip classes in your card templates

## Troubleshooting

If the tooltips are not appearing:

1. Make sure you installed the required WaniKani kanji deck
2. Verify that the kanji deck name in the configuration matches your installed deck
3. Check that you're using the correct filter syntax in your card templates
4. Look for errors in the Anki debug console (Help → About → Copy Debug Info)

## Credits

- Original creator: Billy Priambodo
- Inspired by [Anki-WaniKani-Hints](https://github.com/MattWeinberg24/Anki-WaniKani-Hints) by Matt Weinberg
- Works with [WaniKani Ultimate 2: Japanese Kanji](https://ankiweb.net/shared/info/369908962) by WaniKani Community

## License

This project is licensed under the MIT License - see the LICENSE file for details.
