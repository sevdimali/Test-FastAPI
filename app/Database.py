import psycopg2
import psycopg2.extras
from typing import Optional, Tuple
from settings import DB_CONFIG
from models import User


class Database:
    __DB = None

    @classmethod
    def getDB(cls):
        if cls.__DB is None:
            cls.__DB = psycopg2.connect(
                host=DB_CONFIG.host,
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


class UserTable():

    def get_users(self, limit=10, offset=1, sort="id:asc"):
        attr, order = sort.split(':')
        query = f"""SELECT *
        FROM person
        ORDER BY {attr} {order}
        LIMIT {limit}
        offset {offset}"""
        with Database.query(query) as cur:
            users = [dict(u) for u in cur.fetchall()]
            return users

    def get_user_by_id(self, user_id):
        query = f"""PREPARE getperson (int) AS
            SELECT *
            FROM person
            WHERE id=$1;
        EXECUTE getperson({user_id});"""
        with Database.query(query, (user_id,)) as cur:
            user = cur.fetchone()
            return dict(user) if user is not None else None

    def create_user(self, user_data):
        query = """PREPARE newperson (text, text, text, text, text, text) AS
            INSERT INTO person(
                first_name,
                last_name,
                gender,
                email,
                date_of_birth,
                country_of_birth
            ) VALUES($1,$2,$3,$4,$5,$6);
        EXECUTE newperson({0}{1}{2}{3}{4}{5});""".format(*user_data)
        print("--------- QUERY --------------")
        print(query)
        print("--------- QUERY --------------")
        with Database.query(query, user_data) as cur:
            return cur.lastrowid

    # def update_user(self, new_data):
    #     query = """UPDATE TABLE person set
    #     pass

    # def delete_user(self, id):
    #     query = "DELETE FROM person WHERE id=$1"
    #     Database.query(query, (id,))
