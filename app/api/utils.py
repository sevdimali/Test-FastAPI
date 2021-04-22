import concurrent.futures as futures

from typing import Optional, Dict, Any, Type, TypeVar, List
from pydantic import BaseModel

from api.api_v1.models.tortoise import Person
from api.api_v1.storage.initial_data import INIT_DATA

ORDERS: Dict[str, str] = {
    "asc": "",
    "desc": "-"
}
MODEL = TypeVar("MODEL", bound="API_functools")


class API_functools:

    @classmethod
    def get_or_default(cls: MODEL, list_el: tuple, index: int, default: Any = None) -> Any:
        """Search element from specific list\n

        Args:\n
            cls (API_functools): utility class that used to call this method\n
            list_el (tuple): list of elements
            index (int): position of searched element
            default (Any): default value if element not found in list of elements

        Returns:
            Any: element if found else default
        """
        if len(list_el) <= index:
            return default

        return list_el[index]

    @classmethod
    def instance_of(cls: MODEL, el: Any, class_expected: Type[Any]) -> bool:
        """Check element is from specific class\n

        Args:\n
            cls (API_functools): utility class that used to call this method\n
            el (Any): object from any class\n
            class_expected (Type[U]): class expected\n

        Returns:\n
            bool: equality(True if equals else False)
        """
        return el.__class__.__name__.lower() == class_expected.__name__.lower()

    @classmethod
    def valid_order(cls: MODEL, target_cls: BaseModel, sort: str) -> Optional[str]:
        """Validator for sort db query result with attribute:direction(asc or desc)\n

        Args:\n
            cls (API_functools): utility class that used to call this method\n
            target_cls (BaseModel): model for db data\n
            sort (str): string to valid from http request\n

        Returns:\n
            Optional[str]: valid sql string order by or None
        """
        attr, order = sort.split(":")
        valid_attributes = ('id',) + tuple(
            target_cls.__dict__.get('__fields__', {}).keys())
        if attr.lower() in valid_attributes and order.lower() in ORDERS.keys():
            return f"{ORDERS.get(order.lower(), '')}{attr.lower()}"
        return None

    @classmethod
    def manage_next_previous_page(
        cls,
        request,
        data: List[Dict],
        nb_total_data: int,
        limit: int, offset: int
    ) -> Dict[str, Any]:
        """Manage next/previous data link(url)

        Args:
            request (Request): current request
            data (Dict[str, Any]): request response data
            nb_total_data (int): total number of resources from DB
            limit (int): limit quantity of returned data
            offset (int): offset of returned data

        Returns:
            Dict[str, Any]: response
        """
        data = {
            "next": None,
            "previous": None,
            "users": data
        }

        # manage next data
        base = request.scope.get("path")
        if offset+limit < nb_total_data and limit <= nb_total_data:
            next_offset = offset + limit
            data['next'] = f'{base}?limit={limit}&offset={next_offset}'

        # manage previous data
        if offset-limit >= 0 and limit <= nb_total_data:
            previous_offset = offset - limit
            data['previous'] = f'{base}?limit={limit}&offset={previous_offset}'
        return data

    @classmethod
    async def insert_default_data(cls, data=INIT_DATA) -> None:
        """Init `person` table with some default users\n
        Returns:\n
            None: nothing
        """
        with futures.ProcessPoolExecutor() as executor:
            for user in data:
                executor.map(await cls._create_default_person(user))

    @classmethod
    async def _create_default_person(cls, user: dict) -> Person:
        """Insert person into `person` table
            called by insert_default_data function\n

        Args:\n
            user (dict): user data to insert according to person model\n

        Returns:\n
            Person: inserted person
        """
        person = await Person.create(
            is_admin=user["is_admin"],
            first_name=user['first_name'],
            last_name=user['last_name'],
            gender=user['gender'],
            email=user['email'],
            avatar=user['avatar'],
            company=user['company'],
            job=user['job'],
            date_of_birth=user['date_of_birth'],
            country_of_birth=user['country_of_birth']
        )
        return person
