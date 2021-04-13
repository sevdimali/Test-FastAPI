import psycopg2
import psycopg2.extras
from typing import Optional, Tuple
from settings import DB_CONFIG, DOCKER_DB_HOST


class FastAPI_DB:
    __DB = None

    @classmethod
    def getDB(cls):
        if cls.__DB is None:
            cls.__DB = psycopg2.connect(
                # host=DOCKER_DB_HOST,  # comment if run locally
                host=DB_CONFIG.host,  # uncomment if not run with docker
                database=DB_CONFIG.database,
                user=DB_CONFIG.user,
                password=DB_CONFIG.password,
                port=DB_CONFIG.port,
            )
        return cls.__DB

    @classmethod
    def query(cls, query: str, args: Optional[Tuple] = tuple()):
        with cls.getDB() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, args)
            conn.commit()
            return cur
