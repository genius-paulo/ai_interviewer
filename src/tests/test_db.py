import pytest_asyncio
import pytest
from src.db.models import Users
from src.db.db import *


@pytest_asyncio.fixture(scope='module')
async def setup_db():
    # Создаем таблицу
    await create_tables(Users())
    yield
    # Удаляем таблицу
    # Users.drop_table()


@pytest.mark.asyncio
async def test_create_user(setup_db):
    # Создаем пользователя
    await create_user(123456789)
    # Проверяем, что пользователь был создан
    user = Users.get(Users.tg_id == 123456789)
    assert user is not None


@pytest.mark.asyncio
async def test_update_mode(setup_db):
    # Обновляем режим пользователя
    await update_mode(123456789, 'new_mode')
    # Проверяем, что режим пользователя был обновлен
    user = await get_user(123456789)
    assert user.mode == 'new_mode'


@pytest.mark.asyncio
async def test_update_skill(setup_db):
    # Обновляем навык пользователя
    await update_skill(123456789, 'new_skill')
    # Проверяем, что навык пользователя был обновлен
    user = await get_user(123456789)
    assert user.skill == 'new_skill'


@pytest.mark.asyncio
async def test_update_skill_rating(setup_db):
    # Обновляем оценку по навыку пользователя
    await update_skill_rating(123456789, 'basic', 10)
    # Проверяем, что оценка по навыку пользователя была обновлена
    user = await get_user(123456789)
    assert user.basic == 10



