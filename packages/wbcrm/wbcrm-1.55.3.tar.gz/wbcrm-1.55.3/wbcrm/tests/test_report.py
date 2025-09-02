import pytest
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import UserFactory

from wbcrm.report.activity_report import create_report, create_report_and_send


@pytest.mark.django_db
class TestSpecificReport:
    def test_create_report(self, person_factory, activity_factory):
        person = person_factory()
        activity = activity_factory(participants=(person,))
        report = create_report(person.id, activity.start, activity.end)
        assert report
        assert report.getvalue()

    def test_create_report_and_send(self, person_factory):
        request = APIRequestFactory().get("")
        request.user = UserFactory(is_active=True, is_superuser=True)
        person = person_factory()
        create_report_and_send(request.user.profile.id, person.id)
