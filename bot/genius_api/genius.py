import os
import lyricsgenius

genius = lyricsgenius.Genius(
    os.environ["GENIUS_ACCESS_TOKEN"],
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True
)


def search_song(query: str):
    song = genius.search_song(query)

    if not song:
        return None

    return {
        "title": song.title,
        "artist": song.artist
    }
