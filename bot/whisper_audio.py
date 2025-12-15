import aiohttp
import os

ML_API_BASE = os.getenv("ML_API_BASE", "http://localhost:8000")
WHISPER_API_URL = f"{ML_API_BASE}/transcribe"


print("Whisper URL:", WHISPER_API_URL)


async def transcribe_via_api(audio_path: str) -> str:
    async with aiohttp.ClientSession() as session:
        with open(audio_path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field(
                "file",
                f,
                filename="voice.ogg",
                content_type="audio/ogg"
            )

            async with session.post(WHISPER_API_URL, data=form, timeout=120) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(
                        f"Emotion API error: {resp.status} | {error_text}"
                    )
                data = await resp.json()
                return data["text"]
