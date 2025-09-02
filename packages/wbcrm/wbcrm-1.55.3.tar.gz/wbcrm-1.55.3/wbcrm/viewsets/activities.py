import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.contrib.messages import info, warning
from django.db.models import Exists, F, OuterRef, QuerySet, Subquery
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.agenda.viewsets import CalendarItemViewSet
from wbcore.contrib.directory.models import (
    Company,
    EmailContact,
    EmployerEmployeeRelationship,
    Entry,
    Person,
    TelephoneContact,
)
from wbcore.filters import DjangoFilterBackend

from wbcrm import serializers as crm_serializers
from wbcrm.filters import (
    ActivityChartFilter,
    ActivityFilter,
    ActivityParticipantFilter,
    ActivityTypeFilter,
)
from wbcrm.models.activities import (
    Activity,
    ActivityParticipant,
    ActivityType,
    send_invitation_participant_as_task,
)
from wbcrm.viewsets.buttons import ActivityButtonConfig, ActivityParticipantButtonConfig
from wbcrm.viewsets.display import (
    ActivityDisplay,
    ActivityParticipantDisplayConfig,
    ActivityTypeDisplay,
)
from wbcrm.viewsets.endpoints import (
    ActivityEndpointConfig,
    ActivityParticipantModelEndpointConfig,
)
from wbcrm.viewsets.previews.activities import ActivityPreviewConfig
from wbcrm.viewsets.titles import (
    ActivityChartModelTitleConfig,
    ActivityParticipantTitleConfig,
    ActivityTitleConfig,
    ActivityTypeTitleConfig,
)

from ..serializers import (
    ActivityTypeModelSerializer,
    ActivityTypeRepresentationSerializer,
)
from .recurrence import RecurrenceModelViewSetMixin


class ActivityTypeModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbcrm:activitytype"
    LIST_DOCUMENTATION = "wbcrm/markdown/documentation/activitytype.md"
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeModelSerializer
    display_config_class = ActivityTypeDisplay
    title_config_class = ActivityTypeTitleConfig
    search_fields = ("title",)
    filterset_class = ActivityTypeFilter
    ordering = ("title",)
    ordering_fields = (
        "title",
        "color",
        "score",
        "icon",
        "default",
    )


class ActivityTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcrm:activitytyperepresentation"
    serializer_class = ActivityTypeRepresentationSerializer
    queryset = ActivityType.objects.all()


class ActivityRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Activity.objects.all()
    serializer_class = crm_serializers.ActivityRepresentationSerializer


class ActivityViewSet(RecurrenceModelViewSetMixin, CalendarItemViewSet):
    IDENTIFIER = "wbcrm:activity"
    DEPENDANT_IDENTIFIER = ["wbcrm:calendaritem"]
    LIST_DOCUMENTATION = "wbcrm/markdown/documentation/activity.md"

    ordering = ["-edited", "id"]
    search_fields = ("title", "description", "result")
    serializer_class = crm_serializers.ActivityModelSerializer
    display_config_class = ActivityDisplay
    title_config_class = ActivityTitleConfig
    filterset_class = ActivityFilter
    endpoint_config_class = ActivityEndpointConfig
    preview_config_class = ActivityPreviewConfig
    button_config_class = ActivityButtonConfig
    queryset = Activity.objects.all()

    ordering_fields = [
        "created",
        "description",
        "edited",
        "period",
        "latest_reviewer__computed_str",
        "type",
        "result",
        "title",
    ]

    @cached_property
    def is_external_activity(self):
        if "pk" in self.kwargs:
            if activity := self.get_object():
                return (creator := activity.creator) and not creator.is_internal
        return False

    @cached_property
    def is_private_for_user(self):
        if "pk" in self.kwargs:
            if activity := self.get_object():
                return activity.is_private_for_user(self.request.user)
        return not self.new_mode

    @cached_property
    def is_confidential_for_user(self):
        if "pk" in self.kwargs:
            if activity := self.get_object():
                return activity.is_confidential_for_user(self.request.user)
        return not self.new_mode

    @cached_property
    def participants(self) -> QuerySet[Person]:
        try:
            participant_ids = self.request.GET["participants"].split(",")
        except KeyError:
            participant_ids = []
        return Person.objects.filter(id__in=participant_ids)

    @cached_property
    def companies(self) -> QuerySet[Company]:
        try:
            company_ids = self.request.GET["companies"].split(",")
        except KeyError:
            company_ids = []
        return Company.objects.filter(id__in=company_ids)

    @cached_property
    def entry(self) -> Entry | None:
        try:
            return Entry.all_objects.get(id=self.kwargs.get("person_id", self.kwargs["company_id"]))
        except (KeyError, Entry.DoesNotExist):
            return self.participants.first() or self.companies.first()

    def get_serializer_class(self):
        if self.get_action() in ["list", "list-metadata"]:
            return crm_serializers.ActivityModelListSerializer
        if (
            self.is_private_for_user
            or self.is_confidential_for_user
            or (
                "pk" in self.kwargs
                and (obj := self.get_object())
                and obj.status in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]
            )
        ):
            return crm_serializers.ReadOnlyActivityModelSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        return (
            Activity.get_activities_for_user(user, base_qs=super().get_queryset())
            .select_related("latest_reviewer", "type")
            .prefetch_related(
                "groups",
                "participants",
                "companies",
            )
        )

    def add_messages(self, request, instance: Activity | None = None, **kwargs):
        super().add_messages(request, instance=instance, **kwargs)
        if instance:
            if instance.status in [Activity.Status.CANCELLED, Activity.Status.REVIEWED]:
                info(
                    self.request,
                    _(
                        "You can only modify the review text for an activity that is either cancelled or already reviewed."
                    ),
                )
            if self.is_external_activity:
                warning(
                    self.request,
                    _(
                        "This activity was created by an external user and synchronized. The modification is restricted."
                    ),
                )
            if warning_message := instance.participants_company_check_message():
                warning(request, warning_message, extra_tags="auto_close=0")

            # Throws a warning message when there are more people (probably) participating in an activity on-site
            # than the selected conference room has capacity for.
            if (
                instance.conference_room
                and instance.conference_room.capacity is not None
                and instance.participants.exclude(
                    activity_participants__participation_status__in=[
                        ActivityParticipant.ParticipationStatus.ATTENDS_DIGITALLY,
                        ActivityParticipant.ParticipationStatus.CANCELLED,
                    ]
                ).count()
                > instance.conference_room.capacity
            ):
                warning(
                    request,
                    _(
                        "There are more participants currently participating in this activity than the maximum capacity of the selected conference room allows."
                    ),
                )


class ActivityChartModelViewSet(viewsets.ChartViewSet):
    filter_backends = (DjangoFilterBackend,)
    queryset = Activity.objects.all()
    filterset_class = ActivityChartFilter
    IDENTIFIER = "wbcrm:activitychart"
    title_config_class = ActivityChartModelTitleConfig

    def get_queryset(self):
        return (
            Activity.get_activities_for_user(self.request.user)
            .exclude(period__isnull=True)
            .filter(visibility=CalendarItem.Visibility.PUBLIC)
            .annotate(
                activity_type_color=F("type__color"),
                activity_type_title=F("type__title"),
                start_date=F("period__startswith"),
                end_date=F("period__endswith"),
            )
            .select_related("type")
        )

    def get_plotly(self, queryset):
        fig = go.Figure()
        if queryset.exists():
            df = pd.DataFrame(
                queryset.values("type", "start_date", "end_date", "activity_type_color", "activity_type_title")
            )
            df["start_date"] = df["start_date"].dt.floor("h")
            df["end_date"] = df["end_date"].dt.ceil("h")
            df = (
                pd.concat(
                    [
                        pd.DataFrame(index=pd.date_range(r.start_date, r.end_date, freq="1h")).assign(
                            type=r.type,
                            activity_type_color=r.activity_type_color,
                            activity_type_title=r.activity_type_title,
                        )
                        for r in df.itertuples()
                    ]
                ).reset_index()
            ).rename(columns={"index": "Period", "activity_type_title": "Type"})
            df["Period"] = pd.to_datetime(df["Period"])
            fig = px.histogram(
                df,
                x="Period",
                color="Type",
                labels="Type",
                nbins=len(pd.date_range(df["Period"].min(), df["Period"].max(), freq="1h")) + 1,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title=_("<b>User Activity</b>"),
                bargap=0.2,
                autosize=True,
            )

        return fig


class ActivityParticipantModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbcrm:activity-participant"

    button_config_class = ActivityParticipantButtonConfig
    display_config_class = ActivityParticipantDisplayConfig
    endpoint_config_class = ActivityParticipantModelEndpointConfig
    filterset_class = ActivityParticipantFilter
    serializer_class = crm_serializers.ActivityParticipantModelSerializer
    search_fields = []
    title_config_class = ActivityParticipantTitleConfig
    ordering = ["participation_status", "id"]
    queryset = ActivityParticipant.objects.all()

    def get_queryset(self):
        activity = get_object_or_404(Activity, id=self.kwargs["activity_id"])
        return (
            super()
            .get_queryset()
            .filter(activity=activity)
            .annotate(
                customer_status=Subquery(
                    EmployerEmployeeRelationship.objects.filter(
                        primary=True, employee=OuterRef("participant__pk")
                    ).values("employer__customer_status__title")[:1]
                ),
                position=Subquery(
                    EmployerEmployeeRelationship.objects.filter(
                        primary=True, employee=OuterRef("participant__pk")
                    ).values("position__title")[:1]
                ),
                primary_telephone=Subquery(
                    TelephoneContact.objects.filter(primary=True, entry__id=OuterRef("participant__pk")).values(
                        "number"
                    )[:1],
                ),
                primary_email=Subquery(
                    EmailContact.objects.filter(primary=True, entry__id=OuterRef("participant__pk")).values("address")[
                        :1
                    ],
                ),
                is_occupied=Exists(
                    Activity.objects.filter(
                        period__overlap=activity.period,
                        participants__id=OuterRef("participant__pk"),
                    )
                    .exclude(id=activity.id)
                    .exclude(status=Activity.Status.CANCELLED)
                ),
            )
        )

    @action(methods=["PATCH"], detail=False)
    def send_external_invitation(self, request, activity_id: int, pk=None):
        send_invitation_participant_as_task.delay(activity_id)
        return Response({"__notification": {"title": "Invitation sent to external participants"}})
