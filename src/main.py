import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from src.config import settings
from src.bot.handlers import register_handlers

from loguru import logger


async def main():
    # Инициализация бота
    bot = Bot(token=settings.tg_token)
    logger.info(f'Бот инициализирован: {bot}')

    # Инициализируем объект памяти для хранения состояний
    storage = MemoryStorage()
    logger.info(f'Инициализировали объект памяти для состояний: {bot}')

    # Инициализируем диспетчер
    dp = Dispatcher(bot, storage=storage)
    logger.info(f'Инициализировали диспетчер: {bot}')

    # Асинхронная регистрация обработчиков
    await register_handlers(dp)
    logger.info(f'Хэндлеры инициализированы')

    # Запускаем бота
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
