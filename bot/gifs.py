from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile


def like_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Like", callback_data="creator_like"),
            InlineKeyboardButton(text="👎 Dislike", callback_data="creator_dislike"),
        ]
    ])


async def send_creator_sticker(message: Message):
    await message.answer_sticker(
        sticker="CAACAgQAAxkBAAN9aSx2f9jdHdu5GOxh25WJFafShwEAAr4dAALIgnBTQt6NW-ZDRC02BA"
    )

    await message.answer(
        "😎 Лайк создателю?",
        reply_markup=like_keyboard()
    )
