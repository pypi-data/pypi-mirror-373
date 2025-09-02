from wbcore.tests.conftest import *  # isort:skip
import os

from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.agenda.factories import CalendarItemFactory, ConferenceRoomFactory
from wbcore.contrib.authentication.factories import (
    InternalUserFactory,
    SuperUserFactory,
    UserActivityFactory,
    UserFactory,
)
from wbcore.contrib.directory.factories import (
    CompanyFactory,
    EmailContactFactory,
    EmployerEmployeeRelationshipFactory,
    EntryFactory,
    PersonFactory,
)
from wbcrm.factories import (
    AccountFactory,
    AccountRoleFactory,
    AccountRoleTypeFactory,
    ActivityCompanyFactory,
    ActivityFactory,
    ActivityParticipantFactory,
    ActivityPersonFactory,
    ActivityTypeFactory,
    GroupFactory,
    ProductFactory,
    RecurringActivityFactory,
)

register(EntryFactory)
register(InternalUserFactory)
register(EmailContactFactory)
register(CompanyFactory)
register(PersonFactory)
register(EmployerEmployeeRelationshipFactory)
register(ActivityFactory)
register(ActivityTypeFactory)
register(RecurringActivityFactory)
register(ActivityCompanyFactory)
register(ActivityPersonFactory)
register(ActivityParticipantFactory)
register(GroupFactory)
register(ProductFactory)
register(ConferenceRoomFactory)
register(AccountFactory)
register(AccountRoleFactory)
register(AccountRoleTypeFactory)
register(CalendarItemFactory)

# Authentication
register(UserFactory)
register(SuperUserFactory, "superuser")
register(UserActivityFactory)


@pytest.fixture(autouse=True, scope="session")
def django_test_environment(django_test_environment):
    from django.apps import apps

    get_models = apps.get_models

    for m in [m for m in get_models() if not m._meta.managed]:
        m._meta.managed = True


@pytest.fixture
def chrome_options(chrome_options):
    # chrome_options.add_argument("--headless=new")
    return chrome_options


pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("geography"))
