import os
import lyricsgenius
from dotenv import load_dotenv

load_dotenv()

GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

print("GENIUS_ACCESS_TOKEN exists:",
      "GENIUS_ACCESS_TOKEN" in os.environ)

genius = lyricsgenius.Genius(
    GENIUS_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True
)


def search_song(query: str):
    song = genius.search_song(query)

    if not song or not song.lyrics:
        return None

    return {
        "title": song.title,
        "artist": song.artist,
        "lyrics": song.lyrics
    }
