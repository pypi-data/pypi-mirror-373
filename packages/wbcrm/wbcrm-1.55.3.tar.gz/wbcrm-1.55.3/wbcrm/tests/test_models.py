from datetime import timedelta

import pytest
from django.apps import apps
from django.utils import timezone
from django_fsm import TransitionNotAllowed
from dynamic_preferences.registries import global_preferences_registry
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.authentication.factories import (
    AuthenticatedPersonFactory,
    UserFactory,
)
from wbcore.contrib.directory.factories import PersonWithEmployerFactory
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.icons import WBIcon

from wbcrm.models import Activity, add_employer_to_activities


@pytest.mark.django_db
class TestSpecificModelsActivities:
    def test_get_color_map(self, activity_factory):
        activity1 = activity_factory()
        assert activity1.Status.get_color_map()

    def test_get_minutes_correspondance(self, activity_factory):
        activity1 = activity_factory()
        assert activity1.ReminderChoice.get_minutes_correspondance("NEVER")
        assert activity1.ReminderChoice.get_minutes_correspondance("EVENT_TIME") == 0
        assert activity1.ReminderChoice.get_minutes_correspondance("MINUTES_5")
        assert activity1.ReminderChoice.get_minutes_correspondance("MINUTES_15")
        assert activity1.ReminderChoice.get_minutes_correspondance("MINUTES_30")
        assert activity1.ReminderChoice.get_minutes_correspondance("HOURS_1")
        assert activity1.ReminderChoice.get_minutes_correspondance("HOURS_2")
        assert activity1.ReminderChoice.get_minutes_correspondance("HOURS_12")
        assert activity1.ReminderChoice.get_minutes_correspondance("WEEKS_1")

    def test_str(self, activity_factory):
        assert activity_factory(preceded_by=None).__str__()

    def test_get_participants(self, activity_factory, person_factory, internal_user_factory, company_factory):
        person1 = person_factory()
        company1 = company_factory()
        if apps.is_installed("wbhuman_resources"):
            from wbhuman_resources.factories import EmployeeHumanResourceFactory

            person2 = AuthenticatedPersonFactory(employers=(company1,))
            EmployeeHumanResourceFactory(profile=person2)
        else:
            person2 = person_factory(employers=(company1,))
            u = internal_user_factory.create()
            u.profile = person2
            u.save()
        activity1 = activity_factory(participants=(person1,))
        assert activity1.get_participants().count() == 1
        assert activity1.get_participants()[0] == person1

    def test_get_activities_for_user(self, activity_factory):
        activity0 = activity_factory(preceded_by=None)
        user = UserFactory(is_active=True, is_superuser=True)
        qs = activity0.get_activities_for_user(user)
        assert qs.count() == 1

        user2 = UserFactory(is_active=True)
        qs2 = activity0.get_activities_for_user(user2)
        assert qs2.count() == 0

    def test_add_group_to_activity(self, activity_factory, group_factory, person_factory, company_factory):
        activity_participant_a = person_factory()
        group_member_a = person_factory()
        member_a_entry = Entry.objects.get(pk=group_member_a.pk)
        group_member_b = company_factory()
        member_b_entry = Entry.objects.get(pk=group_member_b.pk)
        group_a = group_factory(members=(member_a_entry, member_b_entry))

        activity = activity_factory(
            participants=[
                activity_participant_a,
            ]
        )
        assert activity.participants.filter(pk=activity_participant_a.pk).exists()
        assert not activity.participants.filter(pk=group_member_a.pk).exists()
        assert not activity.companies.filter(pk=group_member_b.pk).exists()

        activity.groups.set((group_a,))
        activity.save()

        assert activity.participants.filter(pk=activity_participant_a.pk).exists()
        assert activity.participants.filter(pk=group_member_a.pk).exists()
        assert activity.companies.filter(pk=group_member_b.pk).exists()

    def test_remove_group_to_activity(self, activity_factory, group_factory, person_factory, company_factory):
        group_member_a = person_factory()
        group_member_b = person_factory()
        group_member_c = person_factory()
        group_member_d = company_factory()
        group_a = group_factory(members=(group_member_a.entry_ptr, group_member_c.entry_ptr, group_member_d.entry_ptr))
        group_b = group_factory(members=(group_member_b.entry_ptr, group_member_c.entry_ptr))

        activity = activity_factory(groups=[group_a, group_b])

        assert activity.participants.filter(pk=group_member_a.pk).exists()
        assert activity.participants.filter(pk=group_member_b.pk).exists()
        assert activity.participants.filter(pk=group_member_c.pk).exists()
        assert activity.companies.filter(pk=group_member_d.pk).exists()

        activity.groups.remove(group_a.pk)
        activity.save()

        assert not activity.participants.filter(pk=group_member_a.pk).exists()
        assert activity.participants.filter(pk=group_member_b.pk).exists()
        assert activity.participants.filter(pk=group_member_c.pk).exists()
        assert not activity.companies.filter(pk=group_member_d.pk).exists()

    def test_add_participants_employer(self, activity_factory, person_factory):
        person_a = PersonWithEmployerFactory()
        person_b = person_factory()
        employer_a = person_a.employer.get(primary=True).employer
        activity_a = activity_factory(participants=(person_a, person_b))
        assert person_a in activity_a.participants.all()
        assert person_b in activity_a.participants.all()
        assert employer_a in activity_a.companies.all()

    def test_add_participants_employer_on_update(self, activity_factory, person_factory):
        person_a = PersonWithEmployerFactory()
        person_b = person_factory()
        employer_a = person_a.employer.get(primary=True).employer
        activity_a = activity_factory(participants=(person_b,))
        assert person_a not in activity_a.participants.all()
        assert person_b in activity_a.participants.all()
        assert employer_a not in activity_a.companies.all()
        activity_a.participants.set([person_a, person_b])
        assert person_a in activity_a.participants.all()
        assert person_b in activity_a.participants.all()
        assert employer_a in activity_a.companies.all()

    def test_add_participants_employer_to_canceled_activity(self, activity_factory, person_factory):
        person_a = PersonWithEmployerFactory()
        person_b = person_factory()
        activity_a = activity_factory(participants=(person_a, person_b), status=Activity.Status.CANCELLED)
        assert set(activity_a.participants.all()) == {person_a, person_b}

    def test_participant_cannot_attend_digitally(
        self, activity_participant_factory, activity_factory, conference_room_factory
    ):
        room = conference_room_factory(is_videoconference_capable=False)
        activity = activity_factory(conference_room=room)
        obj = activity_participant_factory(activity=activity)
        with pytest.raises(TransitionNotAllowed):
            obj.attendsdigitally()

    def test_participant_can_attend_digitally(self, activity_participant_factory, activity_factory):
        activity = activity_factory()
        obj = activity_participant_factory(activity=activity)
        obj.attendsdigitally()
        assert True

    def test_get_casted_calendar_item(self, activity_factory):
        activity = activity_factory()
        calendar_item = CalendarItem.objects.get(id=activity.id)
        assert calendar_item.get_casted_calendar_item() == activity

    def test_add_employer_to_activities(
        self, activity_factory, employer_employee_relationship_factory, person_factory
    ):
        employee = person_factory()
        act1 = activity_factory(
            status=Activity.Status.PLANNED, start=timezone.now() + timedelta(1), participants=[employee]
        )
        act2 = activity_factory(
            status=Activity.Status.REVIEWED, start=timezone.now() + timedelta(1), participants=[employee]
        )
        act3 = activity_factory(
            status=Activity.Status.PLANNED, start=timezone.now() - timedelta(1), participants=[employee]
        )
        eer = employer_employee_relationship_factory(employee=employee)
        add_employer_to_activities(eer.id)
        act1.refresh_from_db()
        act2.refresh_from_db()
        act3.refresh_from_db()
        assert eer.employer in act1.companies.all()
        assert eer.employer not in act2.companies.all()
        assert eer.employer not in act3.companies.all()
        assert eer.employer.entry_ptr in act1.entities.all()
        assert eer.employer.entry_ptr not in act2.entities.all()
        assert eer.employer.entry_ptr not in act3.entities.all()

    def test_set_color_icons(self, activity_factory, calendar_item_factory):
        activity = activity_factory(type__icon=WBIcon.EURO.icon)
        assert activity.color == activity.type.color
        assert activity.icon == activity.type.icon

        activity_type = activity.type
        activity_type.icon = WBIcon.LOCATION.icon
        activity_type.color = "#42f444"
        activity_type.save()
        activity.refresh_from_db()
        assert activity.color == activity_type.color
        assert activity.icon == activity_type.icon

        calendar_item = calendar_item_factory()
        assert calendar_item.color
        assert calendar_item.icon

    def test_main_company_removed_from_m2m(self, activity, company_factory):
        external_company = company_factory.create()
        activity.companies.add(external_company)
        assert set(activity.companies.all()) == {
            external_company,
        }

        main_company = company_factory.create()
        global_preferences_registry.manager()["directory__main_company"] = main_company.id
        activity.companies.add(main_company)
        assert set(activity.companies.all()) == {
            external_company,
        }
