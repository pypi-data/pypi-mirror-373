import datetime

import pytest
from django.utils import timezone
from psycopg.types.range import DateRange
from selenium.webdriver.common.action_chains import ActionChains
from wbcore.contrib.authentication.factories import SuperUserFactory
from wbcore.contrib.authentication.models import User
from wbcore.contrib.authentication.tests.e2e import create_main_company_user
from wbcore.contrib.directory.models import (
    Company,
    EmployerEmployeeRelationship,
    Person,
)
from wbcore.contrib.directory.serializers import (
    ClientManagerModelSerializer,
    CompanyModelSerializer,
    PersonModelSerializer,
)
from wbcore.contrib.directory.tests.e2e import (
    create_new_cmr_instance,
    create_new_company_instance,
    create_new_person_instance,
    set_up_companies,
    set_up_persons,
)
from wbcore.contrib.directory.viewsets.display import CMR_Color
from wbcore.test import (
    click_button_by_label,
    click_close_all_widgets,
    click_new_button,
    delete_list_entry,
    does_background_color_match,
    edit_list_instance,
    find_element_by_text,
    is_counter_as_expected,
    is_error_visible,
    is_string_not_visible,
    is_tag_not_visible,
    is_tag_visible,
    is_text_visible,
    navigate_to_filter,
    open_menu_item,
    select_async_filter,
    select_column_filter,
    select_filter,
    set_up,
)

from wbcrm.factories import ActivityFactory
from wbcrm.models import Activity
from wbcrm.serializers import ActivityModelSerializer
from wbcrm.tests.e2e import create_new_activity_instance, set_up_activities

USER_PASSWORD = "User_Password"


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.django_db
class TestCRMFilters:
    def test_entry_filter(self, live_server, selenium):
        """
        Testing the "Entry"-Filter.
        """

        # Creating a test user
        user: User = SuperUserFactory(plaintext_password=USER_PASSWORD)
        # Creating three test companies with different last activities.
        companies = set_up_companies()
        now = timezone.now()
        period_a = DateRange(now - datetime.timedelta(days=15, hours=2), now - datetime.timedelta(days=15))
        period_b = DateRange(now - datetime.timedelta(days=60, hours=2), now - datetime.timedelta(days=60))
        ActivityFactory(period=period_a, companies=[companies[0]])
        ActivityFactory(period=period_b, companies=[companies[1], companies[2]])

        set_up(selenium, live_server, user.email, USER_PASSWORD)
        navigate_to_filter(selenium, "CRM", "Companies")

        # And the beginning all three companies should be visible, since no filter is set.
        assert is_counter_as_expected(selenium, Company.objects.count())

        # With no filters selected the there should be a message with the hint "No filter criteria yet"
        assert is_text_visible(selenium, "No filter criteria yet")

        # Select a "No Activity" - filter. Filtering for all companies, that had no activity in the last month.
        select_filter(selenium, "No Activity:", "Last Month")

        # The "No filter criteria yet" text should now be gone and instead there should be a "filter-tag" with "Last Month".
        assert is_string_not_visible(selenium, "No filter criteria yet")
        assert is_tag_visible(selenium, "Last Month")

        # Only two companies should be listed, since one company had an activity withing the last month.
        assert is_text_visible(selenium, "Company B")
        assert is_text_visible(selenium, "Company C")
        assert is_string_not_visible(selenium, "Company A")
        assert is_counter_as_expected(selenium, 2)

        # Selecting an additional column filter to filter by company type.
        select_column_filter(selenium, "Type", "Type A")

        # After selecting the additional filter there should also be an additional filter tag corresponding to the filter and the number of companies should be one.
        assert is_tag_visible(selenium, "Last Month")
        assert is_tag_visible(selenium, "Type A")
        assert is_counter_as_expected(selenium, 1)
        assert is_text_visible(selenium, "Company B")
        assert is_string_not_visible(selenium, "Company C")

        # Resetting the filters
        click_button_by_label(selenium, "Clear all filters")
        assert is_text_visible(selenium, "No filter criteria yet")
        assert is_tag_not_visible(selenium, "Type A")
        assert is_counter_as_expected(selenium, Company.objects.count())

        # Close all widgets and switch to the person list
        click_close_all_widgets(selenium)
        set_up_persons()
        navigate_to_filter(selenium, "Persons")

        assert is_counter_as_expected(selenium, Person.objects.count())
        assert is_text_visible(selenium, "No filter criteria yet")

        # Select a "Specializations" - filter. Filtering for all persons with "Specialization C".
        select_async_filter(selenium, "Specializations:", "Specialization C")
        assert is_tag_visible(selenium, "Specialization C")
        assert is_string_not_visible(selenium, "No filter criteria yet")

        # Only two persons should be listed
        assert is_string_not_visible(selenium, "Henry Kalb")
        assert is_text_visible(selenium, "Konrad Zuse")
        assert is_text_visible(selenium, "Ada Lovelace")
        filter_count = Person.objects.filter(specializations__title="Specialization C").count()
        assert is_counter_as_expected(selenium, filter_count)

        # Selecting an additional column filter to filter by person status.
        select_column_filter(selenium, "Status", "Status C")

        # After selecting the additional filter there should also be an additional filter tag corresponding to the filter and the number of persons should be one.
        assert is_tag_visible(selenium, "Specialization C")
        assert is_tag_visible(selenium, "Status C")
        assert is_string_not_visible(selenium, "Konrad Zuse")
        assert is_text_visible(selenium, "Ada Lovelace")
        filter_count = EmployerEmployeeRelationship.objects.filter(
            employer__in=Company.objects.filter(customer_status__title="Status C"),
            employee__in=Person.objects.filter(specializations__title="Specialization C"),
            primary=True,
        )
        assert is_counter_as_expected(selenium, filter_count)

    def test_activity_filter(self, live_server, selenium):
        """
        Testing the "Type" and "Status" - Filter
        """
        # Creating a test user and setting up selenium
        user: User = SuperUserFactory(plaintext_password=USER_PASSWORD)
        set_up_activities(user.profile)
        set_up(selenium, live_server, user.email, USER_PASSWORD)

        navigate_to_filter(selenium, "CRM", "Activities")

        # And the beginning all three activities should be visible, since no filter is set.
        filter_count = Activity.objects.all().count()
        assert is_counter_as_expected(selenium, filter_count)

        # With no filters selected the there should be a message with the hint "No filter criteria yet"
        assert is_text_visible(selenium, "No filter criteria yet")

        # Selecting a column filter to filter by activity type.
        select_column_filter(selenium, "Type", "Meeting")

        assert is_string_not_visible(selenium, "No filter criteria yet")
        assert is_tag_visible(selenium, "Meeting")

        # After filtering for the type there should be only two activities displayed
        filter_count = Activity.objects.filter(type__title="Meeting").count()
        assert is_counter_as_expected(selenium, filter_count)
        assert is_text_visible(selenium, "Activity A")
        assert is_text_visible(selenium, "Activity B")
        assert is_string_not_visible(selenium, "Activity C")

        # Select a "Status" - filter. Filtering for all activities, that have the status "Finished".
        select_filter(selenium, "Status:", "Finished")

        assert is_string_not_visible(selenium, "Activity A")
        assert is_text_visible(selenium, "Activity B")
        filter_count = Activity.objects.filter(type__title="Meeting", status=Activity.Status.FINISHED).count()
        assert is_counter_as_expected(selenium, filter_count)


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.django_db
class TestCRMActivities:
    def test_create_edit_delete_activity(self, live_server, selenium):
        """
        Creates, edits and deletes an activity.
        """
        # Creating a test user and setting up selenium
        user: User = SuperUserFactory(plaintext_password=USER_PASSWORD)
        actions = ActionChains(selenium, 1000)
        set_up(selenium, live_server, user.email, USER_PASSWORD)

        # # -----> CREATE <----- #
        activity_a = create_new_activity_instance(selenium, ["title", "type"], "Type A", "Activity A", False)
        open_menu_item(selenium, "Activities", perform_mouse_move=True)
        assert is_text_visible(selenium, activity_a.title)
        assert is_counter_as_expected(selenium, Activity.objects.count())

        click_new_button(selenium)
        assert is_text_visible(selenium, "New Activity")

        # Trying to create an activity without filling out anything -> We expect an error to be thrown.
        click_button_by_label(selenium, "Save and close")
        assert is_error_visible(selenium)

        activity_b = create_new_activity_instance(selenium, ["title", "type"], None, "Activity B")
        assert is_text_visible(selenium, activity_b.title)
        assert is_counter_as_expected(selenium, Activity.objects.count())

        # -----> Edit <----- #

        edit_list_instance(selenium, actions, activity_a, ActivityModelSerializer(activity_a), {"title": "A Activity"})

        assert is_string_not_visible(selenium, "Activity A")
        assert is_text_visible(selenium, "A Activity")
        assert is_counter_as_expected(selenium, Activity.objects.count())

        # -----> Delete <----- #
        delete_list_entry(selenium, actions, activity_b.title)
        assert is_counter_as_expected(selenium, Activity.objects.count())
        assert is_string_not_visible(selenium, "Activity A")
        assert is_string_not_visible(selenium, "Activity B")


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.django_db
class TestCRMEntries:
    def test_create_edit_delete_company(self, live_server, selenium):
        """
        Creating a new company from the company list view. After creating the company it should be displayed in the company list view.
        """
        # Creating a test user
        user: User = SuperUserFactory(plaintext_password=USER_PASSWORD)
        actions = ActionChains(selenium, 1000)
        set_up(selenium, live_server, user.email, USER_PASSWORD)

        # -----> CREATE <----- #
        company_a = create_new_company_instance(
            selenium, ["name", "customer_status"], "Company A", "Test Status", False
        )
        open_menu_item(selenium, "Companies", perform_mouse_move=True)
        assert is_text_visible(selenium, company_a.name)
        assert is_counter_as_expected(selenium, Company.objects.count())

        click_new_button(selenium)
        assert is_text_visible(selenium, "New Company")

        # Trying to create an activity without filling out anything -> We expect an error to be thrown.
        click_button_by_label(selenium, "Save and close")
        assert is_error_visible(selenium)
        company_b = create_new_company_instance(selenium, ["name", "customer_status"], "Company B")

        assert is_text_visible(selenium, company_b.name)
        assert is_counter_as_expected(selenium, Company.objects.count())

        # -----> Edit <----- #

        edit_list_instance(selenium, actions, company_a.name, CompanyModelSerializer(company_a), {"name": "A Company"})
        assert is_string_not_visible(selenium, "Company A")
        assert is_text_visible(selenium, "A Company")
        assert is_counter_as_expected(selenium, Company.objects.count())

        # -----> Delete <----- #

        delete_list_entry(selenium, actions, company_b.name)
        assert is_counter_as_expected(selenium, Company.objects.count())
        assert is_text_visible(selenium, "A Company")
        assert is_string_not_visible(selenium, "Company A")
        assert is_string_not_visible(selenium, "Company B")

    def test_create_edit_delete_person(self, live_server, selenium):
        """
        Creating a new person from the person list view. After creating the person it should be displayed in the person list view.
        """
        # Creating a test user
        user: User = SuperUserFactory(plaintext_password=USER_PASSWORD)
        actions = ActionChains(selenium, 1000)
        set_up(selenium, live_server, user.email, USER_PASSWORD)

        # -----> CREATE <----- #
        person_a = create_new_person_instance(
            selenium, ["first_name", "last_name", "prefix"], "Max", "Mustermann", "Mr.", False
        )
        open_menu_item(selenium, "Persons", perform_mouse_move=True)
        assert is_text_visible(selenium, f"{person_a.first_name} {person_a.last_name}")
        assert is_counter_as_expected(selenium, Person.objects.count())

        click_new_button(selenium)
        assert is_text_visible(selenium, "New Person")

        # Trying to create an activity without filling out anything -> We expect an error to be thrown.
        click_button_by_label(selenium, "Save and close")
        assert is_error_visible(selenium)
        person_b = create_new_person_instance(
            selenium, ["first_name", "last_name", "prefix"], "Maike", "Musterfrau", "Mrs.", False
        )

        assert is_text_visible(selenium, f"{person_b.first_name} {person_b.last_name}")
        assert is_counter_as_expected(selenium, Person.objects.count())

        # -----> Edit <----- #

        edit_list_instance(
            selenium,
            actions,
            f"{person_a.first_name} {person_a.last_name}",
            PersonModelSerializer(person_a),
            {"first_name": "Maxissimus"},
        )
        assert is_string_not_visible(selenium, "Max Mustermann")
        assert is_text_visible(selenium, "Maxissimus Mustermann")
        assert is_counter_as_expected(selenium, Person.objects.count())

        # -----> Delete <----- #

        delete_list_entry(selenium, actions, f"{person_b.first_name} {person_b.last_name}")
        assert is_counter_as_expected(selenium, Person.objects.count())
        assert is_text_visible(selenium, "Maxissimus Mustermann")
        assert is_string_not_visible(selenium, "Max Mustermann")
        assert is_string_not_visible(selenium, "Maike Mustermann")


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.django_db
# This test class is currently bugged because of frontend issues.
class TestCRMRelationShipManagement:
    def test_create_edit_and_delete_relationship(self, live_server, selenium):
        """
        Creates, edits and deletes a Customer-Employer-Relationship.
        """
        user: User = create_main_company_user(USER_PASSWORD)
        actions = ActionChains(selenium, 1000)
        set_up(selenium, live_server, user.email, USER_PASSWORD)
        set_up_persons()

        # -----> CREATE <----- #
        cmr = create_new_cmr_instance(selenium, ["client", "relationship_manager", "primary"], True, False)
        open_menu_item(selenium, "Client Manager Relationships", perform_mouse_move=True)
        cmr_element = find_element_by_text(selenium, cmr.client.computed_str)

        assert is_counter_as_expected(selenium, 1)
        assert is_text_visible(selenium, cmr.client.computed_str)
        assert is_text_visible(selenium, cmr.relationship_manager.computed_str)
        assert does_background_color_match(cmr_element, CMR_Color.DRAFT.value)

        # # -----> Edit <----- #

        edit_list_instance(
            selenium,
            actions,
            cmr.client.computed_str,
            ClientManagerModelSerializer(cmr),
            {"relationship_manager": user.profile.computed_str},
        )
        assert is_string_not_visible(selenium, cmr.relationship_manager.computed_str)
        assert is_text_visible(selenium, user.profile.computed_str)
        assert is_counter_as_expected(selenium, Person.objects.count())

        # # -----> Approve <----- #
        # TODO Implement approve
        # -----> Delete <----- #
        # TODO Implement delete
