import pytest
import pytest_asyncio
import peewee_async
from src.config import settings
from src.db.db import Users
from loguru import logger

db = peewee_async.PooledPostgresqlDatabase(database=settings.db_name,
                                           user=settings.db_user,
                                           password=settings.db_password,
                                           host=settings.db_host)


class TestUsers(Users):
    class Meta:
        database = db


@pytest.fixture(scope='module')
def get_table():
    return TestUsers


@pytest_asyncio.fixture(scope='module')
async def create_and_delete_tables():
    db.create_tables([TestUsers])
    yield db
    db.drop_tables([TestUsers])
    logger.debug('Таблицы удалены')
    db.close()
    logger.debug('БД закрыта')
