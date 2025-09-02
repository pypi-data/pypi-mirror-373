from collections import OrderedDict
from datetime import date, timedelta

import pandas as pd
from django.contrib.messages import warning
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from psycopg.types.range import TimestamptzRange
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from slugify import slugify
from wbcore import serializers as wb_serializers
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.agenda.serializers import ConferenceRoomRepresentationSerializer
from wbcore.contrib.authentication.models import User
from wbcore.contrib.directory.models import Company, Entry, Person
from wbcore.contrib.directory.preferences import get_main_company
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbcore.utils.date import calendar_item_shortcuts

from wbcrm.models import Activity, ActivityType
from wbcrm.models.activities import ActivityCompanyThroughModel, ActivityParticipant

from .groups import GroupRepresentationSerializer
from .recurrence import RecurrenceModelSerializerMixin


class ActivityTypeModelSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = (
            "id",
            "title",
            "icon",
            "color",
            "score",
            "default",
            "_additional_resources",
        )

    def validate(self, data):
        title = data.get("title", None)
        if title:
            type = ActivityType.objects.filter(slugify_title=slugify(title, separator=" "))
            if self.instance:
                type = type.exclude(id=self.instance.id)
            if type.exists():
                raise ValidationError({"title": _("Cannot add a duplicate activity type.")})

        return data


class ActivityTypeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    endpoint = "wbcrm:activitytyperepresentation-list"
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcrm:activitytype-detail")

    class Meta:
        model = ActivityType
        fields = (
            "id",
            "title",
            "icon",
            "_detail",
            "color",
            "score",
        )


class ActivityRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcrm:activity-detail")
    _detail_preview = wb_serializers.HyperlinkField(reverse_name="wbcrm:activity-detail")
    end__date = wb_serializers.SerializerMethodField()
    title = wb_serializers.CharField(max_length=255, read_only=True)

    label_key = "{{end__date}}: {{title}}"

    def get_end__date(self, obj):
        if obj.end is not None:
            return obj.end.strftime("%d.%m.%Y")
        return ""

    @wb_serializers.register_resource()
    def activity(self, instance, request, user):
        return {"activity": f'{reverse("wbcrm:activity-list")}?participants={instance.id}'}

    class Meta:
        model = Activity
        fields = ("id", "_detail", "_detail_preview", "end", "end__date", "start", "title", "_additional_resources")


def get_default_period(*args, **kwargs):
    return TimestamptzRange(timezone.now(), timezone.now() + timedelta(hours=1))  # type: ignore


def handle_representation(representation: OrderedDict) -> OrderedDict:
    """
    This method is used to remove certain representation values if the representation is for private/confidential use.
    By removing these values, the corresponding fields in the Workbench appear empty.

    :param representation:  Dict of primitive datatypes representing the serializer fields.
    :return:                Either the unchanged representation or a privatized version of the representation
    """
    keys_to_preserve = ["id", "period", "status"]
    private_keys_to_preserve = [
        "participants",
        "_participants",
        "companies",
        "_companies",
        "groups",
        "_groups",
        "assigned_to",
        "_assigned_to",
        "creator",
        "_creator",
    ]
    is_private: bool
    if not ((is_private := representation.get("is_private", False)) or representation.get("is_confidential")):
        return representation
    hidden_representation = OrderedDict.fromkeys(representation, None)
    hidden_representation |= {key: representation.get(key) for key in keys_to_preserve}
    if is_private:
        hidden_representation |= {key: representation.get(key) for key in private_keys_to_preserve}
    hidden_representation["title"] = _("Private Activity") if is_private else _("Confidential Activity")
    return hidden_representation


def _get_default_recurrence_end():
    """
    Default to 6 months in the future
    """
    return (date.today() + pd.tseries.offsets.DateOffset(months=6)).date()


class ActivityCompanyThroughModelRepresentationSerializer(wb_serializers.RepresentationSerializer):
    endpoint = "wbcore:directory:companyrepresentation-list"
    value_key = "id"

    def to_representation(self, value):
        rep = super().to_representation(value)
        rep["id"] = value.company.id
        return rep

    class Meta:
        model = ActivityCompanyThroughModel
        fields = (
            "id",
            # "company",
            "computed_str",
        )


class ActivityModelListSerializer(RecurrenceModelSerializerMixin, wb_serializers.ModelSerializer):
    _companies = ActivityCompanyThroughModelRepresentationSerializer(
        source="activity_companies", related_key="companies", many=True
    )

    _participants = PersonRepresentationSerializer(source="participants", many=True)

    heat = wb_serializers.EmojiRatingField(label="Sentiment")
    _groups = GroupRepresentationSerializer(source="groups", many=True)
    _type = ActivityTypeRepresentationSerializer(source="type")
    _latest_reviewer = PersonRepresentationSerializer(source="latest_reviewer")
    is_private = wb_serializers.BooleanField(default=False, read_only=True)
    is_confidential = wb_serializers.BooleanField(default=False, read_only=True)

    def to_representation(self, instance):
        return handle_representation(super().to_representation(instance))

    def validate(self, data):
        main_company = get_main_company()
        request = self.context["request"]
        companies = data.get("companies", [])
        if main_company and main_company in companies:
            warning(
                request,
                f"The main company {main_company} was removed from the list of companies",
            )
        return data

    class Meta:
        model = Activity
        fields = (
            "id",
            "_additional_resources",
            "type",
            "_type",
            "title",
            "status",
            "period",
            "companies",
            "_companies",
            "participants",
            "_participants",
            "groups",
            "_groups",
            "edited",
            "created",
            "description",
            "result",
            "latest_reviewer",
            "is_private",
            "is_confidential",
            "summary",
            "heat",
            "_latest_reviewer",
        )
        read_only_fields = list(filter(lambda x: x not in ["result"], fields))


class ActivityModelSerializer(ActivityModelListSerializer):
    type = wb_serializers.PrimaryKeyRelatedField(
        queryset=ActivityType.objects.all(), default=lambda: ActivityType.get_default_activity_type()
    )
    repeat_choice = wb_serializers.ChoiceField(
        help_text="Repeat activity at the specified frequency",
        label="Recurrence Frequency",
        required=False,
        read_only=lambda view: not view.new_mode,
        choices=Activity.ReoccuranceChoice.choices,
    )

    recurrence_end = wb_serializers.DateField(
        required=False, label=gettext_lazy("Recurrence End"), default=_get_default_recurrence_end
    )
    visibility = wb_serializers.ChoiceField(
        choices=Activity.Visibility.choices,
        help_text=gettext_lazy(
            "Set to private for the activity to hide sensitive information from anyone but the assignee and participants. Set to confidential to hide from anyone but users with manager permissions."
        ),
        label=gettext_lazy("Visibility"),
    )
    assigned_to = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.CurrentUserDefault("profile"),
        queryset=Person.objects.all(),
        label=gettext_lazy("Assigned to"),
    )
    _assigned_to = PersonRepresentationSerializer(source="assigned_to")
    creator = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.CurrentUserDefault("profile"),
        many=False,
        read_only=True,
    )
    _creator = PersonRepresentationSerializer(
        source="creator",
    )
    companies = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultFromGET("companies", many=True),
        many=True,
        queryset=Company.objects.all(),
        label=gettext_lazy("Companies"),
    )
    participants = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultFromGET("participants", many=True),
        many=True,
        queryset=Person.objects.all(),
        label=gettext_lazy("Participants"),
    )
    period = wb_serializers.DateTimeRangeField(
        label=gettext_lazy("Period"),
        default=get_default_period,
        shortcuts=calendar_item_shortcuts,
        read_only=lambda view: view.is_external_activity,
    )

    is_private = wb_serializers.BooleanField(default=False, read_only=True)
    is_confidential = wb_serializers.BooleanField(default=False, read_only=True)
    _conference_room = ConferenceRoomRepresentationSerializer(source="conference_room")

    title = wb_serializers.CharField(
        default=wb_serializers.DefaultFromGET("title"),
        label=gettext_lazy("Title"),
        read_only=lambda view: view.is_external_activity,
    )
    all_day = wb_serializers.BooleanField(read_only=lambda view: view.is_external_activity)
    description = wb_serializers.TextField(read_only=lambda view: view.is_external_activity)

    @cached_property
    def user(self) -> User | None:
        if request := self.context.get("request"):
            return request.user
        return None

    @wb_serializers.register_resource()
    def activity_participants_table(self, instance, request, user):
        return {
            "activity_participants_table": reverse(
                "wbcrm:activity-participant-list", kwargs={"activity_id": instance.id}, request=request
            )
        }

    def to_representation(self, instance):
        return handle_representation(super().to_representation(instance))

    def validate(self, data):
        if (
            (result := data.get("result", None))
            and result not in ["", "<p></p>"]
            and result != getattr(self.instance, "result", "")
        ):
            data["latest_reviewer"] = self.user.profile
            data["reviewed_at"] = timezone.now()
        if data.get("creator", None) is None:
            data["creator"] = self.user.profile

        if not data.get("title", self.instance.title if self.instance else None):
            raise ValidationError({"title": "You need to specify a title for this activity."})

        period = data.get("period", self.instance.period if self.instance else None)
        if not data.get("type", self.instance.type if self.instance else None):
            raise ValidationError({"type": _("Please add an activity type.")})

        if room := data.get("conference_room", self.instance.conference_room if self.instance else None):
            qs = Activity.objects.filter(status=Activity.Status.PLANNED, conference_room=room)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            conference_room_activity = Activity.get_inrange_activities(
                qs, period.lower + timedelta(seconds=60), period.upper - timedelta(seconds=60)
            ).first()
            if conference_room_activity and (user := self.user):
                if (
                    conference_room_activity.visibility == Activity.Visibility.PRIVATE
                    and user.profile not in conference_room_activity.participants.all()
                    and user.profile != conference_room_activity.assigned_to
                ):
                    raise ValidationError(
                        {
                            "non_field_errors": _(
                                "A private activity already uses this conference room at the same time."
                            )
                        }
                    )
                elif (
                    conference_room_activity.visibility == Activity.Visibility.CONFIDENTIAL
                    and not CalendarItem.has_user_administrate_permission(user)
                ):
                    raise ValidationError(
                        {
                            "non_field_errors": _(
                                "A confidential activity already uses this conference room at the same time."
                            )
                        }
                    )
                else:
                    raise ValidationError(
                        {
                            "non_field_errors": _(
                                'The activity "{title}" already uses this conference room at the same time.'
                            ).format(title=conference_room_activity.title)
                        }
                    )

        # In the following section we validate the groups and the group members. If a user trys to remove a group member from the participants/companies fields, we want to raise an validation error.
        if self.instance and self.instance.groups.exists() and not ("groups" in data and data["groups"] == []):
            # If there are no companies or participants in the current instance, you cannot remove a group member; therefore there is no need to validate the groups. This can happen if you add to an existing and empty activity a group.
            if self.instance.companies.exists() or self.instance.participants.exists():
                companies = data.get("companies", [])
                participants = data.get("participants", [])
                # If there are new companies or participants in data, we need to check if existing group members have been removed.
                if "companies" in data or "participants" in data:
                    new_groups = data.get("groups", [])
                    new_groups_id_list = [group.id for group in new_groups]
                    old_groups = self.instance.groups.exclude(id__in=new_groups_id_list)

                    # If there are no new groups in data, we need to check if members of the old group have been removed.
                    # If there are new groups and also old groups, we need to check for the old groups if members have been removed.
                    # If only new groups are present, we don't need to validate.
                    if not new_groups or old_groups.exists():
                        new_companies_id_list = (
                            [companies.id for companies in companies]
                            if "companies" in data
                            else self.instance.companies.values_list("id", flat=True)
                        )
                        new_participants_id_list = (
                            [participant.id for participant in participants]
                            if "participants" in data
                            else self.instance.participants.values_list("id", flat=True)
                        )
                        new_entries = Entry.objects.filter(
                            Q(id__in=new_companies_id_list) | Q(id__in=new_participants_id_list)
                        ).distinct()
                        missing_members = (
                            Entry.objects.filter(groups__in=old_groups).exclude(id__in=new_entries).distinct()
                        )
                        # If there are group members who are not in the new entries field, we can assume, that a group member has been removed and we need to throw an error.
                        if missing_members.exists():
                            missing_members_computed_strs = ", ".join(
                                list(missing_members.values_list("computed_str", flat=True))
                            )
                            util_str = _("is a member")
                            if missing_members.count() > 1:
                                start, x, end = missing_members_computed_strs.rpartition(",")
                                missing_members_computed_strs = start + _(" and") + end
                                util_str = _("are members")

                            groups = ", ".join(
                                list(dict.fromkeys(missing_members.values_list("groups__title", flat=True)))
                            )
                            error_message = _(
                                "{missing_members} {util_str} of the following group(s): {groups}\n. You cannot remove members of selected groups.",
                            ).format(missing_members=missing_members_computed_strs, util_str=util_str, groups=groups)

                            raise ValidationError({"groups": error_message})
        return super().validate(data)

    class Meta:
        model = Activity
        required_fields = ("importance", "period", "reminder_choice", "repeat_choice", "start", "title", "type")
        read_only_fields = (
            "creator",
            "edited",
            "latest_reviewer",
            "reviewed_at",
            "is_cancelled",
        )
        fields = (
            "id",
            "_additional_resources",
            "all_day",
            "assigned_to",
            "_assigned_to",
            "companies",
            "_companies",
            "conference_room",
            "_conference_room",
            "created",
            "creator",
            "_creator",
            "description",
            "disable_participant_check",
            "edited",
            "end",
            "groups",
            "_groups",
            "importance",
            "visibility",
            "latest_reviewer",
            "_latest_reviewer",
            "location",
            "location_latitude",
            "location_longitude",
            "online_meeting",
            "participants",
            "_participants",
            "summary",
            "period",
            "propagate_for_all_children",
            "recurrence_count",
            "recurrence_end",
            "reminder_choice",
            "repeat_choice",
            "result",
            "reviewed_at",
            "start",
            "status",
            "title",
            "type",
            "_type",
            "is_cancelled",
            "is_private",
            "is_confidential",
            "_buttons",
        )


class ReadOnlyActivityModelSerializer(ActivityModelSerializer):
    class Meta(ActivityModelSerializer.Meta):
        read_only_fields = list(filter(lambda x: x not in ["result"], ActivityModelSerializer.Meta.fields))


class ActivityParticipantModelSerializer(wb_serializers.ModelSerializer):
    _activity = ActivityRepresentationSerializer(source="activity")
    activity = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultFromGET("activity_id"),
        queryset=Activity.objects.all(),
        label=gettext_lazy("Activity"),
    )
    customer_status = wb_serializers.CharField(
        default="", label=gettext_lazy("Status"), allow_null=True, read_only=True
    )
    position = wb_serializers.CharField(default="", label=gettext_lazy("Position"), read_only=True)
    primary_telephone = wb_serializers.TelephoneField(
        default="", label=gettext_lazy("Primary Telephone"), allow_null=True, read_only=True
    )
    primary_email = wb_serializers.CharField(
        allow_null=True, default="", label=gettext_lazy("Primary Email"), read_only=True
    )
    _participant = PersonRepresentationSerializer(source="participant")
    is_occupied = wb_serializers.BooleanField(default=False)

    def validate(self, data):
        data_activity = data.get("activity", None)
        data_participant = data.get("participant", None)

        if ActivityParticipant.objects.filter(
            activity=data_activity,
            participant=data_participant,
        ).exists():
            raise ValidationError({"participant": _("The person is already a participant in this activity.")})

        return super().validate(data)

    def create(self, validated_data):
        validated_data.pop("is_occupied", None)
        return super().create(validated_data)

    class Meta:
        model = ActivityParticipant
        fields = (
            "_activity",
            "_additional_resources",
            "_participant",
            "activity",
            "customer_status",
            "position",
            "id",
            "is_occupied",
            "participant",
            "participation_status",
            "status_changed",
            "primary_telephone",
            "primary_email",
        )
