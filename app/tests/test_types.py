from tortoise.contrib import test
from app.api.api_v1.models.types import Gender


class TestTypes(test.TestCase):
    def test__str__repr__(self):
        male = Gender("Male")
        female = Gender("Female")
        male_expected = "{}(gender={})".format(
            male.__class__.__name__, male.value
        )
        female_expected = "{}(gender={})".format(
            female.__class__.__name__, female.value
        )
        assert male.__repr__() == male_expected
        assert male.__str__() == male_expected

        assert female.__repr__() == female_expected
        assert female.__str__() == female_expected
