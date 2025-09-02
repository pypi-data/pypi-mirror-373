from django.db import models


class Event(models.Model):
    """
    we store the event notification we received from the webhook in this model to easily debug the sync
    """

    data = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
