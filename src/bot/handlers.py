from src.bot.states import Form
from loguru import logger
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


from src.config import settings
from src.giga_chat.models import MiddlePythonInterviewerChat
from src.giga_chat.giga_chat import AIInterviewer
from src.bot.keyboards import main_keyboard, question_keyboard
from src.bot.models import Commands


# Создаем экземпляр интервьюера
interviewer = AIInterviewer(api_token=settings.gigachat_api_token)


async def start(message: types.Message, state: FSMContext):
    """Отправляем стартовое сообщение"""
    logger.info(f'Пользователь {message.from_user.id} запустил бота.')
    await message.answer(f'Привет, {message.from_user.full_name}! Я бот-интервьюер. '
                         f'Я могу задавать вопросы по программированию на Python. '
                         f'Нажми:\n'
                         f'— /{Commands.get_question_command}, чтобы получить вопрос собеседования.'
                         f'— /{Commands.change_skills_command}, чтобы уточнить навыки, которые ты хочешь подтянуть.',
                         reply_markup = await main_keyboard())
    await state.finish()


async def get_question(message: types.Message, state: FSMContext):
    """Получаем вопрос от ИИ и передаем пользователю"""
    logger.info('Получаем вопрос от ИИ')
    history_chat = MiddlePythonInterviewerChat()
    response = await interviewer.model.achat({"messages":
        [{
            "role": "system",
            "content": history_chat.context_questions
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
    history_chat.question = response.choices[0].message.content
    # Передаем объект истории в состояние
    async with state.proxy() as data:
        data['history_chat'] = history_chat

    # Отправляем вопрос пользователю
    await message.reply(history_chat.question, reply_markup = await question_keyboard())


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
        history_chat.user_answer = message.text
        logger.info(f'Пользователь ответил: {history_chat.user_answer} на вопрос ИИ: {history_chat.question}')
        response = await interviewer.model.achat({"messages":
            [
                {
                    "role": "system",
                    "content": history_chat.context_questions
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
        await state.finish()  # Завершаем состояния

    await message.answer(answer, reply_markup = await main_keyboard())


async def change_skills(message: types.Message, state: FSMContext):
    """"Изменяем навыки, на основе которых модель будет генерировать вопросы"""
    logger.info('Изменяем навыки пользователя')
    # Устанавливаем состояние изменения навыков
    await Form.skills.set()
    # Отправляем вопрос пользователю
    await message.reply('Скоро можно будет конкретно указать, на какие навыки интервьюер сделает упор. '
                        'А пока функция в работе.', reply_markup=await main_keyboard())
    # Заканчиваем состояние
    await state.finish()


async def cancel(message: types.Message, state: FSMContext):
    """Отменяем состояние"""
    logger.info('Отменяем состояние')
    await message.answer(f'Окей, отменяем. Если захочешь продолжить, нажми:\n'
                         f'— /{Commands.get_question_command}, чтобы получить вопрос собеседования.\n'
                         f'— /{Commands.change_skills_command}, чтобы уточнить навыки, которые ты хочешь подтянуть.',
                         reply_markup=await main_keyboard())
    await state.finish()


async def register_handlers(dp: Dispatcher):
    """Регистрируем хэндлеры"""
    # Хэндлеры старта и отмены
    dp.register_message_handler(start, commands=[Commands.start])
    dp.register_message_handler(cancel, Text(Commands.cancel_text), state=Form.question)

    # Хэндлеры получения и пересоздания вопроса
    dp.register_message_handler(recreate_question, Text(Commands.another_question_text), state=Form.question)
    dp.register_message_handler(get_question, Text(Commands.get_question_text))
    dp.register_message_handler(get_question, commands=[Commands.get_question_command])

    # Хэндлеры для изменения скиллов
    dp.register_message_handler(change_skills, Text(Commands.change_skills_text))

    #  Хэндлеры обработки ответа на вопрос
    dp.register_message_handler(process_question, state=Form.question)
