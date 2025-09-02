import calendar
import datetime as dt

week_ahead = dt.date.today() + dt.timedelta(days=7)
week_before = dt.date.today() - dt.timedelta(days=7)
week_ahead_timestamp = calendar.timegm(week_ahead.timetuple()) * 1000
week_before_timestamp = calendar.timegm(week_before.timetuple()) * 1000
credentials = '{"url": "https://fake_url.io", "type": "service_account", "project_id": "fake_project_id", "private_key_id": "fake_private_key_id", "private_key": "fake_private_key", "client_email": "client_mail@serviceaccount.com", "client_id": "fake_client_id", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://fake_auth_url", "client_x509_cert_url": "https://fake_cert_url"}'

person_metadata = {"google_backend": {"watch": {"expiration": str(week_ahead_timestamp)}}}
person_metadata_expired = {"google_backend": {"watch": {"expiration": str(week_before_timestamp)}, "expired": True}}

event = {
    "attendees": [
        {"displayName": "Foo", "email": "Foo@Foo.com", "responseStatus": "accepted"},
        {"displayName": "Bar", "email": "Bar@Bar.com", "responseStatus": "declined"},
        {"displayName": "Foo Bar", "email": "Foo@Bar.com", "responseStatus": "tentative"},
        {"email": "Bar@Foo.com", "responseStatus": "tentative"},
    ]
}

event_data = {
    "id": "test",
    "items": [],
    "start": {"date": "2022-12-06", "dateTime": "2022-12-06T17:25:00+0200", "timeZone": "UTC"},
    "end": {"date": "2022-12-06", "dateTime": "2022-12-06T18:25:00+0200", "timeZone": "UTC"},
}
event_list = [
    {"id": "1", "metaTest": "Parent", "originalStartTime": {"dateTime": "Fake Date Time"}},
    {"id": "2", "metaTest": "Child A", "originalStartTime": {"dateTime": "Fake Date Time A"}},
    {"id": "3", "metaTest": "Child B", "originalStartTime": {"dateTime": "Fake Date Time B"}},
    {"id": "4", "metaTest": "Child C", "originalStartTime": {"dateTime": "Fake Date Time C"}},
]


class event_service:
    def insert(calendarId, body):
        return execute_service(calendarId, body)

    def instances(calendarId, eventId):
        return execute_service(calendarId, eventId)

    def delete(calendarId, eventId):
        return execute_service(calendarId, eventId)

    def update(calendarId, eventId, body=event):
        return execute_service(calendarId, eventId)

    def patch(calendarId, eventId, body=event):
        return execute_service(calendarId, eventId)

    def get(calendarId, eventId, body=event):
        return execute_service(calendarId, eventId)

    def list(calendarId, pageToken, syncToken):
        return execute_service(calendarId, pageToken)

    def watch(calendarId, body=event):
        return execute_service(calendarId, event)


class channels_service:
    def stop(body):
        return execute_service("", body)


class execute_service:
    def __init__(self, calendarId, body):
        self.calendarId = calendarId
        self.body = body

    def execute(self):
        return event_data


class service_data:
    def events(self):
        return event_service

    def channels(self):
        return channels_service
