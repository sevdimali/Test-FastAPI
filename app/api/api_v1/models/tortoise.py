from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator

from .types import Gender


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
        return "{!s}(first_name={!s}, last_name={!s},...)".format(
            self.__class__.__name__, self.first_name, self.last_name
        )

    def __repr__(self):
        return "Class({!r})(first_name={!r}, last_name={!r},...)".format(
            self.__class__.__name__, self.first_name, self.last_name
        )


Person_Pydantic = pydantic_model_creator(Person, name="Person")


class Comment(models.Model):
    user = fields.ForeignKeyField("models.Person", related_name="comment")
    added = fields.DatetimeField(auto_now_add=True)
    edited = fields.DatetimeField(auto_now=True)
    content = fields.TextField()

    def __str__(self):
        return "{!s}({!s})".format(self.__class__.__name__, self.content[:10])

    def __repr__(self):
        return "Class({!r})[{!r}]".format(
            self.__class__.__name__,
            self.content[:10],
        )


Comment_Pydantic = pydantic_model_creator(Comment, name="Comment")


class Vote(models.Model):
    comment = fields.ForeignKeyField("models.Comment", related_name="vote")
    user = fields.ForeignKeyField("models.Person", related_name="vote")

    def __str__(self):
        return "{!s}(User={!s}, Comment={!s},...)".format(
            self.__class__.__name__,
            self.user.first_name,
            self.comment.content[:10],
        )

    def __repr__(self):
        return "Class({!r})(User={!r}, Comment={!r},...)".format(
            self.__class__.__name__,
            self.user.first_name,
            self.comment.content[:10],
        )


Vote_Pydantic = pydantic_model_creator(Vote, name="Vote")
