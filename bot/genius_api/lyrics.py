import requests


def fetch_lyrics(artist: str, title: str):
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None
    return r.json().get("lyrics")
