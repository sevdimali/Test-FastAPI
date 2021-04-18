DATABASE_CONFIG = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': 'api_db',  # comment if postgres is in localhost
                # 'host': 'localhost',  # uncomment if running postgres in localhost
                'port': '5432',
                'user': 'postgres',
                'password': 'postgres',
                'database': 'fastapidb',
            }
        }
    },
    'apps': {
        'app': {
            'models': ['api.api_v1.models.tortoise'],
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
