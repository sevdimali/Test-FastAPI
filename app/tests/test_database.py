import concurrent.futures as futures

from tortoise.contrib import test
from tortoise.query_utils import Q
from main import app
from app.api.api_v1.storage.database import Database


class TestDatabase(test.TestCase):
    def test_connection(self):
        with futures.ThreadPoolExecutor() as executor:
            # Connection OK
            assert (
                executor.submit(Database.connect, application=app).result()
                is True
            )
            # Connection NOK
            assert executor.submit(Database.connect).result() is False

    def test_query_filter_builder(self):
        value = "john"
        scenes = [
            {
                "attr": "first_name",
                "expected": [Q(first_name__icontains=value)],
            },
            {
                "attr": "first_nameOrlast_name",
                "expected": [
                    Q(
                        Q(first_name__icontains=value),
                        Q(last_name__icontains=value),
                        join_type=Q.OR,
                    )
                ],
            },
            {
                "attr": "first_nameANDlast_name",
                "expected": [
                    Q(first_name__icontains=value),
                    Q(last_name__icontains=value),
                ],
            },
            {
                "attr": "first_nameAndlast_nameAndgenderOremail",
                "expected": [
                    Q(first_name__icontains=value),
                    Q(last_name__icontains=value),
                    Q(
                        Q(gender__icontains=value),
                        Q(email__icontains=value),
                        join_type=Q.OR,
                    ),
                ],
            },
            {
                "attr": "first_nameORlast_nameOrgenderANDemail",
                "expected": [
                    Q(
                        Q(first_name__icontains=value),
                        Q(last_name__icontains=value),
                        Q(gender__icontains=value),
                        join_type=Q.OR,
                    ),
                    Q(email_icontains=value),
                ],
            },
        ]
        for scene in scenes:
            assert len(
                Database.query_filter_builder(scene["attr"], value)
            ) == len(scene["expected"])
