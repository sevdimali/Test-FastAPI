from tortoise import models, fields
from .types import Gender


class Person(models.Model):
    is_admin = fields.BooleanField(default=False)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.EmailField(max_length=150, null=True, blank=True)
    gender = fields.CharEnumField(enum_type=Gender, max_length=6)
    date_of_birth = fields.DateField(max_length=50, format="YYYY-mm-dd")
    country_of_birth = fields.CharField(max_length=50)

    def __str__(self):
        return f"[{self.__class__.__name__}] - \
          {self.first_name} {self.last_name}"

    def __repr__(self):
        return f"[{self.__class__.__name__}] - \
          {self.first_name} {self.last_name}"
