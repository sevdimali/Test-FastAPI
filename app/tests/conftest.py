import os
# import  asyncio
import pytest
from tortoise.contrib.test import finalizer, initializer

from api.api_v1 import settings


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    # LOOP = asyncio.get_event_loop()
    initializer(["api.api_v1.models.tortoise"], db_url=getattr(
        settings, "TORTOISE_TEST_DB", "sqlite://:memory:"), app_label='models')
    request.addfinalizer(finalizer)
