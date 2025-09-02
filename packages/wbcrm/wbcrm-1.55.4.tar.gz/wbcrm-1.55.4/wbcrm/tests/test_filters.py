import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.directory.factories.entries import PersonWithEmployerFactory
from wbcore.contrib.directory.models import Company, Person

from wbcrm.filters.signals import choice_noactivity
from wbcrm.viewsets import ActivityViewSet


@pytest.mark.django_db
class TestSpecificFiltersActivities:
    def test_filter_clients_of(self, activity_factory, person_factory):
        person1 = person_factory()
        person2 = person_factory()
        activity_factory(participants=(person_factory(relationship_managers=(person1,)),))
        mvs = ActivityViewSet(kwargs={})
        request = APIRequestFactory().get("")
        request.user = UserFactory(is_active=True, is_superuser=True)
        mvs.request = APIRequestFactory().get("")
        qs = ActivityViewSet.get_model().objects.all()
        assert mvs.filterset_class(request=request).filter_clients_of(qs, "", None) == qs
        assert mvs.filterset_class(request=request).filter_clients_of(qs, "", person1).count() == 1
        assert mvs.filterset_class(request=request).filter_clients_of(qs, "", person2).count() == 0


@pytest.mark.django_db
class TestSpecificFiltersEntries:
    @pytest.mark.parametrize("base_class", [Person, Company])
    def test_choice_noactivity(self, activity_factory, base_class):
        person = PersonWithEmployerFactory()
        company = person.employer.first().employer
        entry_instance = person if base_class == Person else company
        activity = activity_factory(
            creator=person,
            assigned_to=person,
            latest_reviewer=person,
            preceded_by=None,
            participants=(person,),
            companies=(company,),
        )
        number_of_days_since_last_activity = (timezone.now() - activity.period.upper).days + 1
        number_of_days_no_activity = (timezone.now() - activity.period.upper).days - 1
        qs = base_class.objects.all()
        qs_count = qs.count()
        assert choice_noactivity(qs, "", None) == qs
        assert choice_noactivity(qs, "", 0).count() == qs_count - 1
        assert entry_instance not in choice_noactivity(qs, "", 0)
        assert choice_noactivity(qs, "", number_of_days_since_last_activity).count() == qs_count - 1
        assert entry_instance not in choice_noactivity(qs, "", number_of_days_since_last_activity)
        assert choice_noactivity(qs, "", number_of_days_no_activity).count() == qs_count
