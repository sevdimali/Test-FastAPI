from enum import Enum
import json


# class EnumEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if type(obj) in PUBLIC_ENUMS.values():
#             return {"__enum__": str(obj)}
#         return json.JSONEncoder.default(self, obj)


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

    def __repr__(self):
        return "%s" % (self._value_)

    def __str__(self):
        return self.__repr__()
