import peewee

from src.bot.models import mode, SkillsData

# Создаем пустой Proxy для будущей базы данных
database_proxy = peewee.Proxy()


class DBModel(peewee.Model):
    # Указываем proxy вместо реальной базы данных
    class Meta:
        database = database_proxy


class Users(DBModel):
    id = peewee.AutoField(primary_key=True)
    tg_id = peewee.BigIntegerField(unique=True)
    mode = peewee.CharField(choices=[mode.all, mode.specific, mode.worst], default=mode.all)
    skill = peewee.TextField(default=SkillsData().basic)


class SkillsScores(DBModel):
    user_id = peewee.ForeignKeyField(Users)
    basic = peewee.IntegerField(default=0)
    oop = peewee.IntegerField(default=0)
    standard_lib = peewee.IntegerField(default=0)
    async_prog = peewee.IntegerField(default=0)
    db = peewee.IntegerField(default=0)
    web = peewee.IntegerField(default=0)
    test = peewee.IntegerField(default=0)
    docs = peewee.IntegerField(default=0)
    devops = peewee.IntegerField(default=0)
    efficiency = peewee.IntegerField(default=0)
    additional = peewee.IntegerField(default=0)
    algorithms = peewee.IntegerField(default=0)
