from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig


class ActivityTypeTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Activity Types")

    def get_create_title(self):
        return _("New Activity Type")

    def get_instance_title(self):
        return _("Activity Type")


class ActivityTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        if "pk" in self.view.kwargs:
            if self.view.is_private_for_user:
                return _("Private Activity")

            elif self.view.is_confidential_for_user:
                return _("Confidential Activity")

        return _("Activity: {{title}}")

    def get_delete_title(self):
        if "pk" in self.view.kwargs:
            if self.view.is_private_for_user:
                return _("Delete Private Activity")

            elif self.view.is_confidential_for_user:
                return _("Delete Confidential Activity")

        return _("Delete Activity: {{title}}")

    def get_list_title(self):
        if self.view.participants.exists():
            if self.view.participants.count() == 1:
                return _("Activities for {person}").format(person=str(self.view.participants.first()))
            else:
                return _("Activities for Multiple Persons")

        if self.view.companies.exists():
            return _("Activities for {}").format(", ".join(self.view.companies.values_list("name", flat=True)))
        return _("Activities")

    def get_create_title(self):
        if self.view.entry:
            return _("New Activity for {entry}").format(entry=self.view.entry.computed_str)
        return _("New Activity")


class ActivityParticipantTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Participation Status")


class ActivityChartModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Activity Chart")
