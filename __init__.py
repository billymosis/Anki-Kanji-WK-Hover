import os
import time
import logging
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from functools import lru_cache

# Anki dependencies
from anki import hooks
from anki.notes import Note
from anki.template import TemplateRenderContext, TemplateRenderOutput
from aqt import mw
from aqt.utils import showWarning

# Custom module imports
from .static import html, css
from .util import is_kanji

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "kanji_plugin.log")
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Load configuration
try:
    config = mw.addonManager.getConfig(__name__)
    KANJI_FILTER = config.get("kanji_filter", "my_kanji")
    KANJI_DECK = config.get("kanji_deck", "WaniKani Ultimate::Kanjis")
    CACHE_SIZE = config.get("cache_size", 1000)
    DEBUG_MODE = config.get("debug_mode", False)

    if DEBUG_MODE:
        logger.setLevel(logging.DEBUG)

    logger.info(
        f"Plugin initialized with config: filter={KANJI_FILTER}, deck={KANJI_DECK}"
    )
except Exception as e:
    # Provide default values if config loading fails
    logger.error(f"Error loading config: {str(e)}")
    KANJI_FILTER = "my_kanji"
    KANJI_DECK = "WaniKani Ultimate::Kanjis"
    CACHE_SIZE = 1000
    DEBUG_MODE = False

    if mw:
        showWarning(
            f"Kanji Plugin: Error loading configuration. Using default settings."
        )


class SubjectType(str, Enum):
    """Enum for subject types in the Kanji database."""

    KANJI = "kanji"
    VOCABULARY = "vocabulary"
    RADICAL = "radical"


class SubjectError(Enum):
    """Enum for possible errors when retrieving subjects."""

    INVALID_TOKEN = 1
    INVALID_SLUG = 2
    INVALID_ID = 3
    BAD_CONNECTION = 4
    NO_RESULTS = 5
    DECK_NOT_FOUND = 6


class KanjiData:
    """Data class to store kanji information."""

    def __init__(self, data: Dict[str, str]):
        self.character = data.get("character", "")
        self.meaning = data.get("meaning", "")
        self.onyomi = data.get("onyomi", "")
        self.kunyomi = data.get("kunyomi", "")
        self.meaning_mnemonic = data.get("meaning_mnemonic", "")
        self.reading_mnemonic = data.get("reading_mnemonic", "")
        self.radicals = data.get("radicals", "")

    def is_valid(self) -> bool:
        """Check if the kanji data is valid and usable."""
        return bool(self.character and self.meaning)


def query_by_field_name(
    field_name: str, search_term: str, deck_name: str
) -> List[Note]:
    """
    Search for notes using field names within a specified deck.

    Args:
        field_name: The name of the field to search in
        search_term: The term to search for
        deck_name: The name of the deck to search in

    Returns:
        A list of matching notes
    """
    notes = []
    try:
        if not mw or not mw.col:
            logger.error("Collection not available")
            return notes

        # First check if the deck exists
        deck_id = mw.col.decks.id(deck_name)
        if not deck_id:
            logger.warning(f"Deck not found: {deck_name}")
            return notes

        # Perform the search
        query = f'deck:"{deck_name}" {field_name}:*{search_term}*'
        logger.debug(f"Executing query: {query}")
        note_ids = mw.col.find_notes(query)

        # Get the matching notes
        for nid in note_ids:
            note = mw.col.get_note(nid)
            if field_name in note and search_term in note[field_name]:
                notes.append(note)

        logger.debug(
            f"Found {len(notes)} notes matching '{search_term}' in {field_name}"
        )
        return notes

    except Exception as e:
        logger.error(f"Error in query_by_field_name: {str(e)}")
        return notes


@lru_cache(maxsize=CACHE_SIZE)
def get_subject_by_slug(
    subject_type: SubjectType, slug: str
) -> Union[Dict[str, str], SubjectError]:
    """
    Retrieve subject information by its slug (character).
    Uses caching to improve performance.

    Args:
        subject_type: The type of subject (kanji, vocabulary, radical)
        slug: The unique identifier for the subject (character for kanji)

    Returns:
        Dictionary with subject data or SubjectError
    """
    logger.debug(f"Looking up: type={subject_type}, slug={slug}")

    if not slug:
        return SubjectError.INVALID_SLUG

    # Currently only kanji lookups are supported
    if subject_type != SubjectType.KANJI:
        logger.warning(f"Unsupported subject type: {subject_type}")
        return SubjectError.INVALID_SLUG

    # Check for deck existence
    if not mw.col.decks.id(KANJI_DECK):
        logger.error(f"Kanji deck not found: {KANJI_DECK}")
        return SubjectError.DECK_NOT_FOUND

    # Search for the kanji in the specified deck
    start_time = time.time()
    notes = query_by_field_name("Kanji", slug, KANJI_DECK)
    query_time = time.time() - start_time

    if not notes:
        logger.info(f"No results found for kanji: {slug}")
        return SubjectError.NO_RESULTS

    # Use the first matching note
    note = notes[0]

    arr = note.tags
    level = "0"
    for a in arr:
        if "level" in a:
            split = a.split("level")
            if len(split) > 0:
                level = split[1]

    # Extract kanji data - adjust indices based on your note type
    try:
        kanji_data = {
            "character": slug,
            "meaning": note.fields[1],
            "onyomi": note.fields[2],
            "kunyomi": note.fields[3],
            "meaning_mnemonic": note.fields[8] + "</br></br>" + note.fields[9],
            "reading_mnemonic": note.fields[10] + "</br></br>" + note.fields[11],
            "radicals": note.fields[4] + "|" + note.fields[6],
            "level": level,
        }

        logger.debug(f"Retrieved kanji data for {slug} in {query_time:.3f}s")
        return kanji_data

    except IndexError as e:
        logger.error(f"Field index error for kanji {slug}: {str(e)}")
        return SubjectError.INVALID_SLUG


def prepare_kanji_hint(text: str) -> str:
    """
    Process text and add hover tooltips for each kanji character.

    Args:
        text: The input text to process

    Returns:
        HTML-formatted text with kanji tooltips
    """
    if not text:
        return text

    output = ""
    kanji_count = 0
    error_count = 0

    start_time = time.time()

    for char in text:
        # Skip non-kanji characters
        if not is_kanji(char):
            output += char
            continue

        kanji_count += 1
        kanji_data = get_subject_by_slug(SubjectType.KANJI, char)

        # Handle errors or missing data
        if isinstance(kanji_data, SubjectError):
            logger.debug(f"Kanji lookup error for {char}: {kanji_data}")
            error_count += 1
            output += char
            continue

        # Format the HTML tooltip
        output += html.format(
            text=char,
            link=f"https://wanikani.com/kanji/{char}",
            meaning=kanji_data["meaning"],
            component_list=kanji_data["radicals"],
            meaning_mnemonic=kanji_data["meaning_mnemonic"],
            reading_mnemonic=kanji_data["reading_mnemonic"],
            onyomi=kanji_data["onyomi"],
            kunyomi=kanji_data["kunyomi"],
            level=kanji_data["level"],
        )

    process_time = time.time() - start_time
    if kanji_count > 0:
        logger.debug(
            f"Processed {kanji_count} kanji ({error_count} errors) in {process_time:.3f}s"
        )

    return output


def on_field_filter(
    text: str, field_name: str, filter_name: str, context: TemplateRenderContext
) -> str:
    """
    Handle Anki field filtering for kanji hints.
    This function is called by Anki when processing card templates.

    Args:
        text: The field text
        field_name: The name of the field
        filter_name: The name of the filter being applied
        context: The render context

    Returns:
        Processed text with kanji hints if the filter matches
    """
    # Only process if our filter is being used
    if filter_name != KANJI_FILTER:
        return text

    try:
        return prepare_kanji_hint(text)
    except Exception as e:
        logger.error(f"Error in kanji hint filter: {str(e)}")
        # Return original text on error to ensure cards still render
        return text


def on_card_render(
    output: TemplateRenderOutput, context: TemplateRenderContext
) -> None:
    """
    Add CSS to rendered cards.
    This function is called by Anki after a card is rendered.

    Args:
        output: The rendered card output
        context: The render context
    """
    try:
        # Apply CSS to both question and answer sides
        headers = f"<style>{css}</style>"
        output.question_text = headers + output.question_text
        output.answer_text = headers + output.answer_text
    except Exception as e:
        logger.error(f"Error injecting CSS: {str(e)}")


def get_deck_contents(deck_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieve all cards and their notes in a specified deck.
    Useful for debugging and diagnostics.

    Args:
        deck_name: The name of the deck to get contents for

    Returns:
        List of dictionaries with card and note information, or None if deck not found
    """
    if not mw or not mw.col:
        logger.error("Collection not available")
        return None

    deck_id = mw.col.decks.id(deck_name)
    if not deck_id:
        logger.warning(f"Deck not found: {deck_name}")
        return None

    try:
        card_ids = mw.col.decks.cids(deck_id)
        deck_contents = []

        for card_id in card_ids:
            card = mw.col.get_card(card_id)
            note = card.note()

            deck_contents.append(
                {
                    "card_id": card_id,
                    "note_id": note.id,
                    "fields": note.fields,
                    "note_type": note.note_type()["name"],
                    "card_template": card.template()["name"],
                }
            )

        return deck_contents

    except Exception as e:
        logger.error(f"Error retrieving deck contents: {str(e)}")
        return None


def clear_caches() -> None:
    """Clear all function caches."""
    get_subject_by_slug.cache_clear()
    logger.info("Caches cleared")


# Register with Anki hooks
def init_plugin():
    """Initialize the plugin by registering necessary hooks."""
    try:
        hooks.field_filter.append(on_field_filter)
        hooks.card_did_render.append(on_card_render)
        logger.info("Kanji plugin initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize plugin: {str(e)}")


# Initialize the plugin
init_plugin()
