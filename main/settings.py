DATABASE_CONFIG = {
    'connections': {
        # Dict format for connection
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': 'db',
                'port': '5432',
                'user': 'postgres',
                'password': 'postgres',
                'database': 'fastapidb',
            }
        }
    },
    'apps': {
        'app': {
            'models': ['Person'],
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
        }
    }
}
