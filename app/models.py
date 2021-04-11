from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date
from functools import cache
import json


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"


class Method(Enum):
    POST = "post"
    PATCH = "patch"
    PUT = "put"
    DELETE = "delete"


class PartialUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: Gender
    date_of_birth: date
    country_of_birth: str


class User(PartialUser):
    id: int
    is_admin: Optional[bool] = False


class UserModel(PartialUser):
    __id: int
    __is_admin: Optional[bool] = False

    def __init__(
        self, first_name: str, last_name: str,
        email: str, gender: Gender, date_of_birth: date,
        country_of_birth: str
    ):
        super(User, self).__init__(
            first_name, last_name,
            email, gender, date_of_birth,
            country_of_birth
        )

    @property
    def id(self):
        return self.__id

    @property
    def is_admin(self):
        return self.is_admin

    def post_user(self):
        self.__generate_id
        print("___ id generated ___")
        print(self.__id)
        print("_________")
        with open('db.json', 'a') as js_f:
            user = self.__manage_private_attributes(self.__dict__)
            json.dump(user, js_f)
        return self

    def patch_user(self):
        with open('db.json', 'rw') as js_f:
            users = json.load(js_f)
            for user in users:
                if user['id'] == self.__id:
                    user = {
                        **user,
                        **self.__dict__
                    }
                    user = self.__manage_private_attributes(
                        user.__dict__)
                    break
            json.dump(users, js_f)
        return self

    def put_user(self, user: User):
        self.__dict__ = user.__dict__
        user = self.__manage_private_attributes(user.__dict__)
        with open('db.json', 'rw') as js_f:
            users = json.load(js_f)
            users = list(map(
                lambda u: u if u['id'] != user['id'] else user,
                users
            ))
            json.dump(users, js_f)
        return self

    def delete_user(self):
        with open('db.json', 'rw') as js_f:
            users = json.load(js_f)
            users = list(filter(
                lambda u: u['id'] != self.__id,
                users
            ))
            json.dump(users, js_f)
        return self

    def save(self, action: Method):
        print("save called  id is :", self.__id)
        return {
            Method.POST: self.post_user,
            Method.PATCH: self.patch_user,
            Method.PUT: self.put_user,
            Method.DELETE: self.delete_user,
        }.get(action, lambda: "Error: Invalid action")()

    def __manage_private_attributes(self, user):
        user['id'] = user.pop(f'_{self.__class__.__name__}__id')
        user['is_admin'] = user.pop(
            f'_{self.__class__.__name__}__is_admin')
        return user

    @property
    def __generate_id(self):
        if self.__id is None:
            with open('db.json', 'r') as js_f:
                users = json.load(js_f)
                last_user = max(users, key=lambda u: u['id'])
                self.__id = last_user['id'] + 1
