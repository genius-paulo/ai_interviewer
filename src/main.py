from aiogram import Bot, Dispatcher, executor, types

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from src.bot.states import Form

from src.config import settings
from src.giga_chat.giga_chat import AIInterviewer
from src.giga_chat.prompts import MiddlePythonInterviewerChat

from loguru import logger

# Запускаем бота
bot = Bot(token=settings.tg_token)
# Инициализируем объект памяти для хранения состояний
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# Создаем экземпляр интервьюера
interviewer = AIInterviewer(api_token=settings.gigachat_api_token)


@dp.message_handler(commands=['get_question'])
async def get_question(message: types.Message, state: FSMContext):
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

    await Form.question.set()  # Устанавливаем первое состояние
    # Запоминаем ответ-вопрос бота
    history_chat.question = response.choices[0].message.content
    # Передаем объект истории в состояние
    async with state.proxy() as data:
        data['history_chat'] = history_chat

    # Отправляем вопрос пользователю
    await message.reply(history_chat.question)


# Обработчик ответа на вопрос
@dp.message_handler(state=Form.question)
async def process_question(message: types.Message, state: FSMContext):
    # Получаем объект истории чата
    async with state.proxy() as data:
        history_chat = data['history_chat']
        history_chat.user_answer = message.text
        logger.debug(f'История чата: {history_chat}')
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

    await message.answer(answer)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=settings.skip_updates)
