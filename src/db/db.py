import peewee_async
import peewee
from src.config import settings
from loguru import logger
from src.bot.models import User

logger.debug(settings)

db = peewee_async.PooledPostgresqlDatabase(database=settings.db_name,
                                           user=settings.db_user,
                                           password=settings.db_password,
                                           host=settings.db_host)


class Users(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    tg_id = peewee.BigIntegerField(unique=True)
    skills = peewee.TextField(default='любые навыки Middle Python-разработчика')

    class Meta:
        database = db


async def create_tables(table: Users = Users):
    db.create_tables([table])


async def get_table(table: Users = Users):
    return table.select()


async def get_or_create_user(user: User, table: Users = Users) -> [User, bool]:
    # Функция для создания строки в таблице Users
    return table.get_or_create(tg_id=user.tg_id)


async def get_or_user(user: User, table: Users = Users) -> User:
    # Функция для создания строки в таблице Users
    try:
        return table.get(table.tg_id == user.tg_id)
    except peewee.DoesNotExist:
        return User(tg_id=None, skills=None)


async def update_user(user: User, table: Users = Users) -> User:
    return table.update(skills=user.skills).where(Users.tg_id == user.tg_id).execute()


async def get_user(user: User = User, table: Users = Users) -> User:
    return table.get(tg_id=user.tg_id)


async def delete_user(user: User, table: Users = Users) -> None:
    return table.delete().where(tg_id=user.tg_id).execute()
