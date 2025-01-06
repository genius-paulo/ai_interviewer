from pydantic import BaseModel
from loguru import logger
from typing import TypeVar

T = TypeVar('T', bound='Skill')


class Skills(BaseModel):
    short_name: str
    short_description: str
    long_description: str

    @classmethod
    def get_children(cls) -> list:
        """Функция нужна для того, чтобы получать список всех дочерних скиллов"""
        return [child for child in cls.__subclasses__() if child is not cls]

    @classmethod
    def get_skill_by_name(cls, skill_name) -> T:
        """Функция нужна для того, чтобы получать скилл по атрибуту short_name"""
        skill_classes_list = cls.get_children()
        logger.debug(f'Вот такой список классов: {skill_classes_list}')
        for skill in skill_classes_list:
            logger.debug(f'Проходим класс {skill}')
            if skill().short_name == skill_name:
                return skill()
        raise AttributeError


class Basic(Skills):
    short_name: str = 'basic'
    short_description: str = 'Основы Python'
    long_description: str = 'Подробное описание навыка Основы Python'


class OOP(Skills):
    short_name: str = 'oop'
    short_description: str = 'ООП'
    long_description: str = 'Подробное описание навыка ООП'


class StandardLib(Skills):
    short_name: str = 'standard_lib'
    short_description: str = 'Стандартная библиотека'
    long_description: str = 'Подробное описание навыка Стандартная библиотека'


class AsyncProg(Skills):
    short_name: str = 'async_prog'
    short_description: str = 'Асинхронное программирование'
    long_description: str = 'Подробное описание навыка Асинхронное программирование'


class DB(Skills):
    short_name: str = 'db'
    short_description: str = 'Работа с базами данных'
    long_description: str = 'Подробное описание навыка Работа с базами данных'


class Web(Skills):
    short_name: str = 'web'
    short_description: str = 'Веб-фреймворки и RESTful API'
    long_description: str = 'Подробное описание навыка Веб-фреймворки и RESTful API'


class Test(Skills):
    short_name: str = 'test'
    short_description: str = 'Тестирование'
    long_description: str = 'Подробное описание навыка Тестирование'


class Docs(Skills):
    short_name: str = 'docs'
    short_description: str = 'Документация и стиль кода'
    long_description: str = 'Подробное описание навыка Документация и стиль кода'


class DevOps(Skills):
    short_name: str = 'devops'
    short_description: str = 'Контроль версий, CI/CD, контейнеры'
    long_description: str = 'Подробное описание навыка Контроль версий, CI/CD, контейнеры'


class Efficiency(Skills):
    short_name: str = 'efficiency'
    short_description: str = 'Проблемы производительности'
    long_description: str = 'Подробное описание навыка Проблемы производительности'


class Additional(Skills):
    short_name: str = 'additional'
    short_description: str = 'Паттерны проектирования'
    long_description: str = 'Подробное описание навыка Паттерны проектирования'


class Algorithms(Skills):
    short_name: str = 'algorithms'
    short_description: str = 'Структуры данных и алгоритмы'
    long_description: str = 'Подробное описание навыка Структуры данных и алгоритмы'


if __name__ == '__main__':
    skill_class = Skills.get_skill_by_name('efficiency')
    logger.info(skill_class.long_description)
