from typing import Dict

ORDERS: Dict[str, str] = {
    "asc": "",
    "desc": "-"
}


class API_functools:

    @classmethod
    def get_or_default(cls, list_el, index, default):
        if len(list_el) <= index:
            return default

        return list_el[index]

    @classmethod
    def instance_of(cls, el, class_expected):
        return el.__class__.__name__.lower() == class_expected.__name__.lower()

    @classmethod
    def valid_order(cls, target_cls, sort):
        attr, order = sort.split(":")
        valid_attributes = tuple(
            target_cls.__dict__.get('__fields__', {}).keys())
        if attr.lower() in valid_attributes and order.lower() in ORDERS.keys():
            return f"{ORDERS.get(order.lower(), '')}{attr.lower()}"
        return None
