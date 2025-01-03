import peewee_async
import peewee
import asyncio
from src.config import settings
from loguru import logger

from src.bot.models import User
from src.db.models import DBModel, Users, SkillsScores, database_proxy

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


async def get_or_create_user(user: User, table: Users = Users) -> [User, bool]:
    async with db.aio_atomic():
        result_user = table.get_or_create(tg_id=user.tg_id)[0]
        SkillsScores.get_or_create(user_id=result_user)
        logger.debug(result_user)
        return result_user


async def get_user(user: User, table: Users = Users) -> User:
    try:
        return table.get(table.tg_id == user.tg_id)
    except peewee.DoesNotExist:
        return User(tg_id=None, skill=None)


async def update_user(user: User, table: Users = Users) -> User:
    if user.skill is None:
        old_user = await get_user(user)
        user.skill = old_user.skill
    result = table.update(skill=user.skill, mode=user.mode).where(table.tg_id == user.tg_id).execute()
    logger.debug(f'Результат обновления пользователя: {result=}, {user.tg_id=}, {user.skill=}')
    updated_user = await get_user(user)
    logger.debug(f'Получаю пользователя из базы: {updated_user=}')
    return updated_user


async def update_score_skill(user: User, skill: str, score: int) -> None:
    user = await get_user(user)
    result = (SkillsScores
              .update({getattr(SkillsScores, skill): score})
              .where(SkillsScores.user_id == user.id)
              .execute())

    logger.debug(f'Результат обновления скилла: {result=}')


async def get_score_skill(user: User) -> SkillsScores:
    return SkillsScores.get(SkillsScores.user_id == user.id)


async def delete_user(user: User, table: Users = Users) -> None:
    try:
        table.delete().where(table.tg_id == user.tg_id).execute()
        logger.info(f'Пользователь с tg_id {user.tg_id} удален из базы данных.')
    except peewee.DoesNotExist:
        logger.error(f"Пользователь с tg_id {user.tg_id} не найден в базе данных.")


async def main():
    """Небольшие тесты"""
    db = peewee_async.PooledPostgresqlDatabase(database=settings.db_name,
                                                   user=settings.db_user,
                                                   password=settings.db_password,
                                                   host=settings.db_host)
    database_proxy.initialize(db)
    await create_tables(Users())
    user = User(tg_id=542570177)
    await update_score_skill(user, 'algorithms', 10)

if __name__ == '__main__':
    logger.debug('Запуск в режиме отладки')
    asyncio.run(main())
