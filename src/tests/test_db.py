import pytest
import peewee
from loguru import logger

from src.db.db import create_tables, insert_skills, get_or_create_user, update_user, delete_user
from src.bot.models import User
from src.db.models import Users, Skills, SkillsData


@pytest.mark.asyncio
async def test_create_tables(db):
    await create_tables(Users)
    await create_tables(Skills)
    assert Users.table_exists()
    assert Skills.table_exists()


@pytest.mark.asyncio
async def test_insert_skills(db):
    skills_data_model = SkillsData()
    await insert_skills()
    skills = Skills.select().execute()
    assert len(skills) == len(skills_data_model.model_dump())


@pytest.mark.asyncio
async def test_get_or_create_user(db):
    user = User(tg_id=1234567)
    result = await get_or_create_user(user)
    logger.info(f'Пользователь создан: {result}: {result.tg_id=}')
    assert result
    assert result.tg_id == user.tg_id


@pytest.mark.asyncio
async def test_update_user(db):
    user = User(tg_id=1234567, skills="new_skills")
    updated_user = await update_user(user)
    logger.info(f'Пользователь обновлен: {updated_user}: {updated_user.tg_id=}, {updated_user.skills=}')
    assert updated_user.skills == user.skills


@pytest.mark.asyncio
async def test_delete_user(db):
    user = User(tg_id=1234567)
    await delete_user(user)
    result_check_user = Users.get_or_none(Users.tg_id == user.tg_id)
    logger.debug(f'{result_check_user=}')
    assert Users.get_or_none(Users.tg_id == user.tg_id) is None



@pytest.mark.asyncio
async def test_create_skill_score():
    pass
