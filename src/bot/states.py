from aiogram.dispatcher.filters.state import State, StatesGroup


# Создаем класс состояний
class Form(StatesGroup):
    question = State()
    skills = State()
