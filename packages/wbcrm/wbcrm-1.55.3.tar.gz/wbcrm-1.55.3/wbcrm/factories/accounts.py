import factory
from slugify import slugify

from wbcrm.models.accounts import Account, AccountRole, AccountRoleType


class AccountFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("company")
    status = Account.Status.OPEN
    # owner =
    is_public = True
    is_active = True
    is_terminal_account = True

    class Meta:
        model = Account


class AccountWithOwnerFactory(AccountFactory):
    owner = factory.SubFactory("wbcore.contrib.directory.factories.entries.EntryFactory")


class AccountRoleTypeFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("word")
    key = factory.LazyAttribute(lambda o: slugify(o.title))

    class Meta:
        model = AccountRoleType
        django_get_or_create = ["key"]


class AccountRoleFactory(factory.django.DjangoModelFactory):
    role_type = factory.SubFactory("wbcrm.factories.AccountRoleTypeFactory")
    entry = factory.SubFactory("wbcore.contrib.directory.factories.entries.EntryFactory")
    account = factory.SubFactory("wbcrm.factories.AccountFactory", parent=None)
    is_hidden = False

    @factory.post_generation
    def authorized_hidden_users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.authorized_hidden_users.add(user)

    @factory.post_generation
    def visibility_daterange(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            v = self.validity_set.first()
            v.timespan = extracted
            v.save()

    class Meta:
        model = AccountRole
