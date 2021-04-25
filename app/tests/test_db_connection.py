from tortoise.contrib import test

from main import app
from api.api_v1.storage.database import Database


class TestUtils(test.TestCase):
    def test_connection(self):
        # Connection OK
        assert Database.connect(app) is True

        # Connection NOK
        assert Database.connect(None) is False
