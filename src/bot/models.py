from pydantic import BaseModel
from typing import Optional


class Commands:
    start = 'start'

    get_question_command = 'get_question'
    get_question_text = '❓️Получить вопрос'

    change_skills_command = 'change_skills'
    change_skills_text = '💪 Указать навыки'

    another_question_text = '🔁 Другой вопрос'

    cancel_command = 'cancel'
    cancel_text = '🙅Отмена'


class User(BaseModel):
    id: Optional[int] = None
    tg_id: int
    skills: Optional[str] = None
