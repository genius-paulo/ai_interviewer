from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from src.bot.models import Commands


async def main_keyboard() -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text=Commands.get_question_text),
         KeyboardButton(text=Commands.change_skills_text)],
        ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)
    return keyboard


async def question_keyboard() -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text=Commands.another_question_text),
         KeyboardButton(text=Commands.cancel_text)],
        ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)
    return keyboard
