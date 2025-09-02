from typing import Type

from django.db.models import Q
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from wbcore import serializers
from wbcore.contrib.directory.models import Person
from wbcore.serializers.serializers import Serializer
from wbcrm.models import Activity, ActivityParticipant, ActivityType
from wbcrm.serializers import ActivityTypeRepresentationSerializer
from wbhuman_resources.models.kpi import KPI, KPIHandler
from wbhuman_resources.serializers import KPIModelSerializer


class NumberOfActivityKPISerializer(KPIModelSerializer):
    activity_type = serializers.PrimaryKeyRelatedField(
        required=True, many=True, queryset=ActivityType.objects.all(), label=_("Activity Type")
    )
    _activity_type = ActivityTypeRepresentationSerializer(source="activity_type", many=True)

    activity_area = serializers.ChoiceField(
        default="all",
        choices=[("only_internal", _("Only Internal")), ("only_external", _("Only External")), ("all", _("All"))],
    )
    person_participates = serializers.BooleanField(
        default=True,
        label=_("Participants of Activity"),
        help_text=_("Activities considered are related to the participants"),
    )
    person_created = serializers.BooleanField(
        default=True, label=_("Creator of activity"), help_text=_("Activities considered are related to the creator")
    )
    person_assigned = serializers.BooleanField(
        default=True,
        label=_("Person Assigned"),
        help_text=_("Activities considered are related to the persons assigned"),
    )

    def update(self, instance, validated_data):
        activity_type = validated_data.get(
            "activity_type",
            instance.additional_data["serializer_data"].get(
                "activity_type", list(ActivityType.objects.values_list("id", flat=True))
            ),
        )
        activity_area = validated_data.get(
            "activity_area",
            instance.additional_data["serializer_data"].get("activity_area", "all"),
        )

        person_participates = validated_data.get(
            "person_participates",
            instance.additional_data["serializer_data"].get("person_participates", True),
        )
        person_created = validated_data.get(
            "person_created",
            instance.additional_data["serializer_data"].get("person_created", True),
        )
        person_assigned = validated_data.get(
            "person_assigned",
            instance.additional_data["serializer_data"].get("person_assigned", True),
        )

        additional_data = instance.additional_data
        additional_data["serializer_data"]["activity_type"] = (
            [_type.id for _type in validated_data.get("activity_type")]
            if validated_data.get("activity_type")
            else activity_type
        )
        additional_data["serializer_data"]["activity_area"] = activity_area
        additional_data["serializer_data"]["person_participates"] = person_participates
        additional_data["serializer_data"]["person_created"] = person_created
        additional_data["serializer_data"]["person_assigned"] = person_assigned

        additional_data["list_data"] = instance.get_handler().get_list_data(additional_data["serializer_data"])
        validated_data["additional_data"] = additional_data

        return super().update(instance, validated_data)

    class Meta(KPIModelSerializer.Meta):
        fields = (
            *KPIModelSerializer.Meta.fields,
            "activity_type",
            "_activity_type",
            "activity_area",
            "person_participates",
            "person_created",
            "person_assigned",
        )


class NumberOfActivityKPI(KPIHandler):
    def get_name(self) -> str:
        return _("Number of Activities")

    def get_serializer(self) -> Type[Serializer]:
        return NumberOfActivityKPISerializer

    def annotate_parameters(self, queryset: QuerySet[KPI]) -> QuerySet[KPI]:
        return queryset.annotate(
            activity_type=F("additional_data__serializer_data__activity_type"),
            activity_area=F("additional_data__serializer_data__activity_area"),
            person_participates=F("additional_data__serializer_data__person_participates"),
            person_created=F("additional_data__serializer_data__person_created"),
            person_assigned=F("additional_data__serializer_data__person_assigned"),
        )

    def get_list_data(self, serializer_data: dict) -> list[str]:
        activity_types = list(
            ActivityType.objects.filter(pk__in=serializer_data["activity_type"]).values_list("title", flat=True)
        )
        return [
            _("Activity Type: {types}").format(types=activity_types),
            _("Activity Area: {area}").format(area=serializer_data["activity_area"]),
            _("Person Participates: {participating}").format(participating={serializer_data["person_participates"]}),
            _("Person Created: {created}").format(created=serializer_data["person_created"]),
            _("Person Assigned: {assigned}").format(assigned=serializer_data["person_assigned"]),
        ]

    def get_display_grid(self) -> list[list[str]]:
        return [
            ["activity_type"] * 3,
            ["activity_area"] * 3,
            ["person_created", "person_assigned", "person_participates"],
        ]

    def evaluate(self, kpi: "KPI", evaluated_person=None, evaluation_date=None) -> int:
        persons = (
            [evaluated_person.id] if evaluated_person else kpi.evaluated_persons.all().values_list("id", flat=True)
        )
        serializer_data = kpi.additional_data.get("serializer_data")
        qs = Activity.objects.filter(
            period__startswith__date__gte=kpi.period.lower,
            period__endswith__date__lte=evaluation_date if evaluation_date else kpi.period.upper,
        ).exclude(status=Activity.Status.CANCELLED)
        qs = (
            qs.filter(type__id__in=serializer_data.get("activity_type"))
            if serializer_data.get("activity_type")
            else qs
        )

        condition = None
        if serializer_data.get("person_created") or serializer_data.get("person_created") is None:
            condition = Q(creator__in=persons)
        if serializer_data.get("person_assigned") or serializer_data.get("person_assigned") is None:
            condition = (condition | Q(assigned_to__in=persons)) if condition else Q(assigned_to__in=persons)
        if serializer_data.get("person_participates") or serializer_data.get("person_participates") is None:
            condition = (condition | Q(participants__in=persons)) if condition else Q(participants__in=persons)
        if condition:
            qs = qs.filter(condition)

        if (activity_area := serializer_data.get("activity_area")) and (activity_area != "all"):
            participant_ids = set(
                ActivityParticipant.objects.filter(activity__id__in=qs.values_list("id", flat=True)).values_list(
                    "participant", flat=True
                )
            )
            employee_ids = Person.objects.filter_only_internal().values_list("id", flat=True)
            externals = set(
                Person.objects.filter(Q(id__in=participant_ids) & ~Q(id__in=employee_ids)).values_list("id", flat=True)
            )
            if activity_area == "only_internal":
                qs = qs.exclude(
                    Q(creator__in=externals) | Q(assigned_to__in=externals) | Q(participants__id__in=externals)
                )
            elif activity_area == "only_external":
                qs = qs.filter(
                    Q(creator__in=externals) | Q(assigned_to__in=externals) | Q(participants__id__in=externals)
                )
        return qs.distinct("id").count()
