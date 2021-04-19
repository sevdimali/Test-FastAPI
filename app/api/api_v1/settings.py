from api.utils import API_functools


# 'docker' or 'local'
ENV = "docker"

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': API_functools.get_config_env(ENV)['db_host'],
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
