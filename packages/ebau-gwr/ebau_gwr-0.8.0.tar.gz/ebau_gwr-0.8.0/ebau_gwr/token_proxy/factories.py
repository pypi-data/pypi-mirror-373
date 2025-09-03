from factory import Faker
from factory.django import DjangoModelFactory

from . import models


class HousingStatCredsFactory(DjangoModelFactory):
    owner = "admin"
    username = Faker("first_name")
    password = Faker("password")
    municipality = Faker("random_int")
    group = Faker("random_int")

    class Meta:
        model = models.HousingStatCreds
