from django.urls import include, path

urlpatterns = [
    path("activity/", include(("wbcrm.synchronization.activity.urls", "activity"), namespace="activity")),
]
