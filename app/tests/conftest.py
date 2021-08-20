import pytest
from tortoise.contrib.test import finalizer, initializer

from app.api.api_v1 import settings


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    initializer(
        ["app.api.api_v1.models.tortoise"],
        db_url=getattr(settings, "TORTOISE_TEST_DB", "sqlite://:memory:"),
        app_label="models",
    )
    request.addfinalizer(finalizer)
