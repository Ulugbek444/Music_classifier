from dotenv import load_dotenv
import os
import requests
load_dotenv()

GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")
GENIUS_API_URL = "https://api.genius.com/search"  # endpoint
# print(GENIUS_TOKEN[:10])  # sanity check


def search_song(query: str):
    # авторизация
    headers = {
        "Authorization": f"Bearer {GENIUS_TOKEN}",
        "User-Agent": "LyricsEmotionBot/1.0"
    }

    # строка, которую передаем
    params = {
        "q": query
    }

    response = requests.get(GENIUS_API_URL, headers=headers, params=params)  # get запрос
    response.raise_for_status()  # кидает exception при ошибке

    hits = response.json()["response"]["hits"]  # hits — список кандидатов, если ничего не нашли то None

    if not hits:
        return None

    song = hits[0]["result"]  # первый из кандидатов почти всегда нужный

    return {
        "title": song["title"],
        "artist": song["primary_artist"]["name"],
        "url": song["url"]
    }

# # тест
# song_test = search_song("Coldplay Fix You")
# print(song_test)
