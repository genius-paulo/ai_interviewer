import pytest
import peewee_async
from src.config import settings
from src.db.models import Users, Skills, SkillsData, database_proxy


@pytest.fixture(scope="module")
def db():
    db = peewee_async.PooledPostgresqlDatabase(database=settings.db_name,
                                               user=settings.db_user,
                                               password=settings.db_password,
                                               host=settings.db_host)
    database_proxy.initialize(db)
    yield db
    #db.drop_tables([Users, Skills])
