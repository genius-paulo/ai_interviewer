from pydantic import BaseModel
from typing import Optional


class Commands:
    start = 'start'

    get_question_command = 'get_question'
    get_question_text = '❓️Получить вопрос'

    change_skills_command = 'change_skill'
    change_skills_text = '💪 Выбрать навык'

    profile_command = 'profile'
    profile_text = '👤 Профиль'

    change_mode_command = 'mode'
    change_mode_text = '⚙️ Выбрать режим интервью'

    another_question_text = '🔁 Другой вопрос'

    cancel_command = 'cancel'
    cancel_text = '🙅Отмена'


class SkillsData(BaseModel):
    basic: str = 'Основы Python'
    oop: str = 'ООП'
    standard_lib: str = 'Стандартная библиотека'
    async_prog: str = 'Асинхронное программирование'
    db: str = 'Работа с базами данных'
    web: str = 'Веб-фреймворки и RESTful API'
    test: str = 'Тестирование'
    docs: str = 'Документация и стиль кода'
    devops: str = 'Контроль версий, CI/CD, контейнеры'
    efficiency: str = 'Проблемы производительности'
    additional: str = 'Паттерны проектирования'
    algorithms: str = 'Структуры данных и алгоритмы'

    def get_values(self):
        """Возвращает список значений атрибутов."""
        return list(self.model_dump().values())


class User(BaseModel):
    id: Optional[int] = None
    tg_id: int
    mode: Optional[str] = None
    skill: Optional[str] = None


class Modes(BaseModel):
    all: str = 'all'
    specific: str = 'specific'
    worst: str = 'worst'


# TODO: Это нужно убрать
mode = Modes()
