from typing import Optional, Dict, Any, Type, TypeVar
from pydantic import BaseModel

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
        valid_attributes = tuple(
            target_cls.__dict__.get('__fields__', {}).keys())
        if attr.lower() in valid_attributes and order.lower() in ORDERS.keys():
            return f"{ORDERS.get(order.lower(), '')}{attr.lower()}"
        return None
