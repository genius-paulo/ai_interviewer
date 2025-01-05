import os
import asyncio
from loguru import logger
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from src.bot.states import Form
from src.config import settings
from src.giga_chat.models import MiddlePythonInterviewerChat
from src.giga_chat.giga_chat import AIInterviewer
from src.bot.keyboards import (main_keyboard,
                               question_keyboard,
                               skills_keyboard,
                               mode_keyboard,
                               cancel_keyboard)
from src.bot.models.basics import Commands, User, Modes
from src.bot.models.skills import Skills

from src.db import db
from src.bot import utils

# Создаем экземпляр интервьюера
interviewer = AIInterviewer(api_token=settings.gigachat_api_token)


async def start(message: types.Message, state: FSMContext):
    """Отправляем стартовое сообщение"""
    await state.finish()  # на всякий случай заканчивай все состояния
    logger.info(f'Пользователь {message.from_user.id} запустил бота.')

    await db.create_user(message.from_user.id)
    logger.info(f'Пользователь c Telegram ID {message.from_user.id} создан')
    # TODO: Текст нужно вынести в отдельный дата-класс
    await message.answer(f'Привет, {message.from_user.full_name}! Я бот-интервьюер. '
                         f'Я могу задавать вопросы по программированию на Python. '
                         f'Нажми:\n'
                         f'— /{Commands.get_question_command}, чтобы получить вопрос собеседования.\n'
                         f'— /{Commands.change_skills_command}, чтобы уточнить навыки, которые ты хочешь подтянуть.',
                         reply_markup=await main_keyboard())


async def cancel(message: types.Message, state: FSMContext):
    """Отменяем состояние"""
    logger.info('Отменяем состояние')
    # TODO: Текст (в особенности, повторяющийся текст с командами) нужно вынести в отдельный дата-класс
    await message.answer(f'Окей, отменяем. Если захочешь продолжить, нажми:\n'
                         f'— /{Commands.get_question_command}, чтобы получить вопрос собеседования.\n'
                         f'— /{Commands.change_skills_command}, чтобы уточнить навыки, которые ты хочешь подтянуть.',
                         reply_markup=await main_keyboard())
    await state.finish()


async def get_question(message: types.Message, state: FSMContext):
    """Получаем вопрос от ИИ и передаем пользователю"""
    logger.info('Получаем вопрос от ИИ')
    history_chat = MiddlePythonInterviewerChat()

    user = User(tg_id=message.from_user.id)
    logger.debug(f'Создали объект пользователя: {user.model_dump()}')
    user = await db.get_user(tg_id=message.from_user.id)

    history_chat.skill = await utils.get_skill_by_category(message.from_user.id)
    history_chat.score = getattr(user, history_chat.skill.short_name)
    logger.debug(f'Получили оценку текущего навыка: {history_chat.score=}')

    # TODO: Возможно, стоит как-то получше инкапсулировать логику связи
    #  технического названия навыка и его расширенной версии
    logger.debug(f'Получили навык по категории: {history_chat.skill.short_description}')

    personal_context_question = (history_chat
                                 .context_questions
                                 .format(skill=history_chat.skill.short_description))

    logger.info(f'Обновляем персональный контекст вопроса: {personal_context_question}')

    response = await interviewer.model.achat({"messages":
        [{
            "role": "system",
            "content": personal_context_question
        },
            {
                "role": "user",
                "content": history_chat.make_action
            },
        ], })
    logger.debug(f'Ответ: {response}')

    # Устанавливаем состояние вопроса
    await Form.question.set()
    # Запоминаем ответ-вопрос бота
    # TODO: это хардкод, нужна отдельная моделька для запроса и ответа
    history_chat.question = response.choices[0].message.content
    # Передаем объект истории в состояние
    async with state.proxy() as data:
        data['history_chat'] = history_chat
        # Отправляем вопрос пользователю
        await message.reply(f'Вопрос на знание навыка: {history_chat.skill.short_description}\n\n' + history_chat.question, reply_markup=await question_keyboard())


async def recreate_question(message: types.Message, state: FSMContext):
    """Пересоздаем вопрос"""
    logger.info('Пересоздаем вопрос')
    await state.finish()
    await get_question(message, state)


async def process_question(message: types.Message, state: FSMContext):
    """Обрабатываем ответ на вопрос"""
    # Получаем объект истории чата
    async with state.proxy() as data:
        history_chat = data['history_chat']
        # Дополняем промпт ответом пользователя
        history_chat.user_answer = history_chat.user_answer.format(answer=message.text)
        logger.info(f'Пользователь ответил: {history_chat.user_answer} на вопрос ИИ: {history_chat.question}')
        response = await interviewer.model.achat({"messages":
            [
                {
                    "role": "system",
                    "content": history_chat.context_questions
                },
                {
                    "role": "user",
                    "content": history_chat.make_action
                },
                {
                    "role": "assistant",
                    "content": history_chat.question
                },
                {
                    "role": "user",
                    "content": history_chat.user_answer
                },

            ], })
        logger.debug(response)
        answer = response.choices[0].message.content
        await message.answer(answer, reply_markup=await main_keyboard())

        # Получаем оценку из ответа нейросети, рассчитываем экспоненциальное сглаживания
        # и забиваем оценку в базу
        old_score = history_chat.score
        new_score = utils.parse_score_from_ai_answer(answer)
        expo_score = utils.get_new_skill_rating(old_score, new_score)
        result = await db.update_skill_rating(tg_id=message.from_user.id,
                                              skill=history_chat.skill.short_name,
                                              rating=expo_score)
        logger.debug(f'{result=}')

        await state.finish()  # Завершаем состояния


async def change_skills(message: types.Message, state: FSMContext):
    """"Изменяем навыки, на основе которых модель будет генерировать вопросы"""
    logger.info('Изменяем навыки пользователя')
    # Устанавливаем состояние изменения навыков
    await Form.skills.set()
    logger.debug(f'Изменили состояние: {state}')
    # Отправляем вопрос пользователю
    await message.reply('Какую тему хочешь подтянуть?',
                        reply_markup=await skills_keyboard())
    await message.reply(f"Выбери один из вариантов или нажми {Commands.cancel_text}", reply_markup=await cancel_keyboard())


async def process_skill_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор скилла"""
    logger.info('Обрабатываем выбор скилла')
    skill = callback_query.data
    logger.debug(f'User ID при передаче в get_user(): {callback_query.from_user.id=}')
    # Сохраняем выбранный скилл пользователя
    await db.update_skill(callback_query.from_user.id, skill)
    user = await db.get_user(tg_id=callback_query.from_user.id)
    await state.finish()  # Завершаем состояния
    await callback_query.message.answer(f'Тема для тренировок  в режиме {Modes().specific} обновлена. '
                                        f'Попробуй сгенерировать вопрос по теме '
                                        f'«{Skills.get_skill_by_name(user.skill).short_description}».',
                                        reply_markup=await main_keyboard())


async def change_mode(message: types.Message, state: FSMContext):
    """"Изменяем режим тренировок, на основе которого модель будет
    присылать вопросы по одной, по всем или только по слабым темам"""
    logger.info('Изменяем режим тренировок пользователя')
    # Устанавливаем состояние изменения навыков
    await Form.mode.set()
    logger.debug(f'Изменили состояние: {state}')
    # Отправляем вопрос пользователю
    await message.reply('Вопросы, проверяющие какие навыки ты хочешь получать:'
                        '\n— all — все навыки в случайном порядке,'
                        '\n— specific — конкретный навык, '
                        '\n— worst — навыки с самой низкой оценкой.',
                        reply_markup=await mode_keyboard())
    await message.reply(f"Выбери один из вариантов или нажми {Commands.cancel_text}",
                        reply_markup=await cancel_keyboard())


async def process_mode_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор режима"""
    logger.info('Обрабатываем выбор навык')
    current_mode = callback_query.data
    # Сохраняем выбранный скилл пользователя
    await db.update_mode(tg_id=callback_query.from_user.id, mode=current_mode)
    await callback_query.message.answer(f'Режим тренировок обновлен на {current_mode}.',
                                        reply_markup=await main_keyboard())
    await state.finish()  # Завершаем состояние


async def get_profile(message: types.Message):
    """Получаем профиль"""
    logger.info('Получаем профиль')
    user = await db.get_user(tg_id=message.from_user.id)
    path_to_skill_map = await utils.create_skill_map(message.from_user.id)
    photo_file = types.InputFile(path_to_skill_map)
    await message.reply_photo(photo_file,
                              caption=f'🗺️ Вот карта твоих навыков, показывающая готовность к собеседованию. '
                                      f'Отвечай на вопросы и прокачивай навыки до 9-10 баллов.'
                                      f'\n\n⚙️ Режим тренировок: {user.mode}.'
                                      f'\nAll — все темы в случайном порядке, specific — конкретная тема, '
                                      f'worst — темы с самой низкой оценкой.'
                                      f'\n\n💪 Навык для тренировки в режиме specific: '
                                      f'«{Skills.get_skill_by_name(user.skill).short_description}».')
    logger.info(f'Удаляем файл {path_to_skill_map}')
    await asyncio.get_event_loop().run_in_executor(None, os.remove, path_to_skill_map)


async def register_handlers(dp: Dispatcher):
    """Регистрируем хэндлеры"""
    # Хэндлеры старта и отмены
    dp.register_message_handler(start, commands=[Commands.start])
    dp.register_message_handler(cancel, Text(Commands.cancel_text), state='*')

    # Хэндлеры получения и пересоздания вопроса
    dp.register_message_handler(recreate_question, Text(Commands.another_question_text), state=Form.question)
    dp.register_message_handler(get_question, Text(Commands.get_question_text))
    dp.register_message_handler(get_question, commands=[Commands.get_question_command])

    # Хэндлеры для изменения скиллов
    dp.register_message_handler(change_skills, Text(Commands.change_skills_text))
    dp.register_message_handler(change_skills, commands=[Commands.change_skills_command])
    dp.register_callback_query_handler(process_skill_selection, state=Form.skills)

    # Хэндлеры для изменения режима
    dp.register_message_handler(change_mode, Text(Commands.change_mode_text))
    dp.register_message_handler(change_mode, commands=[Commands.change_mode_command])
    dp.register_callback_query_handler(process_mode_selection, state=Form.mode)

    # Хэндлеры для просмотра профиля
    dp.register_message_handler(get_profile, Text(Commands.profile_text))
    dp.register_message_handler(get_profile, commands=[Commands.profile_command])

    #  Хэндлеры обработки ответа на вопрос
    dp.register_message_handler(process_question, state=Form.question)


if __name__ == '__main__':
    logger.debug(Skills.get_skill_by_name('efficiency').short_description)
