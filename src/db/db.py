import peewee_async
from loguru import logger

from src.config import settings
from src.db.models import DBModel, Users, database_proxy
from src.bot.bot_content.basics import Modes

logger.debug(settings)

db = peewee_async.PooledPostgresqlDatabase(database=settings.db_name,
                                           user=settings.db_user,
                                           password=settings.db_password,
                                           host=settings.db_host)
# Привязываем базу данных к прокси
database_proxy.initialize(db)


async def create_tables(table: DBModel):
    db.create_tables([table])


async def get_table(table: DBModel):
    return await table.select()


async def get_user(tg_id: int):
    user = Users.get(Users.tg_id == tg_id)
    return user


async def create_user(tg_id: int):
    user = Users(tg_id=tg_id)
    user.save()


async def update_mode(tg_id: int, mode: str):
    user = Users.get(Users.tg_id == tg_id)
    user.mode = mode
    user.save()


async def update_skill(tg_id: int, skill: str):
    user = Users.get(Users.tg_id == tg_id)
    user.skill = skill
    user.mode = Modes().specific
    user.save()


async def update_skill_rating(tg_id: int, skill: str, rating: int):
    user = Users.get(Users.tg_id == tg_id)
    setattr(user, skill, rating)
    user.save()
