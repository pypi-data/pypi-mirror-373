import pytest
from faker import Faker
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories.users import UserFactory
from wbcore.contrib.directory.models import Entry

from wbcrm.factories.accounts import AccountFactory, AccountRoleFactory
from wbcrm.models import Account
from wbcrm.viewsets.accounts import (
    AccountModelViewSet,
    AccountRepresentationViewSet,
    AccountRoleAccountModelViewSet,
    ChildAccountAccountModelViewSet,
    InheritedAccountRoleAccountModelViewSet,
)

fake = Faker()


@pytest.mark.django_db
class TestAccountViewset:
    @pytest.fixture
    def account_user(self):
        # True, we create a superuser

        if fake.pybool():
            user = UserFactory.create(is_superuser=True)
        else:
            user = UserFactory.create(is_superuser=True)
        entry = Entry.objects.get(id=user.profile.id)

        # Create a bunch of account and roles
        public_account = AccountFactory.create(is_public=True)
        AccountRoleFactory.create(account=public_account, entry=entry)
        AccountRoleFactory.create(account=public_account)
        private_account = AccountFactory.create(is_public=False)
        AccountRoleFactory.create(account=private_account, entry=entry)
        return user

    @pytest.mark.parametrize(
        "viewset_class",
        [
            AccountRepresentationViewSet,
            AccountModelViewSet,
        ],
    )
    def test_ensure_permission_on_account(self, account_user, viewset_class):
        request = APIRequestFactory().get("")
        request.user = account_user
        viewset = viewset_class(request=request)
        assert set(viewset.get_queryset()) == set(Account.objects.filter_for_user(account_user))

    def test_ensure_permission_for_nested_view(self, account_user, account_factory):
        request = APIRequestFactory().get("")
        request.user = account_user
        parent_account = Account.objects.first()
        account_factory.create(parent=parent_account, is_public=True)
        viewset = ChildAccountAccountModelViewSet(request=request, kwargs={"account_id": parent_account.id})

        assert set(viewset.get_queryset()) == set(
            Account.objects.filter(parent=parent_account).filter_for_user(account_user)
        )

    def test_ensure_permission_on_account_role_account(self, user, account_factory, account_role_factory):
        request = APIRequestFactory().get("")
        request.user = user
        parent_account = account_factory.create()
        child_account = account_factory.create(parent=parent_account)
        viewset_account_role = AccountRoleAccountModelViewSet(
            request=request, kwargs={"account_id": parent_account.id}
        )
        viewset_inherited_account_role = InheritedAccountRoleAccountModelViewSet(
            request=request, kwargs={"account_id": child_account.id}
        )
        with pytest.raises((AuthenticationFailed,)):
            viewset_account_role.get_queryset()
        with pytest.raises((AuthenticationFailed,)):
            viewset_inherited_account_role.get_queryset()

        role = account_role_factory.create(account=parent_account, entry=Entry.objects.get(id=user.profile.id))
        account_role_factory.create(account=parent_account)  # noise account role
        assert set(viewset_account_role.get_queryset()) == {role}

        account_role_factory.create(
            account=child_account, entry=Entry.objects.get(id=user.profile.id)
        )  # noise account role
        assert set(viewset_inherited_account_role.get_queryset()) == {role}
