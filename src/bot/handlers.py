import io
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
from src.bot.bot_content.basics import Commands
from src.bot.bot_content.skills import Skills
from src.bot.bot_content.texts import actual_texts

from src.db import db
from src.bot import utils

from src.db.cache.cache import cache

# Создаем экземпляр интервьюера
interviewer = AIInterviewer(api_token=settings.gigachat_api_token)


async def start(message: types.Message, state: FSMContext):
    """Отправляем стартовое сообщение"""
    await state.finish()  # на всякий случай заканчивай все состояния
    logger.info(f'Пользователь {message.from_user.id} запустил бота.')

    await db.create_user(message.from_user.id)
    logger.info(f'Пользователь c Telegram ID {message.from_user.id} создан')

    final_text = actual_texts.greeting.format(user_id=message.from_user.first_name) + actual_texts.all_commands
    await message.answer(text=final_text, reply_markup=await main_keyboard())


async def cancel(message: types.Message, state: FSMContext):
    """Отменяем состояние"""
    logger.info('Отменяем состояние')

    final_text = actual_texts.cancel_all + actual_texts.all_commands
    await message.answer(text=final_text, reply_markup=await main_keyboard())

    await state.finish()


async def get_question(message: types.Message, state: FSMContext):
    """Получаем вопрос от ИИ и передаем пользователю"""
    logger.info('Получаем вопрос от ИИ')
    # Создаем объект истории чата
    history_chat = MiddlePythonInterviewerChat()

    # Получаем пользователя из базы
    user = await db.get_user(tg_id=message.from_user.id)
    # Получаем навык в зависимости от режима и сохраняем навык/оценку в истории чата
    history_chat.skill = await utils.get_skill_by_category(user)
    history_chat.score = getattr(user, history_chat.skill.short_name)

    # Создаем персональный контекст вопроса для пользователя
    personal_context_question = (history_chat
                                 .context_questions
                                 .format(skill=history_chat.skill.short_description))
    logger.info(f'Обновляем персональный контекст вопроса: {personal_context_question}')

    # Составляем запрос в формате, который принимает GigaChatAPI
    response = await interviewer.model.achat({"messages":
        [
            {
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
        await message.reply(text=actual_texts.get_question.format(skill=history_chat.skill.short_description,
                                                                  ai_question=history_chat.question),
                            reply_markup=await question_keyboard())


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

        # Составляем запрос в формате, который принимает GigaChatAPI
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

        # Запоминаем ответ-вопрос бота
        # TODO: это хардкод, нужна отдельная моделька для запроса и ответа
        ai_answer = response.choices[0].message.content

        # Получаем оценку из ответа нейросети, рассчитываем экспоненциальное сглаживание,
        # получаем финальную оценку, чтобы именно ее вставить как новую в базу
        expo_score = utils.get_new_skill_rating(current_rating=history_chat.score,
                                                new_score=utils.parse_score_from_ai_answer(ai_answer))
        # Забиваем оценку в базу
        await db.update_skill_rating(tg_id=message.from_user.id,
                                     skill=history_chat.skill.short_name,
                                     rating=expo_score)
        # Создаем финальное сообщение с изменением оценки
        final_text = actual_texts.ai_answer.format(ai_answer=ai_answer,
                                                   old_score=history_chat.score,
                                                   new_score=expo_score)
        await message.answer(final_text, reply_markup=await main_keyboard())

        # Завершаем состояния
        await state.finish()


async def change_skills(message: types.Message, state: FSMContext):
    """"Изменяем навыки, на основе которых модель будет генерировать вопросы"""
    logger.info('Изменяем навыки пользователя')
    # Устанавливаем состояние изменения навыков
    await Form.skills.set()
    logger.debug(f'Изменили состояние: {state}')
    # Отправляем вопрос пользователю
    await message.reply(text=actual_texts.change_skill,
                        reply_markup=await skills_keyboard())
    await message.reply(text=actual_texts.choose_one_or_cancel,
                        reply_markup=await cancel_keyboard())


async def process_skill_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор скилла"""
    logger.info('Обрабатываем выбор скилла')
    # Сохраняем выбранный скилл пользователя
    skill = callback_query.data
    user = await db.update_skill(callback_query.from_user.id, skill)
    # Завершаем состояния и отвечаем юзеру
    await state.finish()

    await callback_query.message.answer(text=actual_texts.changed_skill
                                        .format(skill=Skills
                                                .get_skill_by_name(user.skill)
                                                .short_description),
                                        reply_markup=await main_keyboard())


async def change_mode(message: types.Message, state: FSMContext):
    """"Изменяем режим тренировок, на основе которого модель будет
    присылать вопросы по одной, по всем или только по слабым темам"""
    logger.info('Изменяем режим тренировок пользователя')
    # Устанавливаем состояние изменения навыков и отправляем вопрос пользователю
    await Form.mode.set()
    await message.reply(text=actual_texts.change_mode,
                        reply_markup=await mode_keyboard())
    await message.reply(text=actual_texts.choose_one_or_cancel,
                        reply_markup=await cancel_keyboard())


async def process_mode_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор режима"""
    logger.info('Обрабатываем выбор навыка')
    # Сохраняем выбранный скилл пользователя и отправляем сообщение
    current_mode = callback_query.data
    await db.update_mode(tg_id=callback_query.from_user.id, mode=current_mode)
    await callback_query.message.answer(text=actual_texts.changed_mode.format(current_mode=current_mode),
                                        reply_markup=await main_keyboard())
    # Завершаем состояние
    await state.finish()


async def get_profile(message: types.Message):
    """Получаем профиль"""
    logger.info('Получаем профиль')
    # Получаем объект пользователя из базы
    user = await db.get_user(tg_id=message.from_user.id)

    # Получаем ключ для кэша и название для файла
    image_cache_key = utils.get_skill_map_name(user, mode='key')
    image_filename = utils.get_skill_map_name(user, mode='file')

    # Проверяем наличие кэша в Redis
    file_id = await cache.get(image_cache_key)

    if file_id is None:
        logger.debug(f"Создаем карту навыков: {image_filename}. "
                     f"Отправляем ее пользователю и загружаем в кэш.")
        # Если кэша нет, создаем картинку со скиллами пользователя
        bytes_skill_map = await utils.create_skill_map(user)
        # Создаем объект InputFile из массива байтов
        skill_map_file = types.InputFile(io.BytesIO(bytes_skill_map), filename=image_filename)
        # Отправляем карту пользователю
        msg = await message.reply_photo(skill_map_file,
                                        caption=actual_texts
                                        .profile
                                        .format(user_mode=user.mode,
                                                user_skill=user.skill))
        # Получаем идентификатор файла
        file_id = msg.photo[-1].file_id
        # Сохраняем идентификатор файла в Redis
        await cache.set(image_cache_key, file_id)
    else:
        logger.debug(f"Отправляем кэш карты навыков: {file_id.decode('utf-8')}")
        # Отправляем файл пользователю
        await message.reply_photo(file_id.decode('utf-8'),
                                  caption=actual_texts
                                  .profile
                                  .format(user_mode=user.mode,
                                          user_skill=user.skill))


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
    dp.register_message_handler(get_profile, Text(Commands.profile_text), )
    dp.register_message_handler(get_profile, commands=[Commands.profile_command])

    #  Хэндлеры обработки ответа на вопрос
    dp.register_message_handler(process_question, state=Form.question)


if __name__ == '__main__':
    logger.debug(Skills.get_skill_by_name('efficiency').short_description)
