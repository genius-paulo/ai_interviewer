import random
import asyncio
import re
from loguru import logger

from src.bot.models import basics, skills
from src.config import settings
from src.db import db

import matplotlib.pyplot as plt
import numpy as np
import textwrap
import uuid
import os


async def get_skill_by_category(tg_id_user) -> skills.Skills:

    user = await db.get_user(tg_id=tg_id_user)

    if user.mode == basics.Modes().all:
        skill = random.choice(skills.Skills.get_children())
        logger.info(f'Пользователь тренирует все скиллы. Выбираем навык рандомно: {skill}')
        return skill()

    elif user.mode == basics.Modes().specific:
        skill = skills.Skills.get_skill_by_name(user.skill)
        logger.info(f'Пользователь тренирует конкретный скилл: {skill}')
        return skill

    elif user.mode == basics.Modes().worst:
        # TODO: Переписать на получение самых слабых навыков
        skill = random.choice(skills.Skills.get_children())
        logger.info(f'Пользователь тренирует самые слабые скиллы: {skill}')
        return skill()


def parse_score_from_ai_answer(answer: str) -> int:
    """Парсим оценку из ответа нейросети"""
    match = re.search(r'Оценка: (\d+/\d+)', answer)
    if match:
        score = int(match.group(1).split('/')[0])
    else:
        score = 1
    logger.info(f'Парсим оценку из ответа нейросети: {score}')
    return score


def get_new_skill_rating(current_rating, new_score, alpha=settings.alpha_coefficient):
    """Пересчитываем оценку, используя метод экспоненциального сглаживания
    для обновления средней оценки"""
    new_score = alpha * new_score + (1 - alpha) * current_rating
    logger.info(f'Пересчитываем оценку, используя метод экспоненциального сглаживания: {new_score}')
    return new_score


async def create_skill_map(tg_id: int) -> str:
    """Создаем диаграмму паука с оценкой навыков"""
    logger.info('Создаем диаграмму паука с оценкой навыков')

    # Получаем оценки навыков в модели пользователя из базы данных
    user = await db.get_user(tg_id)

    # Получаем названия скиллов из класса SkillsData
    all_skills_names = skills.Skills.get_children()

    # Создаем словарь, где ключи - это названия атрибутов в классе SkillsScores,
    # а значения — это названия навыков на русском
    skills_dict = {skill().short_name: skill().short_description for skill in all_skills_names}

    # Создаем список оценок для каждого навыка
    scores = [getattr(user, skill().short_name) for skill in all_skills_names]
    logger.debug(f'Оценки при создании карты: {scores=}')

    # Создаем массив углов для каждого навыка
    angles = np.linspace(0, 2*np.pi, len(skills_dict), endpoint=False).tolist()

    # Добавляем первый угол в конец, чтобы замкнуть диаграмму
    angles += angles[:1]
    scores += scores[:1]

    # Создаем фигуру и оси
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, polar=True)

    # Рисуем диаграмму паука
    ax.plot(angles, scores, 'o-', linewidth=2)
    ax.fill(angles, scores, alpha=0.25)

    # Устанавливаем метки для каждого навыка
    labels = [textwrap.fill(label, 10, break_long_words=False) for label in skills_dict.values()]
    ax.set_thetagrids([angle * 180/np.pi for angle in angles[:-1]], labels)

    # Устанавливаем диапазон значений для оси Y
    ax.set_ylim(0, 10)

    # Увеличиваем размер шрифта и отступы для меток
    ax.tick_params(labelsize=15, pad=60)

    # Устанавливаем отступы для подграфиков
    plt.subplots_adjust(left=0.20, right=0.80, top=0.80, bottom=0.20)

    # Генерируем уникальное название файла
    path_to_result_pic = os.path.join('resources', f'skill_map_{uuid.uuid4()}.png')

    # Создаем папку src/resources/, если она не существует
    os.makedirs(os.path.dirname(path_to_result_pic), exist_ok=True)

    await asyncio.get_event_loop().run_in_executor(None, plt.savefig, path_to_result_pic)

    return path_to_result_pic


if __name__ == '__main__':
    logger.info(get_new_skill_rating(8, 9))

    async def main():
        path_to_result_pic = await create_skill_map(tg_id=542570177)
        print(path_to_result_pic)

    asyncio.run(main())
