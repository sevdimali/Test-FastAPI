import concurrent.futures as futures

from tortoise.contrib import test

from main import app
from api.api_v1.storage.database import Database


class TestUtils(test.TestCase):
    def test_connection(self):
        with futures.ThreadPoolExecutor() as executor:
            # Connection OK
            executor.submit(Database.connect, application=app).result() is True
            # Connection NOK
            executor.submit(Database.connect).result() is False