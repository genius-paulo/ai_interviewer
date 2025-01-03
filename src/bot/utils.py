import random
import re
from loguru import logger
import asyncio

from src.bot.models import User, Modes, SkillsData
from src.db import db, models

import matplotlib.pyplot as plt
import numpy as np
import textwrap
import uuid
import os


async def get_questions_category(user: User) -> str:
    user = await db.get_user(user)
    skills = SkillsData()
    if user.mode == Modes.all:
        skill = random.choice(skills.get_values())
        logger.info(f'Пользователь тренирует все скиллы. Выбираем навык рандомно: {skill}')
        return skill
    elif user.mode == Modes.specific:
        skill = user.skill
        logger.info(f'Пользователь тренирует конкретный скилл: {skill}')
        return skill
    elif user.mode == Modes.worst:
        skill = random.choice(skills.get_values())
        logger.info(f'Пользователь тренирует самые слабые скиллы: {skill}')
        return skill


async def parse_score_from_ai_answer(answer: str) -> int:
    """Парсим оценку из ответа нейросети"""
    match = re.search(r'Оценка: (\d+/\d+)', answer)
    if match:
        score = int(match.group(1).split('/')[0])
    else:
        score = 1
    logger.info(f'Парсим оценку из ответа нейросети: {score}')
    return score


async def create_skill_map(skill_score: db.SkillsScores) -> str:
    """Создаем диаграмму паука с оценкой навыков"""
    logger.info('Создаем диаграмму паука с оценкой навыков')

    # Получаем названия скиллов из класса SkillsData
    skills_data = SkillsData()
    skills = skills_data.model_dump()

    # Создаем словарь, где ключи - это названия атрибутов в классе SkillsScores,
    # а значения — это названия навыков на русском
    skills_dict = {attr: value for attr, value in skills.items()}

    # Создаем список оценок для каждого навыка
    scores = [getattr(skill_score, skill) for skill in skills_dict.keys()]

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
    loop = asyncio.get_event_loop()
    answer = 'Оценка: 7/10'
    logger.info(loop.run_until_complete(parse_score_from_ai_answer(answer)))