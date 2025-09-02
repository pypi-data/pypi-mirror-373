from django.utils.translation import gettext as _
from wbcore.contrib.authentication.models import User
from wbcore.contrib.directory.models import Person
from wbcore.contrib.workflow.decorators import register_assignee
from wbcore.contrib.workflow.models import ProcessStep

# We need to migrate upon name changes!


# TODO: Generalize this through field filter
@register_assignee("Activity Assignee")
def activity_assignee(process_step: ProcessStep, **kwargs) -> User | None:
    if hasattr(process_step.process.instance, "assigned_to"):
        assignee: Person = getattr(process_step.process.instance, "assigned_to")
        if hasattr(assignee, "user_account"):
            return assignee.user_account
        else:
            error_message = _("Assignee has no user account!")
    else:
        error_message = _("No activity attached!")

    process_step.step.get_casted_step().set_failed(
        process_step, _("Error in assignee method: {}").format(error_message)
    )
    return None
