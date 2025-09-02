import functools
from contextlib import suppress
from urllib.parse import urlencode

from django.dispatch import receiver
from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.directory.serializers import (
    CompanyModelSerializer,
    EntryModelSerializer,
    EntryRepresentationSerializer,
    PersonModelListSerializer,
    PersonModelSerializer,
    TelephoneContactSerializer,
)
from wbcore.signals import add_additional_resource, add_instance_additional_resource

from wbcrm.models import ActivityType


@functools.lru_cache()
def get_call_activity_type() -> int:
    return ActivityType.objects.get_or_create(slugify_title="call", defaults={"title": "Call"})[0].id


@receiver(add_additional_resource, sender=TelephoneContactSerializer)
def add_telephone_contact_activity_resources(sender, serializer, instance, request, user, **kwargs):
    res = {}
    with suppress(Entry.DoesNotExist):
        if entry := instance.entry:
            activity_reverse_url = reverse("wbcrm:activity-list", args=[], request=request)

            # Creates the URL for the 'Create New Call Activity'-Button
            query_args = {
                "type": get_call_activity_type(),
                "new_mode": True,
                "participants": [str(request.user.profile.id)],
                "title": _("Call with {name}").format(name=entry.computed_str),
            }

            if entry.is_company:
                query_args["companies"] = [str(entry.id)]
                activity_reverse_url = f"{activity_reverse_url}?companies={entry.id}"
            else:
                query_args["participants"].append(str(entry.id))
                activity_reverse_url = f"{activity_reverse_url}?participants={entry.id}"

            query_args["participants"] = ",".join(query_args["participants"])
            if "companies" in query_args:
                query_args["companies"] = ",".join(query_args["companies"])
        res["list_of_activities"] = activity_reverse_url
        res["new_call"] = reverse("wbcrm:activity-list", args=[], request=request) + "?" + urlencode(query_args)
    return res


@receiver(add_instance_additional_resource, sender=CompanyModelSerializer)
@receiver(add_instance_additional_resource, sender=PersonModelSerializer)
@receiver(add_instance_additional_resource, sender=EntryModelSerializer)
@receiver(add_instance_additional_resource, sender=PersonModelListSerializer)
@receiver(add_instance_additional_resource, sender=EntryRepresentationSerializer)
def add_entry_additional_resources(sender, serializer, instance, request, user, **kwargs):
    res = {"account": f'{reverse("wbcrm:account-list", args=[], request=request)}?customer={instance.id}'}
    if instance.is_company:
        res["activity"] = f'{reverse("wbcrm:activity-list", request=request)}?companies={instance.id}'
        res["interested_products"] = reverse(
            "wbcrm:company-interestedproduct-list", args=[instance.id], request=request
        )
    else:
        res["activity"] = f'{reverse("wbcrm:activity-list", request=request)}?participants={instance.id}'
    return res
