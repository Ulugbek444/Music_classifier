import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from tg_bot import router  # или твой файл с router

os.environ["PATH"] += r";C:\ffmpeg\bin"
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Фатальная ошибка при запуске бота")

