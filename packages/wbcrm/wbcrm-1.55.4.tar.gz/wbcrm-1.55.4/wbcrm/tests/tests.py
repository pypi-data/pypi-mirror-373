import pytest
from django.dispatch import receiver
from rest_framework import status
from rest_framework.test import APIRequestFactory
from termcolor import colored
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.test import GenerateTest, default_config
from wbcore.test.mixins import TestViewSet
from wbcore.test.signals import custom_update_kwargs
from wbcore.test.utils import get_data_from_factory, get_kwargs, get_or_create_superuser

from wbcrm.factories import AccountFactory
from wbcrm.viewsets import ActivityParticipantModelViewSet
from wbcrm.viewsets.accounts import (
    ChildAccountAccountModelViewSet,
    InheritedAccountRoleAccountModelViewSet,
)

config = {}
for key, value in default_config.items():
    config[key] = list(
        filter(
            lambda x: x.__module__.startswith("wbcrm")
            and x.__name__
            not in [
                "ActivityParticipantModelViewSet",
                "InheritedAccountRoleAccountModelViewSet",
                "AccountRoleAccountModelViewSet",
                "ChildAccountAccountModelViewSet",
            ],
            value,
        )
    )


@pytest.mark.django_db
@GenerateTest(config)
class TestProject:
    pass


# ActivityParticipantModelViewSet Test
class ActivityParticipantTestViewSet(TestViewSet):
    def _get_mixins_update_data(self, type):
        api_request = APIRequestFactory()
        superuser = get_or_create_superuser()
        obj = self.factory()
        data = get_data_from_factory(obj, self.mvs, superuser=superuser, update=True)
        data["participant"] = PersonFactory().id
        if type == "PATCH":
            request = api_request.patch("", data)
        else:  # "UPDATE"
            request = api_request.put("", data)
        request.user = superuser
        kwargs = get_kwargs(obj, self.mvs, request=request, data=data)
        return obj, request, kwargs, data

    def test_patch_request(self):
        obj, request, kwargs, data = self._get_mixins_update_data("PATCH")
        vs = self.mvs.as_view({"patch": "partial_update"})
        ep = self._get_endpoint_config(request, kwargs, obj)
        ep_update = ep.get_instance_endpoint()
        response = vs(request, **kwargs, data=data)
        if ep_update:
            assert response.status_code == status.HTTP_200_OK, str(response.status_code) + f" == 200 ({response.data})"
            assert response.data.get("instance"), str(response.data.get("instance")) + " should not be empty"
        else:
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED, (
                str(response.status_code) + f" == 405 ({response.data})"
            )
        print(f"- {self.__class__.__name__}:test_patchviewset", colored("PASSED", "green"))  # noqa: T201

    def test_update_request(self):
        obj, request, kwargs, _ = self._get_mixins_update_data("UPDATE")
        vs = self.mvs.as_view({"put": "update"})
        ep = self._get_endpoint_config(request, kwargs, obj)
        ep_update = ep.get_instance_endpoint()
        response = vs(request, **kwargs)
        if ep_update:
            assert response.status_code == status.HTTP_200_OK, str(response.status_code) + f" == 200 ({response.data})"
            assert response.data.get("instance"), str(response.data.get("instance")) + " should not be empty"
        else:
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED, (
                str(response.status_code) + f" == 405 ({response.data})"
            )
        print(f"- {self.__class__.__name__}:test_update_request", colored("PASSED", "green"))  # noqa: T201


class GenerateActivityParticipantTest(GenerateTest):
    def test_modelviewsets(_self, mvs, client):
        my_test = ActivityParticipantTestViewSet(mvs)
        my_test.execute_test_list_endpoint(client)
        my_test.execute_test_detail_endpoint()


@pytest.mark.django_db
@GenerateActivityParticipantTest({"viewsets": [ActivityParticipantModelViewSet]})
class TestActivityParticipant:
    pass


@receiver(custom_update_kwargs, sender=ChildAccountAccountModelViewSet)
def receive_kwargs_child_account(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        parent = AccountFactory.create()
        obj.parent = parent
        obj.save()
        return {"account_id": parent.id}
    return {}


@receiver(custom_update_kwargs, sender=InheritedAccountRoleAccountModelViewSet)
def receive_kwargs_inherited_account_role(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        parent_account = AccountFactory.create()
        child_account = obj.account
        child_account.parent = parent_account
        child_account.save()
        obj.account = parent_account
        obj.save()
        return {"account_id": child_account.id}
