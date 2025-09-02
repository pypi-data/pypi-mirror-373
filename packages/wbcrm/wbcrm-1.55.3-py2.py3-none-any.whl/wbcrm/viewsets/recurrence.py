from django.contrib.messages import warning
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from wbcrm.models.recurrence import Recurrence


class RecurrenceModelViewSetMixin:
    @action(detail=True, methods=["DELETE"], permission_classes=[permissions.IsAuthenticated])
    def delete_next_occurrences(self, request, pk=None):
        instance = get_object_or_404(self.queryset.model, pk=pk)
        instance.forward_deletion()
        return Response({})

    def add_messages(self, request, instance=None, **kwargs):
        if instance:
            # If true, this activity is recurring.
            if instance.is_recurrent:
                warning(
                    request,
                    _("This is a recurring occurrence with period {repeat_choice}").format(
                        repeat_choice=Recurrence.ReoccuranceChoice(instance.repeat_choice).label
                    ),
                )
