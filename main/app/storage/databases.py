from tortoise import Tortoise
from settings import DATABASE_CONFIG


async def init():
    await Tortoise.init(
        config=DATABASE_CONFIG
    )
    await Tortoise.generate_schemas()
