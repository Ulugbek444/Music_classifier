import requests
from bs4 import BeautifulSoup
import re


def trim_to_lyrics(text: str):
    """
    Оставляем текст, начиная с первого [Verse] / [Chorus] / [Intro]
    """
    match = re.search(r"\[(Verse|Chorus|Bridge|Intro|Outro)", text)

    if match:
        return text[match.start():].strip()

    # fallback — если вдруг тегов нет
    return text.strip()


def fetch_lyrics_from_url(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_containers = soup.select('div[data-lyrics-container="true"]')

    if not lyrics_containers:
        return None

    # берём текст, сохраняя переносы строк
    text = "\n".join(
        container.get_text("\n")
        for container in lyrics_containers
    )

    # # убираем [Verse], [Chorus], [Bridge] и т.д.
    # lyrics = re.sub(r"\[.*?]", "", lyrics)

    text = re.sub(r"\n{2,}", "\n", text)
    text = trim_to_lyrics(text)

    return text.strip()


# lyrics_test = fetch_lyrics_from_url(
#     "https://genius.com/Coldplay-fix-you-lyrics"
# )
# print(lyrics_test[:1200])