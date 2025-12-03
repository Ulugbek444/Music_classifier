import uuid
import asyncio
from aiogram import Router, types, Bot, F

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from genius_api.analyze import analyze_song
from whisper_audio import transcribe_via_api
from config import EMOTION_RU
from gifs import like_keyboard, send_creator_sticker

from pathlib import Path

router = Router()

analysis_count: dict[int, int] = {}  # сколько анализов
creator_shown: set[int] = set()  # пользователи, которым фото уже показали


@router.message(Command("start"))
async def start(message: types.Message):
    text = (
        "🎵 *LyricMood Bot*\n\n"
        "Я анализирую *эмоцию песни* по её тексту.\n\n"
        "👉 Просто отправь:\n"
        "• название песни (английские)\n"
        "• *или* голосовое сообщение\n\n"
        "Я определю эмоцию: *joy, sadness, anger, fear, love или surprise* 💫"
    )

    await message.answer(text, parse_mode="Markdown")


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot):
    await message.answer("🎤 Распознаю голосовое сообщение...")

    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    ogg_path = temp_dir / f"{uuid.uuid4()}.ogg"

    await bot.download(
        message.voice.file_id,
        destination=ogg_path
    )

    audio_path = ogg_path.resolve()
    print("Audio exists:", audio_path.exists())
    print("Audio path:", audio_path)

    try:
        query = await transcribe_via_api(str(audio_path))
    except Exception as e:
        print("Whisper error:", e)
        await message.answer("❌ Не удалось распознать речь.")
        return
    finally:
        ogg_path.unlink(missing_ok=True)

    if len(query) < 3:
        await message.answer("❗ Не смог распознать название песни.")
        return

    await message.answer("🎧 Ищу песню и анализирую текст...")

    try:
        result = await analyze_song(query)
    except Exception as e:
        print("ANALYZE ERROR:", e)
        raise

    if "error" in result:
        await message.answer(
            "😕 Не смог найти эту песню\n\n"
            "Попробуй:\n"
            "• написать *название + исполнитель*\n"
            "• или сказать чуть чётче 🎤",
            parse_mode="Markdown"
        )
        return

    emotion_text = EMOTION_RU.get(result["emotion"], result["emotion"])
    confidence_pct = int(result["confidence"] * 100)

    response = (
        f"🎵 *{result['title']}* — *{result['artist']}*\n\n"
        f"🧠 Основная эмоция: *{emotion_text}*\n"
        f"📊 Уверенность: *{confidence_pct}%*\n\n"
        f"ℹ️ _Это эмоция лирического героя,_\n"
        f"_а не общее настроение песни._"
    )

    await message.answer(response, parse_mode="Markdown")

    user_id = message.from_user.id
    analysis_count[user_id] = analysis_count.get(user_id, 0) + 1

    if analysis_count[user_id] == 2 and user_id not in creator_shown:
        creator_shown.add(user_id)

        # ✅ ПАУЗА
        await asyncio.sleep(5)

        # ✅ ПОТОМ стикер
        await send_creator_sticker(message)


@router.message()
async def handle_text(message: types.Message):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer(
            "❗ Пожалуйста, отправь *название песни или исполнителя*.\n\n"
            "Например:\n"
            "• Coldplay Fix You\n"
            "• Imagine Dragons",
            parse_mode="Markdown"
        )
        return

    query = message.text.strip()

    await message.answer("🎧 Ищу песню и анализирую текст...")

    try:
        result = await analyze_song(query)
    except Exception as e:
        print("ANALYZE ERROR:", e)
        raise

    if "error" in result:
        await message.answer(
            "😕 Не смог найти эту песню\n\n"
            "Попробуй:\n"
            "• написать *название + исполнитель*\n"
            "• или сказать чуть чётче 🎤",
            parse_mode="Markdown"
        )
        return

    emotion_text = EMOTION_RU.get(result["emotion"], result["emotion"])
    confidence_pct = int(result["confidence"] * 100)

    response = (
        f"🎵 *{result['title']}* — *{result['artist']}*\n\n"
        f"🧠 Основная эмоция: *{emotion_text}*\n"
        f"📊 Уверенность: *{confidence_pct}%*\n\n"
        f"ℹ️ _Это эмоция лирического героя,_\n"
        f"_а не общее настроение песни._"
    )

    await message.answer(response, parse_mode="Markdown")

    user_id = message.from_user.id
    analysis_count[user_id] = analysis_count.get(user_id, 0) + 1

    if analysis_count[user_id] == 2 and user_id not in creator_shown:
        creator_shown.add(user_id)

        # ✅ ПАУЗА
        await asyncio.sleep(5)

        # ✅ ПОТОМ стикер
        await send_creator_sticker(message)


@router.callback_query()
async def handle_creator_buttons(callback: CallbackQuery):

    # ✅ 1. СРАЗУ убираем кнопки
    await callback.message.edit_reply_markup(reply_markup=None)

    # ✅ 2. Реакция
    if callback.data == "creator_like":
        await callback.message.answer_sticker(
            "CAACAgQAAxkBAAOAaSx2pgjit-wl8DtEhIOfOWh9e5UAAsUiAAK9t3FTihX9KRsEOAI2BA"
        )
        await callback.message.answer("Спасибооооо 🫶")

    elif callback.data == "creator_dislike":
        await callback.message.answer_sticker(
            "CAACAgIAAxkBAAODaSx6SO-s-4KzQo-WiE1iG0z32hcAAgJxAALtg0BJp3gf5gnmx7Y2BA"
        )
        await callback.message.answer("Я тебя запомнил… 😈")

    # ✅ 3. Закрываем callback (обязательно)
    await callback.answer()
