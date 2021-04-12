from collections import namedtuple
DATABASES_CONFIG = namedtuple(
    'DATABASES_CONFIG',
    ("host", "database", "user", "password", "port"))

DB_CONFIG = DATABASES_CONFIG(
    host="127.0.0.1",
    database="api_db",
    user="postgres",
    password="postgres",
    port=5432)
