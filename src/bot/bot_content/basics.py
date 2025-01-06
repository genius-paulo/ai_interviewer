from pydantic import BaseModel
from typing import Optional
from src.bot.bot_content import skills


class Commands:
    start = 'start'

    get_question_command = 'get_question'
    get_question_text = '❓️Получить вопрос'

    change_skills_command = 'change_skill'
    change_skills_text = '💪 Выбрать навык'

    profile_command = 'profile'
    profile_text = '👤 Мои навыки'

    change_mode_command = 'mode'
    change_mode_text = '⚙️ Выбрать режим интервью'

    another_question_text = '🔁 Другой вопрос'

    cancel_command = 'cancel'
    cancel_text = '🙅Отмена'


class Modes(BaseModel):
    all: str = 'all'
    specific: str = 'specific'
    worst: str = 'worst'


class User(BaseModel):
    id: Optional[int] = None
    tg_id: int
    mode: Optional[str] = Modes().all
    skill: Optional[str] = skills.Basic().short_name
