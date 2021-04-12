from collections import namedtuple
DATABASES_CONFIG = namedtuple(
    'DATABASES_CONFIG',
    ("host", "database", "user", "password", "port"))

# postgresql image name
DOCKER_DB_HOST = "db"
DB_CONFIG = DATABASES_CONFIG(
    host="127.0.0.1",
    database="fastapidb",
    user="postgres",
    password="postgres",
    port=5432)
