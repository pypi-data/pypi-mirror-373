from collections import OrderedDict
from unittest import TestCase

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.contrib.directory.models import Entry

from wbcrm.factories import ActivityFactory, GroupFactory, ProductFactory
from wbcrm.serializers import ActivityModelSerializer, ProductModelSerializer
from wbcrm.serializers.activities import handle_representation


@pytest.mark.django_db
class TestActivitySerializers(TestCase):
    @pytest.mark.unit
    def test_remove_group_member_from_instance(self):
        group_member_a = PersonFactory()
        group_member_a_entry = Entry.objects.get(id=group_member_a.id)
        group_member_b = PersonFactory()
        group_member_b_entry = Entry.objects.get(id=group_member_b.id)
        group = GroupFactory(members=(group_member_a_entry, group_member_b_entry))
        activity = ActivityFactory(groups=(group,), participants=(group_member_a, group_member_b))

        request = APIRequestFactory().get("")
        request.user = UserFactory()
        request.parser_context = {}
        serializer = ActivityModelSerializer(activity, context={"request": request})
        new_data = {
            "participants": [group_member_b],
        }
        assert serializer.data
        assert group_member_a.id in serializer.data["participants"]
        assert group_member_b.id in serializer.data["participants"]
        with self.assertRaises(ValidationError):
            serializer.validate(new_data)

    @pytest.mark.unit
    def test_remove_all_group_members_from_instance(self):
        group_member_a = PersonFactory()
        group_member_a_entry = Entry.objects.get(id=group_member_a.id)
        group_member_b = PersonFactory()
        group_member_b_entry = Entry.objects.get(id=group_member_b.id)
        group = GroupFactory(members=(group_member_a_entry, group_member_b_entry))
        activity = ActivityFactory(groups=(group,), participants=(group_member_a, group_member_b))

        request = APIRequestFactory().get("")
        request.user = UserFactory()
        request.parser_context = {}
        serializer = ActivityModelSerializer(activity, context={"request": request})
        new_data = {
            "participants": [],
        }
        assert serializer.data
        assert set(serializer.data["participants"]) == {group_member_a.id, group_member_b.id}
        with self.assertRaises(ValidationError):
            serializer.validate(new_data)

    @pytest.mark.unit
    def test_remove_all_group_members_and_groups_from_instance(self):
        group_member_a = PersonFactory()
        group_member_a_entry = Entry.objects.get(id=group_member_a.id)
        group_member_b = PersonFactory()
        group_member_b_entry = Entry.objects.get(id=group_member_b.id)
        group = GroupFactory(members=(group_member_a_entry, group_member_b_entry))
        activity = ActivityFactory(groups=(group,), participants=(group_member_a, group_member_b))

        request = APIRequestFactory().get("")
        request.user = UserFactory()
        request.parser_context = {}
        serializer = ActivityModelSerializer(activity, context={"request": request})
        new_data = {
            "participants": [],
            "groups": [],
        }
        assert serializer.data
        try:
            validated_data = serializer.validate(new_data)
        except DjangoValidationError:
            self.fail("Activity threw error in validation method!")
        else:
            self.assertEqual(validated_data, new_data)

    @pytest.mark.unit
    def test_remove_not_group_membersfrom_instance(self):
        group_member_a = PersonFactory()
        group_member_a_entry = Entry.objects.get(id=group_member_a.id)
        not_group_member = PersonFactory()
        not_group_member_b_entry = Entry.objects.get(id=not_group_member.id)
        group = GroupFactory(members=(group_member_a_entry, not_group_member_b_entry))
        activity = ActivityFactory(groups=(group,), participants=(group_member_a, not_group_member))

        request = APIRequestFactory().get("")
        request.user = UserFactory()
        request.parser_context = {}
        serializer = ActivityModelSerializer(activity, context={"request": request})
        new_data = {
            "participants": [
                group_member_a.id,
            ],
            "groups": [],
        }
        assert serializer.data
        try:
            validated_data = serializer.validate(new_data)
        except DjangoValidationError:
            self.fail("Activity threw error in validation method!")
        else:
            self.assertEqual(validated_data, new_data)


@pytest.mark.django_db
class TestActivitySerializersHelperFunction:
    @pytest.mark.parametrize("is_private, is_confidential", [(True, False), (True, False)])
    def test_handle_representaion(self, is_private, is_confidential):
        test_representation = OrderedDict(
            [
                ("id", "Test-ID"),
                ("title", "Test-Title"),
                ("is_private", is_private),
                ("is_confidential", is_confidential),
                ("foo", "Foo"),
                ("bar", "Bar"),
            ]
        )
        test_representation = handle_representation(test_representation)
        assert test_representation["id"] == "Test-ID"
        if is_private:
            assert test_representation["title"] == "Private Activity"
            assert test_representation["foo"] is None
            assert test_representation["bar"] is None
        elif not is_private and is_confidential:
            assert test_representation["title"] == "Confidential Activity"
            assert test_representation["foo"] is None
            assert test_representation["bar"] is None
        elif not is_private and not is_confidential:
            assert test_representation["title"] == "Test-Title"
            assert test_representation["foo"] == "Foo"
            assert test_representation["bar"] == "Bar"


@pytest.mark.django_db
class TestUtilsSerializers:
    def test_duplicate_company_product(self):
        product = ProductFactory(is_competitor=False)
        serializer = ProductModelSerializer()
        data = {"title": product.title, "is_competitor": product.is_competitor}
        with pytest.raises(DjangoValidationError):
            serializer.validate(data)

    def test_non_duplicate_competitors_product(self):
        product = ProductFactory(is_competitor=False)
        serializer = ProductModelSerializer()
        data = {"title": product.title, "is_competitor": not product.is_competitor}
        assert serializer.validate(data)

    def test_non_duplicate_company_product(self):
        product = ProductFactory(is_competitor=True)
        serializer = ProductModelSerializer()
        data = {"title": product.title, "is_competitor": not product.is_competitor}
        assert serializer.validate(data)

    def test_duplicate_competitors_product(self):
        product = ProductFactory(is_competitor=True)
        serializer = ProductModelSerializer()
        data = {"title": product.title, "is_competitor": product.is_competitor}
        with pytest.raises(DjangoValidationError):
            serializer.validate(data)
