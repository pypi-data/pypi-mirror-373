import datetime
import random

import factory
import pytz
from dynamic_preferences.registries import global_preferences_registry
from faker import Faker
from wbcore.contrib.authentication.factories import InternalUserFactory
from wbcore.contrib.directory.factories import CompanyFactory, PersonFactory

from wbcrm.models.activities import Activity, ActivityParticipant, ActivityType

fake = Faker()


class ActivityTypeFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=32)
    color = factory.Faker("color")
    score = factory.Iterator([ActivityType.Score.HIGH, ActivityType.Score.MEDIUM, ActivityType.Score.LOW])

    class Meta:
        model = ActivityType
        django_get_or_create = ("title",)


class ActivityTypeCALLFactory(ActivityTypeFactory):
    title = "Call"


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    title = factory.Faker("text", max_nb_chars=64)
    description = factory.Faker("paragraph", nb_sentences=5)
    start = factory.LazyAttribute(lambda _: fake.date_time(tzinfo=pytz.utc))
    end = factory.LazyAttribute(
        lambda _self: _self.start + datetime.timedelta(days=fake.pyint(0, 100), hours=fake.pyint(1, 23))
    )
    disable_participant_check = True
    location = factory.Faker("local_latlng")
    location_longitude = factory.Faker("longitude")
    location_latitude = factory.Faker("latitude")
    created = factory.Faker("date_time", tzinfo=pytz.utc)
    creator = factory.LazyAttribute(lambda _: InternalUserFactory.create().profile)
    latest_reviewer = factory.SubFactory(PersonFactory)
    reviewed_at = factory.Faker("date_time", tzinfo=pytz.utc)
    edited = factory.Faker("date_time", tzinfo=pytz.utc)
    assigned_to = factory.SubFactory(PersonFactory)
    preceded_by = None
    parent_occurrence = None
    propagate_for_all_children = False
    recurrence_end = None
    recurrence_count = None
    repeat_choice = Activity.ReoccuranceChoice.NEVER
    type = factory.SubFactory(ActivityTypeFactory)
    item_type = "wbcrm.Activity"

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for participant in extracted:
                self.participants.add(participant)

    @factory.post_generation
    def companies(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for company in extracted:
                self.companies.add(company)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)

    @factory.post_generation
    def entities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for entity in extracted:
                self.entities.add(entity)


class RecurringActivityFactory(ActivityFactory):
    repeat_choice = random.choice(list(filter(lambda x: x != "NEVER", Activity.ReoccuranceChoice.names)))
    recurrence_count = 3


class ActivityCompanyFactory(ActivityFactory):
    @factory.post_generation
    def companies(self, create, extracted, **kwargs):
        # Create company
        company = CompanyFactory()
        # Set global config main_company=company.id
        global_preferences_registry.manager()["directory__main_company"] = company.id
        global_preferences = global_preferences_registry.manager()
        assert global_preferences
        self.companies.add(company)


class ActivityPersonFactory(ActivityFactory):
    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        # Create person
        person = PersonFactory()
        self.participants.add(person)


class ActivityParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityParticipant

    participant = factory.SubFactory(PersonFactory)
    activity = factory.SubFactory(ActivityFactory)
