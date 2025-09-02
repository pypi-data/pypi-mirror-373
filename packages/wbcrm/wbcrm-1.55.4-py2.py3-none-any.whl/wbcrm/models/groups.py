from celery import shared_task
from django.db import models
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.directory.models import Company, Entry, Person
from wbcore.models import WBModel

from wbcrm.models import Activity


class Group(WBModel):
    title = models.CharField(max_length=255, unique=True, verbose_name=_("Title"))
    members = models.ManyToManyField("directory.Entry", related_name="groups", verbose_name=_("Members"))

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    def __str__(self):
        return self.title

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcrm:group"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcrm:grouprepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{title}}"


@receiver(m2m_changed, sender=Group.members.through)
def m2m_changed_members(sender, instance, action, pk_set, **kwargs):
    """
    M2m changed Group signal: Change participants, companies and entities of future planned activities/calendar items
    if a group's members get updated
    """
    if action == "post_add":
        add_changed_group_members(instance, pk_set)

    if action == "post_remove":
        remove_changed_group_members(instance, pk_set)


@receiver(pre_delete, sender=Group)
def pre_delete_group(sender, instance, **kwargs):
    """
    Post delete Group signal: Remove members from future planned activities/calendar items if a group was deleted
    """
    remove_deleted_groups_members(instance)


@shared_task
def add_changed_group_members(instance, pk_set):
    for activity in Activity.objects.filter(
        status=Activity.Status.PLANNED, start__gte=timezone.now(), groups=instance
    ):
        item = CalendarItem.all_objects.get(id=activity.id)
        for member in pk_set:
            entry = Entry.all_objects.get(id=member)
            if entry not in item.entities.all():
                item.entities.add(entry)
            if entry.is_company:
                company = Company.all_objects.get(id=entry.id)
                if company not in activity.companies.all():
                    activity.companies.add(company)
            else:
                person = Person.all_objects.get(id=entry.id)
                if person not in activity.participants.all():
                    activity.participants.add(person)


@shared_task
def remove_changed_group_members(instance, pk_set):
    for activity in Activity.objects.filter(
        status=Activity.Status.PLANNED, start__gte=timezone.now(), groups=instance
    ):
        item = CalendarItem.all_objects.get(id=activity.id)
        for member in pk_set:
            entry = Entry.all_objects.get(id=member)
            if entry in item.entities.all():
                item.entities.remove(entry)
            if entry.is_company:
                company = Company.all_objects.get(id=entry.id)
                if company in activity.companies.all():
                    activity.companies.remove(company)
            else:
                person = Person.all_objects.get(id=entry.id)
                if person in activity.participants.all():
                    activity.participants.remove(person)


@shared_task
def remove_deleted_groups_members(instance):
    for activity in Activity.objects.filter(
        status=Activity.Status.PLANNED, start__gte=timezone.now(), groups=instance
    ):
        item = CalendarItem.all_objects.get(id=activity.id)
        for member in instance.members.all():
            if member in item.entities.all():
                item.entities.remove(member)
            if member.is_company:
                company = Company.all_objects.get(id=member.id)
                if company in activity.companies.all():
                    activity.companies.remove(company)
            else:
                person = Person.all_objects.get(id=member.id)
                if person in activity.participants.all():
                    activity.participants.remove(person)
