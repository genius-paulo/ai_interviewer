from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.models import Commands, SkillsData, Modes


async def main_keyboard() -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text=Commands.get_question_text),
         KeyboardButton(text=Commands.change_skills_text)],
        [KeyboardButton(text=Commands.profile_text),
         KeyboardButton(text=Commands.change_mode_text)],
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


async def skills_keyboard():
    skills_dict = SkillsData().model_dump()
    keyboard = InlineKeyboardMarkup()
    for skill_name, skill_value in skills_dict.items():
        keyboard.add(InlineKeyboardButton(text=skill_value, callback_data=skill_name))
    return keyboard


async def mode_keyboard():
    mode_dict = Modes().model_dump()
    keyboard = InlineKeyboardMarkup()
    for skill_name, skill_value in mode_dict.items():
        keyboard.add(InlineKeyboardButton(text=skill_value, callback_data=skill_name))
    return keyboard
