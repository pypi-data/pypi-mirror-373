import pytest
from django.db.models import Q
from django.forms.models import model_to_dict
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.messages import InMemoryMessageStorage

from wbcrm.models.activities import Activity
from wbcrm.models.recurrence import Recurrence
from wbcrm.preferences import (
    get_maximum_allowed_recurrent_date,
    get_recurrence_maximum_count,
)
from wbcrm.serializers import ActivityModelSerializer
from wbcrm.viewsets import ActivityViewSet


@pytest.mark.django_db
class RecurrenceFixture:
    @pytest.fixture
    def occurrence_fixture(self, activity_factory):
        return activity_factory(repeat_choice=Recurrence.ReoccuranceChoice.DAILY, recurrence_count=3, preceded_by=None)

    @pytest.fixture
    def occurrences_fixture(self, occurrence_fixture):
        return Activity.objects.filter(Q(id=occurrence_fixture.id) | Q(parent_occurrence=occurrence_fixture)).order_by(
            "start"
        )


@pytest.mark.django_db
class TestRecurrenceModel(RecurrenceFixture):
    @pytest.mark.parametrize("repeat_choice", [*list(Recurrence.ReoccuranceChoice)])
    def test_is_recurrent(self, repeat_choice, recurring_activity_factory):
        act = recurring_activity_factory(repeat_choice=repeat_choice)
        assert act.is_recurrent == (act.repeat_choice != Recurrence.ReoccuranceChoice.NEVER)

    def test_recurring_activity_without_end(self, recurring_activity_factory):
        act = recurring_activity_factory(repeat_choice=Recurrence.ReoccuranceChoice.DAILY, recurrence_count=None)
        occurrences = Activity.objects.filter(parent_occurrence=act)
        assert occurrences.count() <= get_recurrence_maximum_count()
        assert (
            occurrences.order_by("period__startswith").last().period.lower.date()
            <= get_maximum_allowed_recurrent_date()
        )

    def test_is_root(self, occurrences_fixture):
        for occurrence in occurrences_fixture:
            assert occurrence.is_root == (occurrence.is_recurrent and not occurrence.parent_occurrence)

    def test_is_leaf(self, occurrences_fixture):
        for occurrence in occurrences_fixture:
            assert occurrence.is_leaf == (occurrence.is_recurrent and not occurrence.next_occurrence)

    def test_next_occurrence(self, occurrences_fixture):
        last_row = len(occurrences_fixture) - 1
        for row, occurrence in enumerate(occurrences_fixture):
            if row == last_row:
                assert occurrence.next_occurrence is None
            else:
                assert occurrence.next_occurrence == occurrences_fixture[row + 1]

    def test_previous_occurrence(self, occurrences_fixture):
        for row, occurrence in enumerate(occurrences_fixture):
            if row == 0:
                assert occurrence.previous_occurrence is None
            else:
                assert occurrence.previous_occurrence == occurrences_fixture[row - 1]

    # def test_get_recurrent_valid_children(self, occurrences_fixture):
    #     parent = occurrences_fixture[0]
    #     assert parent.get_recurrent_valid_children().count() == len(occurrences_fixture[1:])
    #     assert parent.get_recurrent_invalid_children().count() == 0
    #     occurrences_fixture[1].cancel()
    #     assert parent.get_recurrent_valid_children().count() == len(occurrences_fixture[1:]) - 1
    #     assert parent.get_recurrent_invalid_children().count() == 1
    #     occurrences_fixture[2].review()
    #     assert parent.get_recurrent_valid_children().count() == len(occurrences_fixture[1:]) - 2
    #     assert parent.get_recurrent_invalid_children().count() == 2
    #     occurrences_fixture[3].finish()
    #     assert parent.get_recurrent_valid_children().count() == len(occurrences_fixture[1:]) - 3
    #     assert parent.get_recurrent_invalid_children().count() == 3

    @pytest.mark.parametrize("position, only_next_occurrence", [(0, False), (0, True), (1, False), (1, True)])
    def test_forward_deletion(self, occurrences_fixture, only_next_occurrence, position):
        nb_activities = Activity.objects.count()
        occ = occurrences_fixture[position]
        next_occurrences = occurrences_fixture.filter(period__startswith__gt=occ.period.lower)
        next_occ = next_occurrences.first()
        nb_next_occurrences = next_occurrences.count()
        assert nb_activities == 4
        if only_next_occurrence:
            occ.forward_deletion([next_occ.id])
            assert Activity.objects.count() == nb_activities - 1 == 3
        else:
            occ.forward_deletion()
            assert Activity.objects.count() == nb_activities - nb_next_occurrences

    def test_claim_parent_hood(self, occurrences_fixture, activity_factory):
        single_activity = activity_factory(repeat_choice=Recurrence.ReoccuranceChoice.NEVER, preceded_by=None)
        single_activity.claim_parent_hood()
        assert single_activity.is_root is False

        for occurrence in occurrences_fixture:
            occurrence.claim_parent_hood()
            if occurrence.is_leaf:
                assert occurrence.is_root is False
            else:
                assert occurrence.is_root is True

    @pytest.mark.parametrize("position, propagation", [(0, False), (0, True), (1, False), (1, True)])
    def test_delete(self, position, propagation, occurrences_fixture):
        occ = occurrences_fixture[position]
        next_occurrences = occurrences_fixture.filter(period__startswith__gt=occ.period.lower)
        next_occ = next_occurrences.first()
        nb_next_occurrences = next_occurrences.count()
        assert Activity.objects.count() == len(occurrences_fixture) == 4
        assert nb_next_occurrences == 3 - position
        Activity.objects.filter(id=occ.id).update(propagate_for_all_children=propagation)
        occ.refresh_from_db()
        was_root = True if occ.is_root else False
        occ.delete()
        if propagation:
            assert Activity.objects.count() == 3 - nb_next_occurrences
        else:
            assert Activity.objects.count() == 3
            next_occ.refresh_from_db()
            next_occ.is_root == was_root

    @pytest.mark.parametrize("include_self", [False, True])
    def test_get_occurrence_start_datetimes(self, occurrences_fixture, include_self, activity_factory):
        single_activity = activity_factory(repeat_choice=Recurrence.ReoccuranceChoice.NEVER, preceded_by=None)
        assert not single_activity._get_occurrence_start_datetimes(include_self)
        assert single_activity.is_root is False

        start_dates = occurrences_fixture[0]._get_occurrence_start_datetimes(include_self)
        nb_occurrences = len(occurrences_fixture) if include_self else len(occurrences_fixture[1:])
        assert len(start_dates) == nb_occurrences

    def test_create_recurrence_child(self, occurrence_fixture):
        nb_activities = Activity.objects.count()
        start_dates = occurrence_fixture._get_occurrence_start_datetimes()
        new_occurrence = occurrence_fixture._create_recurrence_child(start_dates[0])
        assert Activity.objects.count() == nb_activities + 1
        fields = [
            "assigned_to",
            "all_day",
            "conference_room",
            "creator",
            "description",
            "disable_participant_check",
            "importance",
            "visibility",
            "location",
            "location_longitude",
            "location_latitude",
            "recurrence_end",
            "recurrence_count",
            "reminder_choice",
            "repeat_choice",
            "title",
            "type",
        ]
        assert new_occurrence.period.lower == start_dates[0]
        assert occurrence_fixture.duration == new_occurrence.duration
        assert new_occurrence.parent_occurrence == occurrence_fixture
        assert model_to_dict(occurrence_fixture, fields=fields) == model_to_dict(new_occurrence, fields=fields)

    def test_generate_occurrences(self, occurrence_fixture, activity_factory):
        single_activity = activity_factory(repeat_choice=Recurrence.ReoccuranceChoice.NEVER, preceded_by=None)
        assert len(single_activity.generate_occurrences()) == 0
        children = occurrence_fixture.generate_occurrences().order_by("period__startswith")
        assert (
            len(children)
            == len(occurrence_fixture._get_occurrence_start_datetimes())
            == occurrence_fixture.recurrence_count
        )
        assert set(children) == set(occurrence_fixture.child_activities.all())
        assert children[0].is_root is False
        assert len(children[0].generate_occurrences(allow_reclaiming_root=False)) == 0
        assert children[0].is_root is False
        assert len(children[0].generate_occurrences()) == children[0].recurrence_count > 0
        assert children[0].is_root is True
        assert children[0].child_activities.all().count() == children[0].recurrence_count
        assert occurrence_fixture.child_activities.all().count() == 0

    @pytest.mark.parametrize("position_occurrence, propagation", [(0, False), (0, True), (1, False), (1, True)])
    def test_forward_change(self, occurrences_fixture, propagation, position_occurrence, activity_factory):
        activity = occurrences_fixture[position_occurrence]
        nb_next_occurrences = len(occurrences_fixture[position_occurrence + 1 :])
        if activity.is_root:
            assert len(activity.get_recurrent_valid_children()) == nb_next_occurrences
        else:
            assert len(activity.get_recurrent_valid_children()) == 0
        was_root = activity.is_root
        other_activity = activity_factory(preceded_by=None)
        Activity.objects.filter(id=activity.id).update(
            title=other_activity.title, propagate_for_all_children=propagation
        )
        activity.refresh_from_db()
        activity.forward_change()
        activity.refresh_from_db()
        assert activity.is_root == (propagation or was_root)
        assert activity.propagate_for_all_children is False
        if propagation or was_root:
            assert len(activity.get_recurrent_valid_children()) == nb_next_occurrences
        else:
            assert len(activity.get_recurrent_valid_children()) == 0


@pytest.mark.django_db
class TestRecurrenceSerializers(RecurrenceFixture):
    def test_next_occurrence_no_period(self, activity_factory):
        activity = activity_factory(
            period=None, repeat_choice=Recurrence.ReoccuranceChoice.DAILY, recurrence_count=3, preceded_by=None
        )
        request = APIRequestFactory().get("")
        user = UserFactory()
        request.user = user
        request.parser_context = {}
        serializer = ActivityModelSerializer(activity, context={"request": request})
        assert serializer.next_occurrence(activity, request, user)

    def test_previous_occurrence_no_period(self, activity_factory):
        activity = activity_factory(
            period=None, repeat_choice=Recurrence.ReoccuranceChoice.DAILY, recurrence_count=3, preceded_by=None
        )
        request = APIRequestFactory().get("")
        user = UserFactory()
        request.user = user
        request.parser_context = {}
        serializer = ActivityModelSerializer(activity, context={"request": request})
        assert not serializer.previous_occurrence(activity, request, user)

    def test_next_occurrence(self, occurrences_fixture):
        request = APIRequestFactory().get("")
        user = UserFactory()
        request.user = user
        request.parser_context = {}
        last_row = len(occurrences_fixture) - 1
        for row, occurrence in enumerate(occurrences_fixture):
            serializer_occurrence = ActivityModelSerializer(occurrence, context={"request": request})
            if row == last_row:
                assert not serializer_occurrence.next_occurrence(occurrence, request, user)
            else:
                assert serializer_occurrence.next_occurrence(occurrence, request, user) == {
                    "next_occurrence": f"http://testserver/api/crm/activity/{occurrences_fixture[row+1].id}/"
                }

    def test_previous_occurrence(self, occurrences_fixture):
        request = APIRequestFactory().get("")
        user = UserFactory()
        request.user = user
        request.parser_context = {}
        for row, occurrence in enumerate(occurrences_fixture):
            serializer_occurrence = ActivityModelSerializer(occurrence, context={"request": request})
            if row == 0:
                assert not serializer_occurrence.previous_occurrence(occurrence, request, user)
            else:
                assert serializer_occurrence.previous_occurrence(occurrence, request, user) == {
                    "previous_occurrence": f"http://testserver/api/crm/activity/{occurrences_fixture[row-1].id}/"
                }


@pytest.mark.django_db
class TestRecurrenceViewSets(RecurrenceFixture):
    def test_next_and_previous_activity_button_present_for_recurring_activity(
        self, occurrences_fixture, super_user_factory
    ):
        request = APIRequestFactory().get("")
        request.user = super_user_factory()
        request._messages = InMemoryMessageStorage(request)
        view = ActivityViewSet.as_view({"get": "retrieve"})
        for row, occurrence in enumerate(occurrences_fixture):
            response = view(request, pk=occurrence.id).render()
            if occurrence.is_root:
                assert response.data["instance"]["_additional_resources"]["next_occurrence"].endswith(
                    str(occurrences_fixture[row + 1].id) + "/"
                )
                assert "previous_occurrence" not in response.data["instance"]["_additional_resources"]
            elif occurrence.is_leaf:
                assert "next_occurrence" not in response.data["instance"]["_additional_resources"]
                assert response.data["instance"]["_additional_resources"]["previous_occurrence"].endswith(
                    str(occurrences_fixture[row - 1].id) + "/"
                )
            else:
                assert response.data["instance"]["_additional_resources"]["next_occurrence"].endswith(
                    str(occurrences_fixture[row + 1].id) + "/"
                )
                assert response.data["instance"]["_additional_resources"]["previous_occurrence"].endswith(
                    str(occurrences_fixture[row - 1].id) + "/"
                )
