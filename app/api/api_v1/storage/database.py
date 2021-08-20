import re
from typing import Any, List

from tortoise.contrib.fastapi import register_tortoise
from tortoise.query_utils import Q

from app.api.api_v1.settings import TORTOISE_ORM as DATABASE_CONFIG


class Database:
    @classmethod
    def connect(cls, application=None):
        success = True
        try:
            register_tortoise(
                application,
                config=DATABASE_CONFIG,
                generate_schemas=True,
                add_exception_handlers=True,
            )
        except Exception as e:
            print(e)
            success = False

        return success

    @classmethod
    def query_filter_builder(cls, user_attribute: str, value: Any) -> List[Q]:
        """Build a filter with Q function and attributes separated
           by following keywords: Or, And, AND, OR\n

        Args:
            user_attribute (str): attributes
            ex: first_nameOrlast_nameAndemail\n
            value (Any): value that equals attribute\n

        Returns:
            List[Q]: List of Q functions according to attributes and value\n
        """
        attributes = re.compile(r"Or|And|OR|AND").split(user_attribute)
        query_builder = []
        for attr in attributes:
            attr = attr.strip().lower()
            cond = {f"{attr}__icontains": value}
            if user_attribute.split(attr)[0].lower().endswith("or"):
                last_query = query_builder.pop()
                query_builder.append(Q(last_query, Q(**cond), join_type="OR"))
            elif attr != "":
                query_builder = [*query_builder, Q(**cond)]
        return query_builder
