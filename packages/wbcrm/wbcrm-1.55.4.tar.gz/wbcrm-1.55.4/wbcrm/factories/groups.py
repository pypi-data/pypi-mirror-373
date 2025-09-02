import random

import factory
from wbcore.contrib.directory.factories import EntryFactory

from wbcrm.models.groups import Group


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    title = factory.Faker("text", max_nb_chars=64)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return
        elif extracted:
            for member in extracted:
                self.members.add(member)
        else:
            for i in range(1, random.randrange(2, 10)):
                self.members.add(EntryFactory())
