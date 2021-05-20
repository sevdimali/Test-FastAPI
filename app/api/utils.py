import concurrent.futures as futures

from typing import Optional, Dict, Any, Type, TypeVar, List
from pydantic import BaseModel

from api.api_v1.models.tortoise import Person
from api.api_v1.storage.initial_data import INIT_DATA

ORDERS: Dict[str, str] = {"asc": "", "desc": "-"}
MODEL = TypeVar("MODEL", bound="API_functools")


class API_functools:
    @classmethod
    def get_or_default(
        cls: Type[MODEL], list_el: tuple, index: int, default: Any = None
    ) -> Any:
        """Search element from specific list\n

        Args:\n
            cls (API_functools): utility class that used to call this method\n
            list_el (tuple): list of elements
            index (int): position of searched element
            default (Any): default value if element not found in\
                list of elements\n

        Returns:\n
            Any: element if found else default
        """
        return default if len(list_el) <= index else list_el[index]

    @classmethod
    def instance_of(cls: Type[MODEL], el: Any, class_expected: Type[Any]) -> bool:
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
    def get_attributes(cls: Type[MODEL], target_cls) -> tuple[str]:
        """Return class object attributes except ID\n

        Returns:
            tuple[str]: attributes
        """
        return tuple(target_cls.__dict__.get("__fields__", {}).keys())

    @classmethod
    def valid_order(cls: Type[MODEL], target_cls: BaseModel, sort: str) -> Optional[str]:
        """Validator for sort db query result with \
            attribute:direction(asc or desc)\n

        Args:\n
            cls (API_functools): utility class that used to call this method\n
            target_cls (BaseModel): model for db data\n
            sort (str): string to valid from http request\n

        Returns:\n
            Optional[str]: valid sql string order by or None
        """
        attr, order = sort.lower().split(":")
        valid_attributes = ("id",) + cls.get_attributes(target_cls)
        if attr in valid_attributes and order in ORDERS.keys():
            return f"{ORDERS.get(order, '')}{attr}"
        return None

    @classmethod
    def is_attribute_of(
        cls: Type[MODEL],
        attr: str,
        target_cls: BaseModel,
    ) -> bool:
        """Check if attr is a target_cls's attribute
           except the ID attribute\n

        Args:
            cls (MODEL): utility class that used to call this method\n
            target_cls (BaseModel): model for db data\n
            attr (str): attribute to check

        Returns:
            bool: is valid attribute
        """
        return attr.lower() in cls.get_attributes(target_cls)

    @classmethod
    def manage_next_previous_page(
        cls,
        request,
        data: List[Dict],
        nb_total_data: int,
        limit: int,
        offset: int,
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
        data = {"next": None, "previous": None, "users": data}

        # manage next data
        base = request.scope.get("path")
        if offset + limit < nb_total_data and limit <= nb_total_data:
            next_offset = offset + limit
            data["next"] = f"{base}?limit={limit}&offset={next_offset}"

        # manage previous data
        if offset - limit >= 0 and limit <= nb_total_data:
            previous_offset = offset - limit
            data["previous"] = f"{base}?limit={limit}&offset={previous_offset}"
        return data

    @classmethod
    async def insert_default_data(cls, data=INIT_DATA, quantity: int = -1) -> None:
        """Init `person` table with some default users\n

        Args:
            data ([type], optional): data to load. Defaults to INIT_DATA.
            max_data (int, optional): quantity of data to load. \
                Defaults to -1.
        Returns:\n
            None: nothing
        """
        data_length = len(INIT_DATA)
        quantity = quantity if data_length >= quantity >= 1 else data_length
        data = data[:quantity]
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
        return await Person.create(**user)
