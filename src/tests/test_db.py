import pytest
from src.db import db
from loguru import logger
from src.bot.models import User
import random


@pytest.mark.asyncio
@pytest.mark.parametrize('tg_id, skills', ([
    [random.randint(1000000, 99999999), 'алгосики'],
    [random.randint(1000000, 99999999), 'питон, джанго и прочее'],
]))
async def test_create_user(create_and_delete_tables, get_table, tg_id, skills):
    table = get_table()
    new_user = User(tg_id=tg_id, skills=skills)
    await db.get_or_create_user(new_user, table)
    assert (await db.get_user(new_user, table)).tg_id == new_user.tg_id

