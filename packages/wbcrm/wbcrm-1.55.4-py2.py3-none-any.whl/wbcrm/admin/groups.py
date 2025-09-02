from django.contrib import admin

from wbcrm.models import Group


@admin.register(Group)
class GroupModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ("members",)
