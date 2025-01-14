from playhouse.migrate import PostgresqlMigrator, migrate
from src.db.db import db
from src.db.models import Users
import peewee

# Создаем мигратор
migrator = PostgresqlMigrator(db)


def run_migrations():
    db.connect()
    if not Users.table_exists():
        db.create_tables([Users])
    else:
        field_name = 'paid'
        # Проверка на существование поля 'paid'
        if not Users._meta.fields.get(field_name):
            # Добавление нового поля в таблицу users
            migrate(
                migrator.add_column('users', field_name, peewee.BooleanField(default=False))
            )
    db.close()


if __name__ == "__main__":
    run_migrations()

