from unittest.mock import patch

import pytest
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import status
from wbcore.contrib.authentication.factories import UserFactory

from wbcrm.synchronization.activity.admin import UserSyncAdmin

from .fixtures import TestOutlookSyncFixture, msgraph_fixture


@pytest.mark.parametrize(
    "backend, credentials, subscription, tenant_id",
    [
        (False, True, {"id": "fake_id"}, "fake_tenant_id"),
        (True, False, None, None),
        (True, True, None, None),
        (True, True, {"id": "fake_id"}, None),
        (True, True, {"id": "fake_id"}, "fake_tenant_id"),
    ],
)
@patch("wbcrm.synchronization.activity.backends.outlook.backend.MicrosoftGraphAPI")
@pytest.mark.django_db
class TestAdminUserWebhook(TestOutlookSyncFixture):
    def _initialiation(self, mock_msgraph, backend, credentials, subscription, tenant_id, credentials_fixture):
        preferences = global_preferences_registry.manager()
        preferences["wbactivity_sync__sync_backend_calendar"] = preferences[
            "wbactivity_sync__outlook_sync_credentials"
        ] = ""
        if backend:
            preferences["wbactivity_sync__sync_backend_calendar"] = (
                "wbcrm.synchronization.activity.backends.outlook.backend.OutlookSyncBackend"
            )
        mock_msgraph.return_value.status_code = status.HTTP_200_OK
        mock_msgraph.return_value = msgraph_fixture()
        if credentials:
            preferences["wbactivity_sync__outlook_sync_credentials"] = credentials_fixture
            msgraph_fixture._subscription = subscription
            msgraph_fixture.tenant_id = tenant_id
        else:
            mock_msgraph.side_effect = AssertionError("Invalid URL")
        user = UserFactory(is_superuser=True)
        if subscription:
            user.metadata = {"outlook": {"subscription": subscription}}
            user.save()
        return user

    def test_set_web_hook(
        self, mock_msgraph, backend, credentials, subscription, tenant_id, fixture_request, credentials_fixture
    ):
        user = self._initialiation(mock_msgraph, backend, credentials, subscription, tenant_id, credentials_fixture)
        fixture_request.user = user
        assert len([m.message for m in get_messages(fixture_request)]) == 0
        user_admin = UserSyncAdmin(UserFactory, AdminSite())
        user_admin.set_web_hook(fixture_request, get_user_model().objects.filter(id=user.id))
        messages = [m.message for m in get_messages(fixture_request)]
        assert len(messages) == 1
        if backend:
            if credentials:
                if subscription or tenant_id:
                    assert "Operation completed" in messages[0]
                else:
                    assert messages[0] == f"Operation Failed, Outlook TenantId not found for: {user}"
            else:
                assert "Operation Failed, Invalid URL" in messages[0]
        else:
            assert messages[0] == "Operation Failed, No backend set in preferences"

    def test_stop_web_hook(
        self, mock_msgraph, backend, credentials, subscription, tenant_id, fixture_request, credentials_fixture
    ):
        user = self._initialiation(mock_msgraph, backend, credentials, subscription, tenant_id, credentials_fixture)
        fixture_request.user = user
        assert len([m.message for m in get_messages(fixture_request)]) == 0
        user_admin = UserSyncAdmin(UserFactory, AdminSite())
        user_admin.stop_web_hook(fixture_request, get_user_model().objects.filter(id=user.id))
        messages = [m.message for m in get_messages(fixture_request)]
        assert len(messages) == 1
        if backend:
            if subscription:
                if credentials:
                    assert "Operation completed" in messages[0]
                else:
                    assert "Operation Failed, Invalid URL" in messages[0]
            else:
                assert f"Operation Failed, {user} has no active webhook"
        else:
            assert messages[0] == "Operation Failed, No backend set in preferences"

    def test_check_web_hook(
        self, mock_msgraph, backend, credentials, subscription, tenant_id, fixture_request, credentials_fixture
    ):
        user = self._initialiation(mock_msgraph, backend, credentials, subscription, tenant_id, credentials_fixture)
        fixture_request.user = user
        assert len([m.message for m in get_messages(fixture_request)]) == 0
        user_admin = UserSyncAdmin(UserFactory, AdminSite())
        user_admin.check_web_hook(fixture_request, get_user_model().objects.filter(id=user.id))
        messages = [m.message for m in get_messages(fixture_request)]
        assert len(messages) == 1
        if backend:
            if credentials:
                if subscription:
                    assert "Operation completed" in messages[0]
                elif tenant_id:
                    assert (
                        "Operation Failed, Webhook not found. Number of subscriptions found in outlook for"
                        in messages[0]
                    )
                else:
                    assert messages[0] == f"Operation Failed, Webhook not found. TenantId not found for {user}"
            else:
                assert "Operation Failed, Invalid URL" in messages[0]
        else:
            assert messages[0] == "Operation Failed, No backend set in preferences"
