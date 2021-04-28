from tortoise.contrib.fastapi import register_tortoise

from api.api_v1.settings import TORTOISE_ORM as DATABASE_CONFIG


class Database:
    @classmethod
    def connect(cls, application=None):
        success = True
        try:
            register_tortoise(
                application,
                config=DATABASE_CONFIG,
                generate_schemas=True,
                add_exception_handlers=True,
            )
        except Exception as e:
            print(e)
            success = False

        return success
