from tortoise.contrib.fastapi import register_tortoise

from settings import DATABASE_CONFIG
from models import Person


class Database:

    @classmethod
    def connect(cls, app):
        try:
            register_tortoise(
                app,
                config=DATABASE_CONFIG,
                generate_schemas=True,
                add_exception_handlers=True
            )
        except Exception as e:
            print(e)
