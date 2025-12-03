import aiohttp
import logging
import os
from genius_api.genius import search_song
from genius_api.lyrics import fetch_lyrics_from_url

ML_API_BASE = os.getenv("ML_API_BASE", "http://localhost:8000")
EMOTION_API_URL = f"{ML_API_BASE}/predict-emotion"


async def analyze_song(query: str):
    song = search_song(query)
    if not song:
        return {"error": "Song not found"}

    lyrics = fetch_lyrics_from_url(song["url"])
    if not lyrics:
        return {"error": "Lyrics not available"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                EMOTION_API_URL,
                json={"text": lyrics},
                timeout=30
            ) as resp:

                if resp.status != 200:
                    raise RuntimeError("Emotion API error")

                data = await resp.json()

        return {
            "title": song["title"],
            "artist": song["artist"],
            "emotion": data["emotion"],
            "confidence": round(data["confidence"], 3)
        }

    except Exception:
        logging.exception("Emotion prediction failed")
        return {"error": "Prediction error"}


# тест
# result = analyze_song("Coldplay Fix You")
# print(result)
