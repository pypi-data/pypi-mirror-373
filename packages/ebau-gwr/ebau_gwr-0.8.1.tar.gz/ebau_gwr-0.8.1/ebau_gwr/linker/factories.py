from factory import Faker
from factory.django import DjangoModelFactory

from . import models


class GWRLinkFactory(DjangoModelFactory):
    eproid = Faker("slug")
    local_id = Faker("slug")
    context = {}

    class Meta:
        model = models.GWRLink
