from django.urls import path

from wbcrm.synchronization.activity.views import event_watch

urlpatterns = [
    path("event_watch", event_watch, name="event_watch"),
]
