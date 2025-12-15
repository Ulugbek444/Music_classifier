from genius_api.genius import search_song
from genius_api.lyrics import fetch_lyrics


async def analyze_song(query: str):
    song = search_song(query)
    if not song:
        return {"error": "Song not found or lyrics unavailable"}

    lyrics = fetch_lyrics(song["artist"], song["title"])
    if not lyrics:
        return {"error": "Lyrics not available"}

    # обязательно ограничиваем длину
    lyrics = lyrics[:800]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                EMOTION_API_URL,
                json={"text": lyrics},
                timeout=60
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(
                        f"Emotion API error: {resp.status} | {error_text}"
                    )

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
