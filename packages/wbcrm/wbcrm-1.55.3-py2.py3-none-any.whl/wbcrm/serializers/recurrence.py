from django.db.models import Model
from django.forms import ValidationError
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers

from wbcrm.models.recurrence import Recurrence


class RecurrenceModelSerializerMixin:
    @wb_serializers.register_only_instance_resource()
    def next_occurrence(self, instance: Model, request, user, **kwargs) -> dict:
        resources = {}
        if next_occurrence := instance.next_occurrence:
            resources["next_occurrence"] = reverse(
                f"{instance.get_endpoint_basename()}-detail", args=[next_occurrence.id], request=request
            )
        return resources

    @wb_serializers.register_only_instance_resource()
    def previous_occurrence(self, instance: Model, request, user, **kwargs) -> dict:
        resources = {}
        if previous_occurrence := instance.previous_occurrence:
            resources["previous_occurrence"] = reverse(
                f"{instance.get_endpoint_basename()}-detail", args=[previous_occurrence.id], request=request
            )
        return resources

    @wb_serializers.register_only_instance_resource()
    def get_parent_occurrence(self, instance: Model, request, user, **kwargs) -> dict:
        resources = {}
        if instance.parent_occurrence:
            resources["get_parent_occurrence"] = reverse(
                f"{instance.get_endpoint_basename()}-detail", args=[instance.parent_occurrence.id], request=request
            )
        return resources

    @wb_serializers.register_only_instance_resource()
    def delete_occurrences(self, instance, request, user, **kwargs):
        resources = dict()
        parent = instance.parent_occurrence if instance.parent_occurrence else instance
        child_occurrences = parent.get_recurrent_valid_children()
        if instance.period and child_occurrences.exists():
            child_occurrences = child_occurrences.filter(period__startswith__gt=instance.period.lower)
        if child_occurrences.exists():
            resources["delete_next_occurrences"] = reverse(
                f"{instance.get_endpoint_basename()}-delete-next-occurrences", args=[instance.id], request=request
            )
        return resources

    def validate(self, data):
        period = data.get("period", self.instance.period if self.instance else None)
        recurrence_count = data.get("recurrence_count", self.instance.recurrence_count if self.instance else None)
        recurrence_end = data.get("recurrence_end", self.instance.recurrence_end if self.instance else None)
        repeat_choice = data.get("repeat_choice", self.instance.repeat_choice if self.instance else None)
        if not period:
            raise serializers.ValidationError({"period": gettext("Please provide a valid timeframe.")})

        if recurrence_end and recurrence_count:
            error = gettext("You can only pick either a recurrence count or an end date but not both.")
            raise ValidationError({"recurrence_end": error, "recurrence_count": error})

        if (
            not self.instance
            and (recurrence_end or recurrence_count)
            and repeat_choice == Recurrence.ReoccuranceChoice.NEVER
        ):
            data["recurrence_end"] = None
            data["recurrence_count"] = None
        if data.get("repeat_choice") and data.get("repeat_choice") != Recurrence.ReoccuranceChoice.NEVER:
            if data.get("recurrence_end") and period.lower.date() >= data.get("recurrence_end"):
                raise ValidationError(
                    {
                        "recurrence_end": gettext(
                            'The "Repeat Until" date needs to be after the "Recurrence Start" date.'
                        )
                    }
                )
            if data.get("repeat_choice") == Recurrence.ReoccuranceChoice.BUSINESS_DAILY and period.lower.weekday() > 4:
                raise ValidationError({"period": gettext("Period must correspond to the recurrence 'Business Daily'")})

        if self.instance and self.instance.period and self.instance.is_recurrent:
            if (
                self.instance.period.lower.date() != period.lower.date()
                or self.instance.period.upper.date() != period.upper.date()
            ):
                raise ValidationError(
                    {"period": gettext("It is only possible to change the time of the period of an occurrence.")}
                )
        return super().validate(data)
