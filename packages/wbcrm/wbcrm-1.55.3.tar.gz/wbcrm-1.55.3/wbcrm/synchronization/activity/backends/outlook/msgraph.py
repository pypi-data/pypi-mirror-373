import json
from contextlib import suppress
from datetime import date, timedelta
from urllib.parse import urlparse

import pandas as pd
import requests
from django.contrib.sites.models import Site
from django.db.utils import ProgrammingError
from django.http import HttpResponse
from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import status

from .parser import parse


class MicrosoftGraphAPI:
    def __init__(self):
        with suppress(ProgrammingError):
            global_preferences = global_preferences_registry.manager()
            if (credentials := global_preferences["wbactivity_sync__outlook_sync_credentials"]) and (
                serivce_account_file := json.loads(credentials)
            ):
                self.authority = serivce_account_file.get("authority")
                self.client_id = serivce_account_file.get("client_id")
                self.client_secret = serivce_account_file.get("client_secret")
                self.token_endpoint = serivce_account_file.get("token_endpoint")
                self.notification_url = serivce_account_file.get("notification_url")
                self.graph_url = serivce_account_file.get("graph_url")

                if global_preferences["wbactivity_sync__outlook_sync_access_token"] == "":
                    self._get_access_token()
                else:
                    # try to get a data in the api (i.e list of applications), update the token if it is expired
                    self.applications()
            else:
                self.authority = None
                self.client_id = None
                self.client_secret = None
                self.token_endpoint = None
                self.notification_url = None
                self.graph_url = None

    def _get_administrator_consent(self) -> HttpResponse:
        url = f"{self.authority}/adminconsent?client_id={self.client_id}&state=12345&redirect_uri={self.notification_url}"
        if urlparse(url):
            response = self._query(url, access_token=False)
            if response:
                return response
            else:
                raise ValueError("get administrator consent does not return response 200")
        else:
            raise ValueError("Invalid URL")

    def _get_access_token(self) -> str | None:
        # Get administrator consent
        self._get_administrator_consent()
        # Get an access token
        url = f"{self.authority}{self.token_endpoint}"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "scope": "https://graph.microsoft.com/.default",
            "client_secret": self.client_secret,
        }

        response = self._query(url, method="POST", data=payload, is_json=False, access_token=False)
        data = None
        if response:
            if response.json():
                data = response.json().get("access_token")
                global_preferences = global_preferences_registry.manager()
                global_preferences["wbactivity_sync__outlook_sync_access_token"] = data
        else:
            raise ValueError(response, response.json())
        return data

    def _subscribe(
        self, resource: str, change_type: str, minutes: int = 4230, raise_error: bool = False
    ) -> dict | None:
        subscription_data: dict = {
            "changeType": change_type,
            "notificationUrl": self.notification_url,
            "resource": resource,
            "clientState": global_preferences_registry.manager()["wbactivity_sync__outlook_sync_client_state"],
            "latestSupportedTlsVersion": "v1_2",
        }
        if minutes:
            # maximum time of subscription 4230 minutes (under 3 days)
            date = timezone.now() + timedelta(minutes=minutes)
            date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            subscription_data["expirationDateTime"] = date
        url = f"{self.graph_url}/subscriptions"
        response = self._query(url, method="POST", data=json.dumps(subscription_data))
        data = None
        if response and response.status_code == status.HTTP_201_CREATED:
            if response.json():
                data = parse(response.json(), scalar_value=True)
                if data and isinstance(data, list):
                    data = data[0]
        elif raise_error:
            raise ValueError(response, response.json())
        return data

    def _unsubscribe(self, subscription_id: str) -> HttpResponse:
        url = f"{self.graph_url}/subscriptions/{subscription_id}"
        return self._query(url, method="DELETE")

    def _renew_subscription(self, subscription_id: str, minutes: int = 4230, raise_error: bool = False) -> dict | None:
        url = f"{self.graph_url}/subscriptions/{subscription_id}"
        date = timezone.now() + timedelta(minutes=minutes)
        date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        data = {"expirationDateTime": date}
        response = self._query(url, method="PATCH", data=json.dumps(data))
        data = None
        if response and response.status_code == status.HTTP_200_OK:
            if response.json():
                data = parse(response.json(), scalar_value=True)
                if data and isinstance(data, list):
                    data = data[0]
        elif raise_error:
            raise ValueError(response, response.json())
        return data

    def subscriptions(self) -> list[dict]:
        url = f"{self.graph_url}/subscriptions"
        response = self._query(url)
        data = []
        if response:
            if datum := response.json():
                data = parse(datum.get("value"))
                url = datum.get("@odata.nextLink")
                while url:
                    response = self._query(url)
                    if datum := response.json():
                        data += parse(datum.get("value"))
                        url = datum.get("@odata.nextLink")
                    else:
                        url = None
        else:
            raise ValueError(response, response.json())
        return data

    def subscription(self, subscription_id: str, raise_error: bool = False) -> dict | None:
        url = f"{self.graph_url}/subscriptions/{subscription_id}"
        response = self._query(url)
        data = None
        if response and response.status_code == status.HTTP_200_OK:
            if response.json():
                data = parse(response.json(), scalar_value=True)
                if data and isinstance(data, list):
                    data = data[0]
        elif raise_error:
            raise ValueError(response, response.json())
        return data

    def applications(self) -> dict | None:
        # List of applications in MS graph
        url = f"{self.graph_url}/applications"
        response = self._query(url)
        data = None
        if response:
            if datum := response.json():
                data = parse(datum.get("value"))
                url = datum.get("@odata.nextLink")
                while url:
                    response = self._query(url)
                    if datum := response.json():
                        data += parse(datum.get("value"))
                        url = datum.get("@odata.nextLink")
                    else:
                        url = None
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            self._get_access_token()
            if response := self._query(url):
                data = response.json()
        else:
            raise ValueError(response, response.json())
        return data

    def user(self, email: str, raise_error: bool = False) -> dict | None:
        query_params = {"$select": "id, userPrincipalName, displayName"}
        url = f"{self.graph_url}/users/{email}"
        response = self._query(url, params=query_params)
        data = None
        if response:
            if response.json():
                data = parse(response.json(), scalar_value=True)
                if data and isinstance(data, list):
                    data = data[0]
        elif raise_error:
            raise ValueError(response, response.json())
        return data

    def users(self, filter_params: bool = True) -> dict:
        query_params = {
            "$select": "id,displayName,businessPhones,mobilePhone, userPrincipalName, mail,email, mailNickname, givenName, surname, imAddresses"
        }
        url = f"{self.graph_url}/users"
        if filter_params:
            response = self._query(url, params=query_params)
        else:
            response = self._query(url)
        data = None
        if response:
            data = parse(response.json().get("value"))
        else:
            raise ValueError(response, response.json())
        return data

    def get_tenant_id(self, email: str) -> str | None:
        try:
            if msuser := self.user(email):
                return msuser.get("id", None)
        except Exception:
            pass
        return None

    def delta_changes_events(self, tenant_id: str, minutes: int) -> list:
        start = (timezone.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (timezone.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"{self.graph_url}/users/{tenant_id}/calendarView/delta?startdatetime={start}&enddatetime={end}"
        response = self._query(url)
        datum = []
        if response:
            if datum := response.json():
                _value = datum.get("value")
                external_event_list = parse(_value)
                url = datum.get("@odata.deltaLink")
                while _value:
                    response = self._query(url)
                    datum = response.json()
                    _value = datum.get("value")
                    external_event_list += parse(_value)
                    url = datum.get("@odata.deltaLink")
            else:
                raise ValueError(response, response.json())
        return datum

    def create_event(self, tenant_id: str, event_body: dict) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events"
        return self._query_create(url, event_body)

    def delete_event(self, tenant_id: str, external_id: str) -> None:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}"
        return self._query(url, method="DELETE")

    def update_event(self, tenant_id: str, external_id: str, event_body: dict) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}"
        return self._query_update(url, event_body)

    def get_event(
        self, tenant_id: str, external_id: str, extension: bool = False, extension_id: str = ""
    ) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}"
        if extension:
            extension_id = (
                extension_id if extension_id else ".".join(reversed(Site.objects.get_current().domain.split(".")))
            )
            url += f"?$expand=Extensions($filter=Id eq '{extension_id}')"
        return self._query_get(url)

    def update_or_create_extension_event(
        self, tenant_id: str, external_id: str, extension_body: dict, extension_id: str = ""
    ):
        extension_id = (
            extension_id if extension_id else ".".join(reversed(Site.objects.get_current().domain.split(".")))
        )
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/extensions"
        data = {"@odata.type": "microsoft.graph.openTypeExtension", "extensionName": extension_id, **extension_body}
        if self.get_extension_event(tenant_id, external_id, extension_id):
            url += f"/{extension_id}"
            return self._query_update(url, data)
        else:
            return self._query_create(url, data)

    def get_extension_event(self, tenant_id: str, external_id: str, extension_id: str = "") -> dict | None:
        extension_id = (
            extension_id if extension_id else ".".join(reversed(Site.objects.get_current().domain.split(".")))
        )
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/extensions/{extension_id}"
        return self._query_get(url)

    def delete_extension_event(self, tenant_id: str, external_id: str, extension_id: str = "") -> None:
        extension_id = (
            extension_id if extension_id else ".".join(reversed(Site.objects.get_current().domain.split(".")))
        )
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/extensions/{extension_id}"
        return self._query(url, method="DELETE")

    def forward_event(self, tenant_id: str, external_id: str, participants: list) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/forward"
        data = {
            "ToRecipients": participants,
        }
        return self._query_create(url, data)

    def get_event_by_uid(self, tenant_id: str, uid: str) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events?$filter=uid eq '{uid}'"
        event = list_data[0] if (list_data := self._query_get_list(url)) else None
        return event

    def get_list_events(self, tenant_id: str) -> list:
        url = f"{self.graph_url}/users/{tenant_id}/events"
        return self._query_get_list(url)

    def get_instances_event(self, tenant_id: str, external_id: str, start: str | date, end: str | date) -> list:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/instances?startDateTime={start}&endDateTime={end}"
        list_data = self._query_get_list(url)
        return list_data if list_data else []

    def get_instances_event_by_resource(self, resource: str, start: str | date, end: str | date) -> list:
        url = f"{self.graph_url}/{resource}/instances?startDateTime={start}&endDateTime={end}"
        list_data = self._query_get_list(url)
        return list_data if list_data else []

    def get_event_by_resource(self, resource: str, extension: bool = False, extension_id: str = "") -> dict | None:
        url = f"{self.graph_url}/{resource}"
        if extension:
            extension_id = (
                extension_id if extension_id else ".".join(reversed(Site.objects.get_current().domain.split(".")))
            )
            url += f"?$expand=Extensions($filter=Id eq '{extension_id}')"
        return self._query_get(url)

    def delete_event_by_resource(self, resource: str) -> dict | None:
        url = f"{self.graph_url}/{resource}"
        return self._query(url, method="DELETE")

    def tentatively_accept_event(self, tenant_id: str, external_id: str) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/tentativelyAccept"
        data = {"sendResponse": False}
        return self._query_create(url, data)

    def decline_event(self, tenant_id: str, external_id: str) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/decline"
        data = {"sendResponse": False}
        return self._query_create(url, data)

    def accept_event(self, tenant_id: str, external_id: str) -> dict | None:
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/accept"
        data = {"sendResponse": False}
        return self._query_create(url, data)

    def cancel_event(self, tenant_id: str, external_id: str) -> dict | None:
        # Only the organizer can cancel an event
        url = f"{self.graph_url}/users/{tenant_id}/events/{external_id}/cancel"
        data = {}
        return self._query_create(url, data)

    def _query_get(self, url: str, raise_error: bool = False) -> dict | None:
        response = self._query(url)
        data = None
        if response.status_code < 400:
            if response.json():
                data = parse(pd.json_normalize(response.json()))
                if data and isinstance(data, list):
                    data = data[0]
        elif raise_error:
            raise ValueError(response, response.json())
        return data

    def _query_get_list(self, url: str, raise_error: bool = False) -> list:
        response = self._query(url)
        datum = []
        if response:
            if (result := response.json()) and (value := result.get("value")):
                datum = parse(pd.json_normalize(value))
                next_url: str | None = result.get("@odata.nextLink")
                while next_url:
                    response = self._query(next_url)
                    if (result := response.json()) and (value := result.get("value")):
                        datum += parse(pd.json_normalize(value))
                        next_url = result.get("@odata.nextLink")
                    else:
                        next_url = None
        elif raise_error:
            raise ValueError(response, response.json())
        return datum

    def _query_create(self, url: str, event_data: dict) -> dict | None:
        response = self._query(url, method="POST", data=json.dumps(event_data))
        data = None
        if response.status_code < 400:
            try:
                if response.json():
                    data = parse(pd.json_normalize(response.json()))
                    if data and isinstance(data, list):
                        data = data[0]
            except requests.exceptions.InvalidJSONError:
                pass
        else:
            raise ValueError(response, response.__dict__)
        return data

    def _query_update(self, url: str, event_data: dict) -> dict | None:
        response = self._query(url, method="PATCH", data=json.dumps(event_data))
        data = None
        if response:
            if response.json():
                data = parse(pd.json_normalize(response.json()))
        else:
            if response.status_code not in [status.HTTP_503_SERVICE_UNAVAILABLE, status.HTTP_409_CONFLICT]:
                raise ValueError(response, response.json())
            else:
                import time

                time.sleep(60)
                if response := self._query(url, method="PATCH", data=json.dumps(data)):
                    if response.json():
                        data = parse(pd.json_normalize(response.json()))
        if data and isinstance(data, list):
            data = data[0]
        return data

    def _query(
        self,
        url: str,
        method: str = "GET",
        data: dict | str | None = None,
        params: dict | None = None,
        access_token: bool = True,
        is_json: bool = True,
    ) -> HttpResponse:
        headers = {"content-type": "application/json" if is_json else "application/x-www-form-urlencoded"}
        if access_token:
            global_preferences = global_preferences_registry.manager()
            headers["Authorization"] = f'Bearer {global_preferences["wbactivity_sync__outlook_sync_access_token"]}'
        if method == "POST":
            response = requests.post(url, data=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, data=data, headers=headers)
        else:
            response = requests.get(url, headers=headers, params=params)
        return response
