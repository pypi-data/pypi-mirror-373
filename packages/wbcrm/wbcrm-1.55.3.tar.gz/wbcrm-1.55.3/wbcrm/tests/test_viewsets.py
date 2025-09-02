import pytest
from django.contrib.messages import get_messages
from django.test import Client
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.authentication.factories import (
    InternalUserFactory,
    SuperUserFactory,
)
from wbcore.contrib.authentication.models import Permission
from wbcore.messages import InMemoryMessageStorage
from wbcore.test.utils import get_data_from_factory, get_kwargs, get_model_factory

from wbcrm.models import Activity, ActivityParticipant
from wbcrm.viewsets import (
    ActivityParticipantModelViewSet,
    ActivityTypeModelViewSet,
    ActivityViewSet,
    ProductModelViewSet,
)

# =====================================================================================================================
#                                                 TESTING ACTIVITY VIEWSETS
# =====================================================================================================================


@pytest.mark.django_db
class TestActivityModelViewSet:
    api_factory = APIRequestFactory()

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_random_cannot_see_private_item(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        item = activity_factory(visibility=CalendarItem.Visibility.PRIVATE, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == item.id
        assert response.data["results"][0]["title"] == "Private Activity"

    # =================================================================================================================
    #                                            TESTING CONFIDENTIAL CALENDAR ITEMS
    # =================================================================================================================

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_manager_can_see_confidential_item(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        permission = Permission.objects.get(codename="administrate_confidential_items")
        user.user_permissions.add(permission)
        item = activity_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == item.id
        assert response.data["results"][0]["title"] == item.title

    @pytest.mark.parametrize("mvs", [ActivityParticipantModelViewSet])
    def test_create_activity_participant(self, mvs, activity_participant_factory):
        # Arrange
        activity_participant = activity_participant_factory()
        superuser = InternalUserFactory(is_active=True, is_superuser=True)
        data = get_data_from_factory(activity_participant, mvs, delete=True, superuser=superuser)
        request = self.api_factory.post("", data=data)
        request.user = superuser
        kwargs = {"activity_id": activity_participant.activity.id}
        view = mvs.as_view({"post": "create"})
        # Act
        response = view(request, **kwargs)
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("instance")
        assert response.data["instance"]["participant"] == activity_participant.participant.id
        assert (
            response.data["instance"]["participation_status"]
            == activity_participant.participation_status
            == ActivityParticipant.ParticipationStatus.PENDING_INVITATION
        )
        assert response.data["instance"]["activity"] == activity_participant.activity.id

    # @pytest.mark.parametrize("mvs", [ActivityParticipantModelViewSet])
    def test_get_activity_participant_instance(self, activity_participant_factory):
        # Arranged
        activity_participant = activity_participant_factory.create()
        user = InternalUserFactory(is_active=True, is_superuser=True)
        client = APIClient()
        url = reverse(
            "wbcrm:activity-participant-detail",
            kwargs={"pk": activity_participant.id, "activity_id": activity_participant.activity.id},
        )
        client.force_authenticate(user)
        response = client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.data["instance"]["id"] == activity_participant.id

    @pytest.mark.parametrize("mvs", [ActivityParticipantModelViewSet])
    def test_get_activity_participant_list(self, mvs, activity_participant_factory):
        # Arrange
        activity_participant_1 = activity_participant_factory()
        activity_participant_factory(activity=activity_participant_1.activity)
        activity_participant_factory(activity=activity_participant_1.activity)
        request = self.api_factory.get("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        view = mvs.as_view({"get": "list"})
        kwargs = {"activity_id": activity_participant_1.activity.id}
        # Act
        response = view(request, **kwargs)
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert not response.data.get("instance")
        assert response.data.get("results")
        assert response.data["results"]
        assert len(response.data["results"]) == 3

    @pytest.mark.parametrize("mvs", [ActivityParticipantModelViewSet])
    def test_delete_activity_participant_instance(self, mvs, activity_participant_factory):
        # Arrange
        activity_participant = activity_participant_factory()
        request = self.api_factory.delete("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        view = mvs.as_view({"delete": "destroy"})
        kwargs = {"activity_id": activity_participant.activity.id}
        # Act
        response = view(request, pk=activity_participant.id, **kwargs)
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize("mvs", [ActivityParticipantModelViewSet])
    def test_partial_update_activity_participant_instance(self, mvs, activity_participant_factory, person_factory):
        # Arrange
        activity_participant = activity_participant_factory()
        new_participant = person_factory()
        superuser = InternalUserFactory(is_active=True, is_superuser=True)
        request = self.api_factory.patch("", data={"participant": new_participant.id})
        request.user = superuser
        view = mvs.as_view({"patch": "partial_update"})
        kwargs = {"activity_id": activity_participant.activity.id}
        # Act
        response = view(request, pk=activity_participant.id, **kwargs)
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["instance"]["participant"] == new_participant.id
        assert not response.data["instance"]["participant"] == activity_participant.participant.id

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_msg_missing_company(
        self,
        mvs,
        activity_factory,
        person_factory,
        company_factory,
    ):
        company_a = company_factory()
        company_b = company_factory()
        person = person_factory()
        person.employers.set([company_a, company_b])
        activity = activity_factory(participants=[person], companies=None, disable_participant_check=False)
        request = APIRequestFactory().get("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        request.query_params = {}
        request._messages = InMemoryMessageStorage(request)
        mvs.request = request
        mvs.kwargs = get_kwargs(activity, ActivityViewSet, request)
        mvs.kwargs["pk"] = activity.pk
        mvs().add_messages(request, instance=activity)
        assert len(get_messages(request)._messages) > 0

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_msg_missing_participant(
        self,
        mvs,
        activity_factory,
        person_factory,
        company_factory,
    ):
        company = company_factory()
        person = person_factory()
        person.employers.set([company])
        company.employees.set([person])
        activity = activity_factory(participants=None, companies=[company], disable_participant_check=False)
        activity.disable_participant_check = False
        activity.save()
        request = APIRequestFactory().put("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        request.query_params = {}
        request._messages = InMemoryMessageStorage(request)
        mvs.request = request
        mvs.kwargs = get_kwargs(activity, ActivityViewSet, request)
        mvs.kwargs["pk"] = activity.pk
        mvs().add_messages(request, instance=activity)
        assert len(get_messages(request)._messages) > 0

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_msg_missing_participant_no_check(
        self,
        mvs,
        activity_factory,
        person_factory,
        company_factory,
    ):
        company = company_factory()
        person = person_factory()
        person.employers.set([company])
        company.employees.set([person])
        internal_user = InternalUserFactory.create()
        activity = activity_factory(
            participants=None, creator=internal_user.profile, companies=[company], disable_participant_check=True
        )
        request = APIRequestFactory().put("")
        request.user = internal_user
        request.query_params = {}
        request._messages = InMemoryMessageStorage(request)
        mvs.request = request
        mvs.kwargs = get_kwargs(activity, ActivityViewSet, request)
        mvs.kwargs["pk"] = activity.pk
        mvs().add_messages(request, instance=activity)
        assert len(get_messages(request)._messages) == 0

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_msg_missing_participant_and_company(
        self,
        mvs,
        activity_factory,
        person_factory,
        company_factory,
    ):
        company_a = company_factory()
        company_b = company_factory()
        company_c = company_factory()
        person_a = person_factory()
        person_b = person_factory()
        person_a.employers.set([company_a])
        person_b.employers.set([company_b, company_c])
        company_a.employees.set([person_a])
        company_b.employees.set([person_b])
        activity = activity_factory(participants=[person_b], companies=[company_a], disable_participant_check=False)
        request = APIRequestFactory().patch("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        request.query_params = {}
        request._messages = InMemoryMessageStorage(request)
        mvs.request = request
        mvs.kwargs = get_kwargs(activity, ActivityViewSet, request)
        mvs.kwargs["pk"] = activity.pk
        mvs().add_messages(request, instance=activity)
        assert len(get_messages(request)._messages) > 0

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_get_messages(self, mvs, activity_factory, recurring_activity_factory, person_factory):
        request = APIRequestFactory().get("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        person1 = person_factory()
        obj = recurring_activity_factory(
            status=Activity.Status.PLANNED, repeat_choice=Activity.ReoccuranceChoice.DAILY, participants=(person1,)
        )
        activity_factory(start=obj.start, end=obj.end, participants=(person1,))
        request.query_params = {}
        request._messages = InMemoryMessageStorage(request)
        mvs.request = request
        mvs.kwargs = get_kwargs(obj, ActivityViewSet, request)
        mvs.kwargs["pk"] = obj.pk
        mvs().add_messages(request, instance=obj)
        assert len(get_messages(request)._messages) > 0

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_create_activity(self, mvs, activity_factory):
        # Arrange
        activity = activity_factory()
        user = InternalUserFactory(is_active=True, is_superuser=True)
        data = get_data_from_factory(activity, mvs, delete=True, superuser=user)
        request = self.api_factory.post("", data=data)
        request.user = user
        kwargs = {}
        view = mvs.as_view({"post": "create"})
        # Act
        response = view(request, kwargs).render()
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("instance")
        assert response.data["instance"]["title"] == activity.title

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_create_reviewed_activity(self, mvs, activity_factory):
        # Arrange
        activity = activity_factory(result="A Test Review For This Activity!")
        user = SuperUserFactory()
        data = get_data_from_factory(activity, mvs, delete=True, superuser=user)
        request = self.api_factory.post("", data=data)
        request.user = user
        kwargs = {}
        view = mvs.as_view({"post": "create"})
        # Act
        response = view(request, kwargs).render()
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("instance")
        assert response.data["instance"]["title"] == activity.title
        assert response.data["instance"]["result"] == activity.result

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_get_activity_instance(self, mvs, activity_factory):
        # Arrange
        activity = activity_factory()
        request = self.api_factory.get("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        view = mvs.as_view({"get": "retrieve"})
        # Act
        response = view(request, pk=activity.id).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.data["instance"]["id"] == activity.id

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_get_activity_list(self, mvs, activity_factory):
        # Arrange
        activity_factory.create_batch(3, preceded_by=None)
        request = self.api_factory.get("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        view = mvs.as_view({"get": "list"})
        # Act
        response = view(request).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert not response.data.get("instance")
        assert response.data.get("results")
        assert response.data["results"]
        assert len(response.data["results"]) == 3

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_delete_activity_instance(self, mvs, activity_factory):
        # Arrange
        activity = activity_factory()
        request = self.api_factory.delete("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        view = mvs.as_view({"delete": "destroy"})
        # Act
        response = view(request, pk=activity.id).render()
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_update_activity_instance(self, mvs, activity_factory):
        activity_old = activity_factory()
        activity_new = activity_factory()
        user = InternalUserFactory(is_active=True, is_superuser=True)
        data = get_data_from_factory(activity_new, mvs, update=True, superuser=user)
        request = self.api_factory.put("", data=data)
        request.user = user
        view = mvs.as_view({"put": "update"})
        response = view(request, pk=activity_old.id).render()
        assert response.status_code == status.HTTP_200_OK
        assert not activity_old.title == activity_new.title
        assert response.data["instance"]["id"] == activity_old.id

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_update_reviewed_activity_instance(self, mvs, activity_factory):
        user = SuperUserFactory()
        client = Client()
        client.force_login(user)
        activity: Activity = activity_factory()
        updated_result = activity.result + "Foo Bar"
        data = get_data_from_factory(activity, mvs, update=True, superuser=user)
        data["result"] = updated_result
        assert activity.result != updated_result
        update_url: str = reverse("wbcrm:activity-detail", args=[activity.pk])
        response = client.put(update_url, data, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        activity.refresh_from_db()
        assert activity.result == updated_result

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_partial_update_activity_instance(self, mvs, activity_factory):
        activity = activity_factory()
        activity.title
        user = InternalUserFactory(is_active=True, is_superuser=True)
        request = self.api_factory.patch("", data={"title": "New Title"})
        request.user = user
        view = mvs.as_view({"patch": "partial_update"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data["instance"]["id"] == activity.id

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_partial_update_reviewed_activity_instance(self, mvs, activity_factory):
        user = SuperUserFactory()
        client = Client()
        client.force_login(user)
        activity: Activity = activity_factory()
        updated_result = activity.result + "Foo Bar"
        update_url: str = reverse("wbcrm:activity-detail", args=[activity.pk])

        assert activity.result != updated_result
        response = client.patch(update_url, {"result": updated_result}, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        activity.refresh_from_db()
        assert activity.result == updated_result

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_conference_room_capacity_error_message(
        self, mvs, activity_factory, person_factory, conference_room_factory
    ):
        room = conference_room_factory(capacity=2)
        p1 = person_factory()
        p2 = person_factory()
        p3 = person_factory()
        activity = activity_factory(conference_room=room, participants=[p1, p2, p3])
        request = self.api_factory.get("")
        request._messages = InMemoryMessageStorage(request)
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        view = mvs.as_view({"get": "retrieve"})
        # Act
        response = view(request, pk=activity.id).render()
        assert len(response.data["messages"]) == 1

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_conference_room_capacity_no_error_message(
        self, mvs, activity_factory, person_factory, conference_room_factory
    ):
        room = conference_room_factory(capacity=3)
        p1 = person_factory()
        p2 = person_factory()
        p3 = person_factory()
        activity = activity_factory(conference_room=room, participants=[p1, p2, p3])
        request = self.api_factory.get("")
        request._messages = InMemoryMessageStorage(request)
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        view = mvs.as_view({"get": "retrieve"})
        response = view(request, pk=activity.id).render()
        assert len(response.data["messages"]) == 0

    # =================================================================================================================
    #                                            TESTING PRIVATE ACTIVITIES
    # =================================================================================================================

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_assignee_can_see_private_activity_list(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(
            visibility=CalendarItem.Visibility.PRIVATE, assigned_to=user.profile, preceded_by=None
        )
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == activity.id
        assert response.data["results"][0]["title"] == activity.title
        assert response.data["results"][0]["type"] == activity.type.id
        assert response.data["results"][0]["participants"] == list(
            activity.participants.all().values_list("id", flat=True)
        )
        assert response.data["results"][0]["companies"] == list(activity.companies.all().values_list("id", flat=True))
        assert response.data["results"][0]["groups"] == list(activity.groups.all().values_list("id", flat=True))
        assert response.data["results"][0]["edited"] is not None
        assert response.data["results"][0]["created"] is not None
        assert response.data["results"][0]["description"] == activity.description
        assert response.data["results"][0]["latest_reviewer"] == activity.latest_reviewer.id
        if activity.status not in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]:
            assert response.data["results"][0]["_additional_resources"] is not None

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_participant_can_see_private_activity_list(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(
            visibility=CalendarItem.Visibility.PRIVATE, participants=[user.profile.id], preceded_by=None
        )
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == activity.id
        assert response.data["results"][0]["title"] == activity.title
        assert response.data["results"][0]["type"] == activity.type.id
        assert response.data["results"][0]["participants"] == list(
            activity.participants.all().values_list("id", flat=True)
        )
        assert response.data["results"][0]["companies"] == list(activity.companies.all().values_list("id", flat=True))
        assert response.data["results"][0]["groups"] == list(activity.groups.all().values_list("id", flat=True))
        assert response.data["results"][0]["edited"] is not None
        assert response.data["results"][0]["created"] is not None
        assert response.data["results"][0]["description"] == activity.description
        assert response.data["results"][0]["result"] == activity.result
        assert response.data["results"][0]["latest_reviewer"] == activity.latest_reviewer.id
        if activity.status not in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]:
            assert response.data["results"][0]["_additional_resources"] is not None

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_random_cannot_see_private_activity_list(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(visibility=CalendarItem.Visibility.PRIVATE, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == activity.id
        assert response.data["results"][0]["title"] == "Private Activity"
        assert response.data["results"][0]["type"] is None
        assert response.data["results"][0]["edited"] is None
        assert response.data["results"][0]["created"] is None
        assert response.data["results"][0]["description"] is None
        assert response.data["results"][0]["result"] is None
        assert response.data["results"][0]["latest_reviewer"] is None
        assert response.data["results"][0]["participants"] is not None
        assert response.data["results"][0]["_participants"] is not None
        assert response.data["results"][0]["companies"] is not None
        assert response.data["results"][0]["_companies"] is not None
        assert response.data["results"][0]["groups"] is not None
        assert response.data["results"][0]["_groups"] is not None
        assert response.data["results"][0]["_additional_resources"] is None

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_assignee_can_see_private_activity_instance(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(
            visibility=CalendarItem.Visibility.PRIVATE, assigned_to=user.profile, preceded_by=None
        )
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "retrieve"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.data["instance"]["id"] == activity.id
        assert response.data["instance"]["title"] == activity.title
        assert response.data["instance"]["participants"] == list(
            activity.participants.all().values_list("id", flat=True)
        )
        assert response.data["instance"]["type"] == activity.type.id
        assert response.data["instance"]["companies"] == list(activity.companies.all().values_list("id", flat=True))
        assert response.data["instance"]["groups"] == list(activity.groups.all().values_list("id", flat=True))
        assert response.data["instance"]["edited"] is not None
        assert response.data["instance"]["created"] is not None
        assert response.data["instance"]["description"] == activity.description
        assert response.data["instance"]["result"] == activity.result
        assert response.data["instance"]["latest_reviewer"] == activity.latest_reviewer.id
        if activity.status not in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]:
            assert response.data["instance"]["_additional_resources"] is not None
        assert response.data["instance"]["all_day"] == activity.all_day
        assert response.data["instance"]["assigned_to"] == activity.assigned_to.id
        assert response.data["instance"]["conference_room"] == activity.conference_room
        assert response.data["instance"]["disable_participant_check"] == activity.disable_participant_check
        assert response.data["instance"]["creator"] == activity.creator.id
        assert response.data["instance"]["importance"] == activity.importance
        assert response.data["instance"]["online_meeting"] == activity.online_meeting
        assert response.data["instance"]["reminder_choice"] == activity.reminder_choice

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_participant_can_see_private_activity_instance(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(
            visibility=CalendarItem.Visibility.PRIVATE, participants=[user.profile.id], preceded_by=None
        )
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "retrieve"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.data["instance"]["id"] == activity.id
        assert response.data["instance"]["title"] == activity.title
        assert response.data["instance"]["participants"] == list(
            activity.participants.all().values_list("id", flat=True)
        )
        assert response.data["instance"]["type"] == activity.type.id
        assert response.data["instance"]["companies"] == list(activity.companies.all().values_list("id", flat=True))
        assert response.data["instance"]["groups"] == list(activity.groups.all().values_list("id", flat=True))
        assert response.data["instance"]["edited"] is not None
        assert response.data["instance"]["created"] is not None
        assert response.data["instance"]["description"] == activity.description
        assert response.data["instance"]["result"] == activity.result
        assert response.data["instance"]["latest_reviewer"] == activity.latest_reviewer.id
        if activity.status not in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]:
            assert response.data["instance"]["_additional_resources"] is not None
        assert response.data["instance"]["all_day"] == activity.all_day
        assert response.data["instance"]["assigned_to"] == activity.assigned_to.id
        assert response.data["instance"]["conference_room"] == activity.conference_room
        assert response.data["instance"]["disable_participant_check"] == activity.disable_participant_check
        assert response.data["instance"]["creator"] == activity.creator.id
        assert response.data["instance"]["importance"] == activity.importance
        assert response.data["instance"]["online_meeting"] == activity.online_meeting
        assert response.data["instance"]["reminder_choice"] == activity.reminder_choice

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_random_cannot_see_private_activity_instance(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(visibility=CalendarItem.Visibility.PRIVATE, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "retrieve"})
        response = view(request, pk=activity.id).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.data["instance"]["id"] == activity.id
        assert response.data["instance"]["title"] == "Private Activity"
        assert response.data["instance"]["participants"] is not None
        assert response.data["instance"]["_participants"] is not None
        assert response.data["instance"]["companies"] is not None
        assert response.data["instance"]["_companies"] is not None
        assert response.data["instance"]["groups"] is not None
        assert response.data["instance"]["_groups"] is not None
        assert response.data["instance"]["assigned_to"] is not None
        assert response.data["instance"]["_assigned_to"] is not None
        assert response.data["instance"]["creator"] is not None
        assert response.data["instance"]["_creator"] is not None
        assert response.data["instance"]["type"] is None
        assert response.data["instance"]["_type"] is None
        assert response.data["instance"]["edited"] is None
        assert response.data["instance"]["created"] is None
        assert response.data["instance"]["description"] is None
        assert response.data["instance"]["result"] is None
        assert response.data["instance"]["latest_reviewer"] is None
        assert response.data["instance"]["_latest_reviewer"] is None
        assert response.data["instance"]["_additional_resources"] is None
        assert response.data["instance"]["all_day"] is None
        assert response.data["instance"]["conference_room"] is None
        assert response.data["instance"]["disable_participant_check"] is None
        assert response.data["instance"]["importance"] is None
        assert response.data["instance"]["location"] is None
        assert response.data["instance"]["location_latitude"] is None
        assert response.data["instance"]["location_longitude"] is None
        assert response.data["instance"]["online_meeting"] is None
        assert response.data["instance"]["reminder_choice"] is None
        assert response.data["instance"]["reviewed_at"] is None

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_private_instance_not_deleteable(self, mvs, activity_factory, user_factory):
        activity = activity_factory(visibility=CalendarItem.Visibility.PRIVATE, preceded_by=None)
        request = self.api_factory.delete("")
        request.user = user_factory(is_active=True, is_superuser=True)
        view = mvs.as_view({"delete": "destroy"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_private_instance_deleteable_for_participant(self, mvs, activity_factory, user_factory):
        superuser = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(
            visibility=CalendarItem.Visibility.PRIVATE, participants=[superuser.profile.id], preceded_by=None
        )
        request = self.api_factory.delete("")
        request.user = superuser
        view = mvs.as_view({"delete": "destroy"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_private_instance_deleteable_for_assignee(self, mvs, activity_factory, user_factory):
        superuser = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(
            visibility=CalendarItem.Visibility.PRIVATE, assigned_to=superuser.profile, preceded_by=None
        )
        request = self.api_factory.delete("")
        request.user = superuser
        view = mvs.as_view({"delete": "destroy"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # =================================================================================================================
    #                                            TESTING CONFIDENTIAL ACTIVITIES
    # =================================================================================================================

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_manager_can_see_confidential_activity_list(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        permission = Permission.objects.get(codename="administrate_confidential_items")
        user.user_permissions.add(permission)
        activity = activity_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == activity.id
        assert response.data["results"][0]["title"] == activity.title
        assert response.data["results"][0]["participants"] == list(
            activity.participants.all().values_list("id", flat=True)
        )
        assert response.data["results"][0]["companies"] == list(activity.companies.all().values_list("id", flat=True))
        assert response.data["results"][0]["groups"] == list(activity.groups.all().values_list("id", flat=True))
        assert response.data["results"][0]["type"] == activity.type.id
        assert response.data["results"][0]["edited"] is not None
        assert response.data["results"][0]["created"] is not None
        assert response.data["results"][0]["description"] == activity.description
        assert response.data["results"][0]["latest_reviewer"] == activity.latest_reviewer.id
        if activity.status not in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]:
            assert response.data["results"][0]["_additional_resources"] is not None

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_random_cannot_see_confidential_activity_list(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "list"})
        response = view(request).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == activity.id
        assert response.data["results"][0]["title"] == "Confidential Activity"
        assert response.data["results"][0]["participants"] is None
        assert response.data["results"][0]["companies"] is None
        assert response.data["results"][0]["groups"] is None
        assert response.data["results"][0]["type"] is None
        assert response.data["results"][0]["edited"] is None
        assert response.data["results"][0]["created"] is None
        assert response.data["results"][0]["description"] is None
        assert response.data["results"][0]["result"] is None
        assert response.data["results"][0]["latest_reviewer"] is None
        assert response.data["results"][0]["_additional_resources"] is None

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_manager_can_see_confidential_activity_instance(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        permission = Permission.objects.get(codename="administrate_confidential_items")
        user.user_permissions.add(permission)
        activity = activity_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "retrieve"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.data["instance"]["id"] == activity.id
        assert response.data["instance"]["title"] == activity.title
        assert response.data["instance"]["participants"] == list(
            activity.participants.all().values_list("id", flat=True)
        )
        assert response.data["instance"]["type"] == activity.type.id
        assert response.data["instance"]["companies"] == list(activity.companies.all().values_list("id", flat=True))
        assert response.data["instance"]["groups"] == list(activity.groups.all().values_list("id", flat=True))
        assert response.data["instance"]["edited"] is not None
        assert response.data["instance"]["created"] is not None
        assert response.data["instance"]["description"] == activity.description
        assert response.data["instance"]["result"] == activity.result
        assert response.data["instance"]["latest_reviewer"] == activity.latest_reviewer.id
        if activity.status not in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]:
            assert response.data["instance"]["_additional_resources"] is not None
        assert response.data["instance"]["all_day"] == activity.all_day
        assert response.data["instance"]["assigned_to"] == activity.assigned_to.id
        assert response.data["instance"]["conference_room"] == activity.conference_room
        assert response.data["instance"]["disable_participant_check"] == activity.disable_participant_check
        assert response.data["instance"]["creator"] == activity.creator.id
        assert response.data["instance"]["importance"] == activity.importance
        assert response.data["instance"]["online_meeting"] == activity.online_meeting
        assert response.data["instance"]["reminder_choice"] == activity.reminder_choice

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_random_cannot_see_confidential_activity_instance(self, mvs, activity_factory, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        activity = activity_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL, preceded_by=None)
        request = self.api_factory.get("")
        request.user = user
        view = mvs.as_view({"get": "retrieve"})
        response = view(request, pk=activity.id).render()
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.data["instance"]["id"] == activity.id
        assert response.data["instance"]["title"] == "Confidential Activity"
        assert response.data["instance"]["participants"] is None
        assert response.data["instance"]["_participants"] is None
        assert response.data["instance"]["type"] is None
        assert response.data["instance"]["_type"] is None
        assert response.data["instance"]["companies"] is None
        assert response.data["instance"]["_companies"] is None
        assert response.data["instance"]["groups"] is None
        assert response.data["instance"]["_groups"] is None
        assert response.data["instance"]["edited"] is None
        assert response.data["instance"]["created"] is None
        assert response.data["instance"]["description"] is None
        assert response.data["instance"]["result"] is None
        assert response.data["instance"]["latest_reviewer"] is None
        assert response.data["instance"]["_latest_reviewer"] is None
        assert response.data["instance"]["_additional_resources"] is None
        assert response.data["instance"]["all_day"] is None
        assert response.data["instance"]["assigned_to"] is None
        assert response.data["instance"]["conference_room"] is None
        assert response.data["instance"]["disable_participant_check"] is None
        assert response.data["instance"]["creator"] is None
        assert response.data["instance"]["importance"] is None
        assert response.data["instance"]["location"] is None
        assert response.data["instance"]["location_latitude"] is None
        assert response.data["instance"]["location_longitude"] is None
        assert response.data["instance"]["online_meeting"] is None
        assert response.data["instance"]["reminder_choice"] is None
        assert response.data["instance"]["reviewed_at"] is None
        assert response.data["instance"]["_assigned_to"] is None
        assert response.data["instance"]["_creator"] is None

    @pytest.mark.parametrize("mvs", [ActivityViewSet])
    def test_confidential_instance_not_deleteable(self, mvs, activity_factory, internal_user_factory, user_factory):
        employee = internal_user_factory().profile
        user = user_factory(is_active=True)
        employee.user_account = user
        for permission in Permission.objects.exclude(codename="administrate_confidential_items"):
            user.user_permissions.add(permission)
        global_preferences_registry.manager()["directory__main_company"] = employee.employers.first().id
        activity = activity_factory(visibility=CalendarItem.Visibility.CONFIDENTIAL, preceded_by=None)
        request = self.api_factory.delete("")
        request.user = user
        view = mvs.as_view({"delete": "destroy"})
        response = view(request, pk=activity.id).render()
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# =====================================================================================================================
#                                                  TESTING ENTRY VIEWSETS
# =====================================================================================================================


# # =====================================================================================================================
# #                                                  TESTING UTILS VIEWSETS
# # =====================================================================================================================


@pytest.mark.django_db
class TestUtilsViewSets:
    api_factory = APIRequestFactory()

    @pytest.mark.parametrize(
        "mvs",
        [
            ActivityTypeModelViewSet,
            ProductModelViewSet,
        ],
    )
    def test_get_utils(self, mvs):
        request = self.api_factory.get("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        factory.create_batch(3)
        vs = mvs.as_view({"get": "list"})
        response = vs(request)
        assert response.data.get("results")
        assert not response.data.get("instance")
        assert len(response.data.get("results")) == 3
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "mvs",
        [
            ActivityTypeModelViewSet,
            ProductModelViewSet,
        ],
    )
    def test_retrieve_utils(self, mvs):
        request = self.api_factory.get("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        vs = mvs.as_view({"get": "retrieve"})
        response = vs(request, pk=obj.id)
        assert response.data.get("instance")
        assert not response.data.get("results")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "mvs",
        [
            ActivityTypeModelViewSet,
            ProductModelViewSet,
        ],
    )
    def test_post_utils(self, mvs):
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        super_user = InternalUserFactory(is_active=True, is_superuser=True)
        data = get_data_from_factory(obj, mvs, superuser=super_user, delete=True)
        request = self.api_factory.post("", data=data)
        request.user = super_user
        kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"post": "create"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "mvs",
        [
            ActivityTypeModelViewSet,
            ProductModelViewSet,
        ],
    )
    def test_delete_utils(self, mvs):
        request = self.api_factory.delete("")
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"delete": "destroy"})
        response = vs(request, **kwargs, pk=obj.pk)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        "mvs",
        [
            ActivityTypeModelViewSet,
            ProductModelViewSet,
        ],
    )
    def test_put_utils(self, mvs):
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        old_obj = factory()
        new_obj = factory()
        user = InternalUserFactory(is_active=True, is_superuser=True)
        data = get_data_from_factory(new_obj, mvs, superuser=user, delete=True)
        request = APIRequestFactory().put("", data=data)
        request.user = user
        vs = mvs.as_view({"put": "update"})
        response = vs(request, pk=old_obj.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["instance"]["title"] == new_obj.title
        assert not response.data["instance"]["title"] == old_obj.title

    @pytest.mark.parametrize(
        "mvs",
        [
            ActivityTypeModelViewSet,
            ProductModelViewSet,
        ],
    )
    def test_patch_utils(self, mvs):
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        request = APIRequestFactory().patch("", data={"title": "New Title"})
        request.user = InternalUserFactory(is_active=True, is_superuser=True)
        vs = mvs.as_view({"patch": "partial_update"})
        response = vs(request, pk=obj.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["instance"]["title"] == "New Title"
