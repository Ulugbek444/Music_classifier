import os
import logging
import requests
from typing import Optional
import lyricsgenius

logger = logging.getLogger(__name__)

genius = lyricsgenius.Genius(
    os.environ["GENIUS_ACCESS_TOKEN"],
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True,
    verbose=False,
)


def search_song(query: str) -> Optional[dict[str, str]]:
    try:
        song = genius.search_song(query)
    except Exception:
        logger.warning("Genius search failed", exc_info=True)
        return None

    if not song:
        return None

    return {
        "title": song.title,
        "artist": song.artist,
    }
