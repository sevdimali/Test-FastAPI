# runing app environment('local' or 'docker'). Defaults to "docker".
ENV = "docker"


def get_config_env() -> dict:
    """set port and host depending on environment

    Returns:
        dict: contains host and port
    """
    return {
        "docker": {
            "port": 80,
            "db_host": "api_db"
        },
        "local": {
            "port": 8000,
            "db_host": "127.0.0.1"
        }
    }.get(ENV)


TORTOISE_TEST_DB = "sqlite://tests/test-{}.sqlite3"
TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                # set ENV variable
                'host': get_config_env()['db_host'],
                'port': '5432',
                'user': 'postgres',
                'password': 'postgres',
                'database': 'fastapidb',
            }
        }
    },
    'apps': {
        'app': {
            'models': ['api.api_v1.models.tortoise', "aerich.models"],
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
        }
    },
}

CORS_MIDDLEWARE_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PATCH", "PUT", "DELETE"],
    "allow_headers": ["*"],
}
