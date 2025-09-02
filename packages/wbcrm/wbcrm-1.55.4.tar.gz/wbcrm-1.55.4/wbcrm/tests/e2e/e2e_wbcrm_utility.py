from selenium.webdriver.remote.webdriver import WebDriver
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.contrib.directory.models import Person
from wbcore.test import (
    click_element_by_path,
    fill_out_form_fields,
    open_create_instance,
)

from wbcrm.factories import ActivityFactory, ActivityTypeFactory
from wbcrm.models import Activity, ActivityType
from wbcrm.serializers import ActivityModelSerializer


def set_up_activities(creator: Person = None):
    """Sets up three activities for testing purposes with fixed participants, types and titles.

    Args:
        creator (Person | None, optional): The person that is used as the activities creator. Defaults to None.
    """
    type_a = ActivityTypeFactory(title="Meeting")
    type_b = ActivityTypeFactory(title="Call")
    participant_a = PersonFactory(last_name="Turing")
    participant_b = PersonFactory(last_name="Zuse")
    participant_c = PersonFactory(last_name="Lovelace")
    activity_creator = creator if creator else PersonFactory()
    ActivityFactory(
        title="Activity A",
        type=type_a,
        creator=activity_creator,
        preceded_by=None,
        participants=[participant_a, participant_c],
        status=Activity.Status.PLANNED,
    )
    ActivityFactory(
        title="Activity B",
        type=type_a,
        creator=activity_creator,
        preceded_by=None,
        participants=[participant_a, participant_b],
        status=Activity.Status.FINISHED,
    )
    ActivityFactory(
        title="Activity C",
        type=type_b,
        creator=activity_creator,
        preceded_by=None,
        participants=[participant_b, participant_c],
        status=Activity.Status.PLANNED,
    )


def create_new_activity_instance(
    driver: WebDriver,
    field_list: list[str],
    type_title="",
    activity_title="",
    is_create_instance_open=True,
) -> Activity:
    """A function that automatically creates a new activity for selenium e2e-tests.
    After creating the instance this function will close the create-widget.

    Args:
        driver (WebDriver): The Selenium webdriver.
        field_list (list[str]): List of fields to be filled in the creation mask. The field names must match the names in the ActivitySerializer.
        type_title (str, optional): The title of the activity type. Defaults to "".
        activity_title (str, optional): The title of the activity. Defaults to "".
        is_create_instance_open (bool, optional): Should be true if the create-widget is already open. Defaults to True.
    """
    if not is_create_instance_open:
        open_create_instance(driver, "CRM", "Create Activity")

    type_title = type_title if type_title else "Test Activity Type"
    activity_title = activity_title if activity_title else "Test Activity"
    if ActivityType.objects.filter(title=activity_title).exists():
        activity_type = ActivityType.objects.get(title=activity_title)
    else:
        activity_type = ActivityTypeFactory(title=type_title)
    activity = ActivityFactory.build(title=activity_title, type=activity_type)
    serializer = ActivityModelSerializer(activity)
    fill_out_form_fields(driver, serializer, field_list, activity)
    click_element_by_path(driver, "//button[@label='Save and close']")
    return activity
