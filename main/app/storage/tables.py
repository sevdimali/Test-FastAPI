
from typing import Optional, Tuple
from models.classes import User, PartialUser
from .databases import FastAPI_DB


class UserTable():

    __VALID_FIELDS: Tuple[str] = (
        'id', 'is_admin',
        'first_name', 'last_name'
        'email', 'gender'
        'date_of_birth', 'country_of_birth'
    )

    def get_users(self, limit=10, offset=0, sort="id:asc"):
        """Get all users

        Args:
            limit (int, optional): max number of users to return. Defaults to 10.
            offset (int, optional): starting index in the list of users to return. Defaults to 0.
            sort (str, optional): order the list of users with the combination attribute: order. Defaults to "id:asc".

        Returns:
            dict: list of users found, success state
        """
        attr, order = sort.split(':')
        if not attr in self.__VALID_FIELDS:
            return {
                "success": False,
                "detail": f"Invalid attribute order by '{attr}'"
            }
        query = f"""SELECT *
        FROM person
        ORDER BY {attr} {order}
        LIMIT {limit}
        offset {offset}"""
        with FastAPI_DB.query(query) as cur:
            users = [dict(u) for u in cur.fetchall()]
            return {"success": True, "users": users}

    @classmethod
    def number_user(cls):
        """Get number of users

        Returns:
            int: number of users
        """
        with FastAPI_DB.query("SELECT COUNT(*) AS number_user FROM person") as cur:
            return dict(cur.fetchone()).get("number_user", 0)

    def get_user_by_id(self, user_id):
        """Get user by ID

        Args:
            user_id (int): User ID

        Returns:
            dict: user found, success state, Optional[detail]
        """
        query = f"""SELECT *
            FROM person
            WHERE id=%s;"""
        with FastAPI_DB.query(query, (user_id,)) as cur:
            user = cur.fetchone()
            return {
                "success": True,
                "user": dict(user)
            }if user is not None else {
                "success": False,
                "user": {},
                "detail": "Not Found"
            }

    def post_user(self, user_data: PartialUser):
        """Create new users

        Args:
            user_data (PartialUser): User to create

        Returns:
            dict: user created, success state
        """
        prepare_data = (
            user_data.first_name, user_data.last_name,
            user_data.gender.value, user_data.email,
            user_data.date_of_birth.isoformat(),
            user_data.country_of_birth)
        query = """INSERT INTO person(
                first_name,
                last_name,
                gender,
                email,
                date_of_birth,
                country_of_birth
            ) VALUES(%s,%s,%s,%s,%s,%s)
            RETURNING *;"""
        with FastAPI_DB.query(query, args=prepare_data) as cur:
            return {"success": True, "user": dict(cur.fetchone())}

    def patch_user(self, user_id: int, user_data: PartialUser):
        """Fix some users attributes except his ID

        Args:
            user_id (int): user ID
            user_data (PartialUser): new data

        Returns:
            dict: user fixed, success state
        """
        if user_id == 1:
            return {"detail": "Cannot patch admin user."}
        prepare_data = (
            user_data.first_name, user_data.last_name,
            user_data.gender.value, user_data.email,
            user_data.date_of_birth.isoformat(),
            user_data.country_of_birth, str(user_id))
        query = """UPDATE person set
                first_name=%s,
                last_name=%s,
                gender=%s,
                email=%s,
                date_of_birth=%s,
                country_of_birth=%s
            WHERE id=%s
            RETURNING *;"""
        with FastAPI_DB.query(query, prepare_data) as cur:
            if cur.rowcount >= 1:
                return {"success": True, "user": dict(cur.fetchone())}

    def put_user(self, user_id: int, new_user: User):
        """Replace user by another

        Args:
            user_id (int): user to replace, his ID
            new_user (User): new user

        Returns:
            dict: user updated, success state
        """
        if user_id == new_user.id:
            return {
                "success": False,
                "detail": "Please use PATCH method instead of PUT."
            }
        if user_id == 1:
            return {
                "success": False,
                "detail": "Cannot update admin user."
            }
        # update if id > 0 and user with chosen id doesn't exist
        if not self.get_user_by_id(new_user.id)['success'] and not new_user.id == 0:
            prepare_data = (
                str(new_user.id),
                new_user.first_name, new_user.last_name,
                new_user.gender.value, new_user.email,
                new_user.date_of_birth.isoformat(),
                new_user.country_of_birth, str(user_id))
            query = """UPDATE person set
                    id=%s,
                    first_name=%s,
                    last_name=%s,
                    gender=%s,
                    email=%s,
                    date_of_birth=%s,
                    country_of_birth=%s
                WHERE id=%s
                RETURNING *;"""
            with FastAPI_DB.query(query, prepare_data) as cur:
                return {"success": True, "user": dict(cur.fetchone())}

        return {
            "success": False,
            "detail": f"Invalid user ID={new_user.id} or already exists."
        }

    def delete_user(self, user_id: int):
        """Delete a user

        Args:
            user_id (int): user to delete, his ID

        Returns:
            dict: user deleted, success state
        """
        user_exists = self.get_user_by_id(user_id)
        if user_exists['success']:

            if user_exists['user']['is_admin']:
                return {"detail": "Cannot delete admin user."}

            query = "DELETE FROM person WHERE id=%s RETURNING *"
            with FastAPI_DB.query(query, (user_id,)) as cur:
                return {"success": True, "user": dict(cur.fetchone())}

        return {
            "success": False,
            "detail": f"Invalid user ID: {user_id}"
        }
