import re
import concurrent.futures as futures
from typing import Optional, Dict, Any, Type, TypeVar, List

from pydantic import BaseModel
from tortoise.models import Model

from .api_v1.models.tortoise import Person, Comment
from .api_v1.storage.initial_data import INIT_DATA

ORDERS: Dict[str, str] = {"asc": "", "desc": "-"}
MODEL = TypeVar("MODEL", bound="API_functools")


class API_functools:
    @classmethod
    def strip_spaces(cls: Type[MODEL], string: str) -> str:
        """Remove multiple spaces in the given string

        Args:
            string (str): string to be processed
        Returns:
            str: processed string
        """
        return re.sub(r"\s{2,}", " ", string.strip())

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
    def instance_of(
        cls: Type[MODEL], el: Any, expected_class: Type[Any]
    ) -> bool:
        """Check element is from specific class\n

        Args:\n
            cls (API_functools): utility class that used to call this method\n
            el (Any): object from any class\n
            expected_class (Type[U]): class expected\n

        Returns:\n
            bool: equality(True if equals else False)
        """
        return el.__class__.__name__.lower() == expected_class.__name__.lower()

    @classmethod
    def get_attributes(
        cls: Type[MODEL], target_cls: BaseModel, **kwargs: dict
    ) -> tuple[str]:
        """Return class object attributes except ID\n

        Args:\n
            target (BaseModel): The class
            kwargs (dict): options
                exclude (list or tuple): attributes to exclude from attributes found
                replace (dict): attributes to replace, key(old) -> value(new)
                add (list or tuple): some attributes to add to the attributes found
        Returns:
            tuple[str]: attributes
        """
        exclude = kwargs.get("exclude", tuple())  # (attr1, attr2)
        add = kwargs.get("add", tuple())  # (new_attr1, new_attr2)
        replace = kwargs.get("replace", dict())  # {old_attr: new_attr}
        attributes = tuple(target_cls.__dict__.get("__fields__", {}).keys())

        for old, new in replace.items():
            attributes = tuple(
                map(lambda attr: new if attr == old else attr, attributes)
            )
        if type(add) in (tuple, list):
            for attr in add:
                attributes += (attr,)
        if type(exclude) in (tuple, list):
            attributes = tuple(
                filter(lambda attr: attr not in exclude, attributes)
            )

        return attributes

    @classmethod
    def valid_order(
        cls: Type[MODEL], target_cls: BaseModel, sort: str, **kwargs: dict
    ) -> Optional[str]:
        """Validator for sort db query result with \
            attribute:direction(asc or desc)\n

        Args:\n
            cls (API_functools): utility class that used to call this method\n
            target_cls (BaseModel): model for db data\n
            sort (str): string to valid from http request\n
            kwargs (dict): Options
                more_attributes (list or tuple): append more attributes to check

        Returns:\n
            Optional[str]: valid sql string order by or None
        """
        attr, order = sort.lower().split(":")
        valid_attributes = ("id",) + cls.get_attributes(
            target_cls, add=kwargs.get("more_attributes")
        )
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
        data_type: str = "users",
    ) -> Dict[str, Any]:
        """Manage next/previous data link(url)

        Args:
            request (Request): current request
            data (Dict[str, Any]): request response data
            nb_total_data (int): total number of resources from DB
            limit (int): limit quantity of returned data
            offset (int): offset of returned data
            data_type (str): type of data, Default to users.

        Returns:
            Dict[str, Any]: response
        """
        _data = {"next": None, "previous": None}
        _data[data_type] = data

        # manage next data
        base = request.scope.get("path")
        if offset + limit < nb_total_data and limit <= nb_total_data:
            next_offset = offset + limit
            _data["next"] = f"{base}?limit={limit}&offset={next_offset}"

        # manage previous data
        if offset - limit >= 0 and limit <= nb_total_data:
            previous_offset = offset - limit
            _data[
                "previous"
            ] = f"{base}?limit={limit}&offset={previous_offset}"
        return _data

    @classmethod
    async def insert_default_data(
        cls: Type[MODEL],
        table: Optional[str] = None,
        data: Optional[dict] = INIT_DATA,
        quantity: int = -1,
    ) -> None:
        """Init tables with some default fake data\n

        Args:
            table (str): specific table to manage, Default to None == all
            data ([dict], optional): data to load. Defaults to INIT_DATA.
            max_data (int, optional): quantity of data to load. \
                Defaults to -1.
        Returns:\n
            None: nothing
        """
        if cls.instance_of(data, list) and table is not None:
            data_length = len(data)
            quantity = (
                quantity if data_length >= quantity >= 1 else data_length
            )
            data = data[:quantity]
            with futures.ProcessPoolExecutor() as executor:
                for user in data:
                    executor.map(await cls._insert_default_data(table, user))
        elif cls.instance_of(data, dict):
            for _table, _data in data.items():
                data_length = len(_data)
                quantity = (
                    quantity if data_length >= quantity >= 1 else data_length
                )
                c_data = _data[:quantity]
                with futures.ProcessPoolExecutor() as executor:
                    for user in c_data:
                        executor.map(
                            await cls._insert_default_data(_table, user)
                        )
        else:
            raise ValueError("Data must be a list or dict")

    @classmethod
    async def _insert_default_data(
        cls: Type[MODEL], table: str, _data: dict
    ) -> Model:
        """Insert data into specific table
            called by insert_default_data function\n

        Args:\n
            table (str): table to modify
            _data (dict): data to insert according to table model\n

        Returns:\n
            Model: inserted instance
        """
        data = {**_data}  # prevent: modify content of argument _data
        # Replace foreign attribute to an instance of foreign model
        if table.lower() == "comment" and cls.instance_of(data["user"], int):
            data["user"] = await Person.filter(id=data["user"]).first()
        elif (
            table.lower() == "vote"
            and cls.instance_of(data["user"], int)
            and cls.instance_of(data["comment"], int)
        ):
            exec("from .api_v1.models.tortoise import Vote")
            data["user"] = await Person.filter(id=data["user"]).first()
            data["comment"] = await Comment.filter(id=data["comment"]).first()

        return await eval(f"{table.capitalize()}.create(**data)")
