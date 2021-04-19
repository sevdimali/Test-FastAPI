from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator

from api.api_v1.models.types import Gender


class Person(models.Model):
    is_admin = fields.BooleanField(default=False)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=150, null=True, blank=True)
    gender = fields.CharEnumField(enum_type=Gender, max_length=6)
    avatar = fields.CharField(max_length=255, null=True, blank=True)
    job = fields.CharField(max_length=50, null=True, blank=True)
    company = fields.CharField(null=True, blank=True, max_length=50)
    date_of_birth = fields.DateField()
    country_of_birth = fields.CharField(max_length=50)

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.first_name} {self.last_name})"

    def __repr__(self):
        return self.__str__()


Person_Pydantic = pydantic_model_creator(Person, name="Person")
# PersonIn_Pydantic = pydantic_model_creator(
#     Person, name="PersonIn", exclude_readonly=True)
