from enum import Enum


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

    def __repr__(self):
        return f"{self.__class__.__name__}(gender={self._value_})"

    def __str__(self):
        return self.__repr__()
