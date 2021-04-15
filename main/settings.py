DATABASE_CONFIG = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                # 'host': 'db', # uncomment if running with docker
                'host': 'localhost',  # comment if running with docker
                'port': '5432',
                'user': 'postgres',
                'password': 'postgres',
                'database': 'fastapidb',
            }
        }
    },
    'apps': {
        'app': {
            'models': ['app.models'],
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
        }
    },
}
