from enum import Enum
import json


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

    def __repr__(self):
        return "%s" % (self._value_)

    def __str__(self):
        return self.__repr__()
