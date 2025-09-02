import pytest
from wbcore.contrib.directory.typings import Person as PersonDTO

from wbcrm.typings import Activity as ActivityDTO
from wbcrm.typings import ParticipantStatus as ParticipantStatusDTO
from wbcrm.typings import User as UserDTO


@pytest.mark.django_db
class TestDTO:
    @pytest.mark.parametrize("user_id", [None, 1])
    def test_user_comparison(self, user_id):
        user1 = UserDTO(1, {})
        user2 = UserDTO(id=user_id, metadata={})
        if user1.id == user2.id is not None:
            assert user1 == user2
        else:
            assert user1 != user2
        assert user2 is not None

    @pytest.mark.parametrize(
        "id, name, email",
        [
            (None, None, None),
            (None, "test", None),
            (None, "test", "test@test.com"),
            (1, None, None),
            (1, "test", None),
            (1, "test", "test@test.com"),
        ],
    )
    def test_participation_status(self, id, name, email):
        person1 = PersonDTO(1, "test", "test", "test@test.com")
        person2 = PersonDTO(id=id, first_name=name, last_name=name, email=email)

        participant1 = ParticipantStatusDTO(person=person1)
        participant2 = ParticipantStatusDTO(person=person2)
        if (participant1.id == participant2.id is not None) or (
            participant1.person == participant2.person and participant1.activity == participant2.activity
        ):
            assert participant1 == participant2
        else:
            assert participant1 != participant2
        assert participant2 is not None

    @pytest.mark.parametrize(
        "id, title, email",
        [
            (None, None, None),
            (None, "test", None),
            (None, "test", "test@test.com"),
            (1, None, None),
            (1, "test", None),
            (1, "test", "test@test.com"),
        ],
    )
    def test_activity(self, id, title, email):
        activity1 = ActivityDTO(id=1, title="test", metadata={})
        activity2 = ActivityDTO(id=id, title=title, metadata={})
        if activity1.id == activity2.id is not None:
            assert activity1 == activity2
        else:
            assert activity1 != activity2
        assert activity2 is not None
