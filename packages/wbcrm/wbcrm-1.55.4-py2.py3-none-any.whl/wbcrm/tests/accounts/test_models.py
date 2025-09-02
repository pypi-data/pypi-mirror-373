from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from faker import Faker
from psycopg.types.range import DateRange
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.directory.signals import deactivate_profile

from wbcrm.models import Account, AccountRole, AccountRoleValidity

fake = Faker()


@pytest.mark.django_db
class TestAccountModel:
    def test_init(self, account):
        assert account.id is not None

    def test_close_account_set_inactive(self, account):
        assert account.is_active
        account.status = Account.Status.CLOSE
        account.save()
        assert not account.is_active

    def test_disable_account_set_status_close(self, account):
        assert account.status == Account.Status.OPEN
        account.delete()
        assert not account.is_active
        assert account.status == Account.Status.CLOSE

    def test_account_with_owner_create_account_role(self, account_factory, entry_factory):
        customer = entry_factory.create()
        account = account_factory.create(owner=customer)
        assert account.roles.filter(entry=customer, role_type__key="customer").exists()

    def test_leaf_account_automatically_set_to_terminal(self, account_factory):
        parent_account = account_factory.create()

        assert parent_account.is_terminal_account is True
        child_account1 = account_factory.create(parent=parent_account, is_terminal_account=False)
        child_account2 = account_factory.create(parent=parent_account, is_terminal_account=False)

        parent_account.refresh_from_db()
        child_account1.refresh_from_db()
        child_account2.refresh_from_db()

        assert parent_account.is_terminal_account is False
        assert child_account1.is_terminal_account is True
        assert child_account2.is_terminal_account is True

        child_account1.delete(no_deletion=False)
        parent_account.refresh_from_db()
        assert parent_account.is_terminal_account is False  # because there is still another child

        child_account2.delete(no_deletion=False)
        parent_account.refresh_from_db()
        assert parent_account.is_terminal_account is True  # There is no children left so we expect it to become leaf

    def test_disabled_parent_account_disabled_children(self, account_factory):
        parent_account = account_factory.create()
        child_account = account_factory.create(parent=parent_account)
        assert child_account.is_active
        assert parent_account.is_active

        parent_account.is_active = False
        parent_account.save()

        child_account.refresh_from_db()
        assert not child_account.is_active

    def test_private_root_account_set_children_as_private(self, account_factory):
        parent_account = account_factory.create(is_public=True)
        child_account = account_factory.create(parent=parent_account, is_public=True)
        parent_account.is_public = False
        parent_account.save()
        child_account.refresh_from_db()
        assert not child_account.is_public

    def test_can_manage(self, account, user):
        assert not account.can_administrate(user)

        perm = Permission.objects.get(content_type__app_label="wbcrm", codename="administrate_account")
        user.user_permissions.add(perm)

        user = get_user_model().objects.get(
            id=user.id
        )  # we refetch user to clear perm cache, doesn't happen with refresh_from_db
        assert account.can_administrate(user)

    def test_get_inherited_roles_for_account(self, account_factory, account_role_factory):
        parent_account = account_factory.create()
        parent_role = account_role_factory.create(account=parent_account)
        child_account = account_factory.create(parent=parent_account)
        child_role = account_role_factory.create(account=child_account)
        assert set(child_account.get_inherited_roles_for_account()) == {parent_role}
        assert set(child_account.get_inherited_roles_for_account(include_self=True)) == {child_role, parent_role}

    @pytest.mark.parametrize("validity_date,account__is_public", [(fake.date_object(), False)])
    def test_can_see_account(self, user, account, account_role_factory, validity_date):
        # Check user doesn't see permission on the account by default
        assert not account.can_see_account(user, validity_date)
        role = account_role_factory.create(account=account, entry=Entry.objects.get(id=user.profile.id))
        # with a valid role, they can see it
        assert account.can_see_account(user, validity_date=validity_date)

        # with an unvalid role, they cannot see it
        role.validity_set.first().timespan = DateRange(date.min, validity_date - timedelta(days=1))
        role.validity_set.first().save()
        assert account.can_see_account(user, validity_date=validity_date)

    @pytest.mark.parametrize("account__is_public", [True, False])
    def test_can_see_account_with_internal_employee(self, internal_user_factory, account):
        # Check user doesn't see permission on the account by default

        # with being an internal user, they can see it
        assert account.can_see_account(internal_user_factory.create()) == account.is_public

    @pytest.mark.parametrize("account__is_public", [True])
    def test_normaluser_cannot_see_account_public_account(self, user, account):
        assert not account.can_see_account(user)

    def test_get_accounts_for_customer(self, account_factory, company_factory, employer_employee_relationship_factory):
        owner1 = company_factory.create()
        employee1 = employer_employee_relationship_factory.create(employer=owner1).employee
        owner2 = company_factory.create()
        employee2 = employer_employee_relationship_factory.create(employer=owner2).employee

        parent_account = account_factory.create(owner=owner1)
        other_parent_account = account_factory.create(owner=owner1)
        child_account = account_factory.create(parent=parent_account, owner=owner2)
        # test if all child account also shows in the queryset as well as the direct related account for that owner
        assert set(Account.get_accounts_for_customer(owner1.entry_ptr)) == {
            parent_account,
            other_parent_account,
            child_account,
        }
        assert set(Account.get_accounts_for_customer(employee1.entry_ptr)) == {
            parent_account,
            other_parent_account,
            child_account,
        }
        assert set(Account.get_accounts_for_customer(owner2.entry_ptr)) == {child_account}
        assert set(Account.get_accounts_for_customer(employee2.entry_ptr)) == {child_account}

    def test_get_managed_accounts_for_entry(self, entry, account_factory, account_role_factory):
        main_role = account_role_factory.create(entry=entry)
        child_account = account_factory.create(parent=main_role.account)
        other_account = account_factory.create()  # noqa
        other_role = account_role_factory.create()  # noqa
        assert set(Account.get_managed_accounts_for_entry(entry)) == {main_role.account, child_account}

    def test_handle_user_deactivation(self, account_role_factory, person_factory):
        profile = person_factory.create()
        substitute_profile = person_factory.create()

        valid_role = account_role_factory.create(entry=Entry.objects.get(id=profile.id))
        unvalid_role = account_role_factory.create(
            entry=Entry.objects.get(id=profile.id), visibility_daterange=DateRange(date.min, date.today())
        )

        deactivate_profile.send(AccountRole, instance=profile, substitute_profile=substitute_profile)
        valid_role.refresh_from_db()
        unvalid_role.refresh_from_db()
        assert valid_role.validity_set.first().timespan == DateRange(date.min, date.today() - timedelta(days=1))
        assert valid_role.entry.id == profile.id
        assert unvalid_role.entry.id == profile.id

        new_role = AccountRole.objects.get(entry_id=substitute_profile.id, account=valid_role.account)
        assert new_role.validity_set.first().timespan == DateRange(date.today() - timedelta(days=1), date.max)

    @pytest.mark.parametrize(
        "validity_date,is_internal_user, is_superuser",
        [
            (fake.date_object(), True, True),
            (fake.date_object(), False, True),
            (fake.date_object(), True, False),
            (fake.date_object(), False, False),
        ],
    )
    def test_filter_for_user(
        self,
        user_factory,
        internal_user_factory,
        account_factory,
        account_role_factory,
        validity_date,
        is_internal_user,
        is_superuser,
    ):
        # We assume role logic are tested in the AccountRole manager unit test
        # so we test here only:
        # - chain filtering
        # - Return account where user has a valid role
        # - and Return public account if user is superuser or internal

        if is_internal_user:
            user = internal_user_factory.create()
        else:
            user = user_factory.create()
        if is_superuser:
            user.user_permissions.add(
                Permission.objects.get(content_type__app_label="wbcrm", codename="administrate_account")
            )
        profile_entry = Entry.objects.get(id=user.profile.id)
        public_account = account_factory.create(is_public=True)
        private_account = account_factory.create(is_public=False)  # noqa
        valid_role = account_role_factory.create(account__is_public=fake.pybool(), entry=profile_entry)
        children_valid_role_account = account_factory.create(
            parent=valid_role.account, is_public=True
        )  # check that entry with role on the parent account can access the public children account
        account_factory.create(
            parent=valid_role.account, is_public=False
        )  # check that entry with role on the parent account cannot access private children account

        unvalid_role = account_role_factory.create(  # noqa
            account__is_public=False,
            entry=profile_entry,
            visibility_daterange=DateRange(date.min, validity_date - timedelta(days=1)),
        )
        user = get_user_model().objects.get(id=user.id)
        if is_superuser:
            assert set(Account.objects.filter_for_user(user, validity_date)) == set(Account.objects.all())
        elif is_internal_user:
            assert set(Account.objects.filter_for_user(user, validity_date)) == {
                public_account,
                valid_role.account,
                children_valid_role_account,
            }
            assert set(Account.objects.filter(id=public_account.id).filter_for_user(user, validity_date)) == {
                public_account
            }  # basic test filter chainage
        else:
            assert set(Account.objects.filter_for_user(user, validity_date)) == {
                valid_role.account,
                children_valid_role_account,
            }

    def test_cannot_merge_account_with_children(self, account_factory):
        """
        Check that we cannot merge an account that still has children
        """
        base_account = account_factory.create()
        merged_account = account_factory.create()
        children_merged_account = account_factory.create(parent=merged_account)
        base_account.merge(merged_account)
        merged_account.refresh_from_db()
        assert merged_account

        # but can merge the children into the parent account
        merged_account.merge(children_merged_account)
        with pytest.raises(Account.DoesNotExist):
            children_merged_account.refresh_from_db()

    def test_cannot_merge_account_on_different_trees(self, account_factory):
        """
        Check that we cannot merge an account that still has children
        """
        base_account = account_factory.create(parent=account_factory.create())
        merged_account = account_factory.create(parent=account_factory.create())
        account_factory.create(parent=merged_account)
        base_account.merge(merged_account)
        merged_account.refresh_from_db()
        assert merged_account

    def test_account_merging(self, account_factory, account_role_factory, user):
        # TODO implemetns for commission
        pivot_date = date(2023, 1, 1)
        base_account = account_factory.create()
        base_account_role = account_role_factory.create(
            account=base_account, visibility_daterange=DateRange(date.min, pivot_date)
        )
        base_account_role_validity = base_account_role.validity_set.first()

        merged_account = account_factory.create()
        merged_account_role_overlapping = account_role_factory.create(
            account=merged_account, entry=base_account_role.entry, visibility_daterange=DateRange(pivot_date, date.max)
        )
        merged_account_role_overlapping.authorized_hidden_users.add(user)
        merged_account_role_validity = merged_account_role_overlapping.validity_set.first()

        merged_account_role_different = account_role_factory.create(account=merged_account)
        merged_account_role_different_validity = merged_account_role_different.validity_set.first()

        base_account.merge(merged_account)

        # test that the none overlapping role were forwarded to the base account
        assert set(base_account.roles.all()) == {base_account_role, merged_account_role_different}

        # test that the validity set for the base role got the new validity from the base merged account role
        assert set(base_account_role.validity_set.all()) == {base_account_role_validity, merged_account_role_validity}

        # test that the authorized user set on the merged account role were forwarded to the base account
        assert set(base_account_role.authorized_hidden_users.all()) == {user}

        # test that the merged account was deleted
        with pytest.raises(Account.DoesNotExist):
            merged_account.refresh_from_db()

        # test that the non overlapping role correctly follows the role
        role = AccountRole.objects.get(account=base_account, entry=merged_account_role_different.entry)
        assert set(role.validity_set.all()) == {merged_account_role_different_validity}


@pytest.mark.django_db
class TestAccountRoleModel:
    def test_init(self, account_role):
        assert account_role.id is not None
        validity = account_role.validity_set.first()
        assert validity
        assert validity.timespan == DateRange(date.min, date.max)

    def test_hidden_role_set_account_to_private(self, account_factory, account_role_factory):
        public_account = account_factory.create(is_public=True)
        role = account_role_factory.create(account=public_account, is_hidden=True)
        assert not role.account.is_public

    # def test_filter_for_user(self, ):
    #     # here we want to check that the chained filtering works and
    #     # - Internal or super user can see their roles + public account roles if there are unhidden + hidden role if they have the right to see them
    #     # - Otherwise, can only see direct roles
    #     # - Check if the annotation is_currently_valid is there
    @pytest.mark.parametrize(
        "is_superuser,is_internal_user",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_filter_related_account_roles_for_internal_user(
        self, user_factory, internal_user_factory, account_role_factory, is_superuser, is_internal_user
    ):
        if is_internal_user:
            user = internal_user_factory.create()
        else:
            user = user_factory.create()
        if is_superuser:
            user.user_permissions.add(
                Permission.objects.get(content_type__app_label="wbcrm", codename="administrate_account")
            )
        role_unhidden_public_account = account_role_factory.create(is_hidden=False, account__is_public=True)
        role_unhidden_private_account = account_role_factory.create(is_hidden=False, account__is_public=False)  # noqa
        role_hidden_public_account_without_privilege = account_role_factory.create(  # noqa
            is_hidden=True, account__is_public=True
        )

        role_hidden_private_account_with_privilege = account_role_factory.create(
            is_hidden=True, account__is_public=False, authorized_hidden_users=[user]
        )
        role_direct = account_role_factory.create(
            entry=Entry.objects.get(id=user.profile.id),
            account__is_public=fake.pybool(),
        )
        role_indirect_private_account = account_role_factory.create(account__is_public=False)  # noqa

        if is_superuser:
            assert set(AccountRole.objects.filter_for_user(user)) == set(AccountRole.objects.all())
        elif is_internal_user:
            assert set(AccountRole.objects.filter_for_user(user)) == {
                role_unhidden_public_account,
                role_hidden_private_account_with_privilege,
                role_direct,
            }
            assert set(AccountRole.objects.filter(is_hidden=True).filter_for_user(user)) == {
                role_hidden_private_account_with_privilege
            }  # Test that chain filtering works
        else:
            assert set(AccountRole.objects.filter_for_user(user)) == {role_direct}


@pytest.mark.django_db
class TestAccountRoleValidityModel:
    @pytest.mark.parametrize("validity_date", [fake.date_object()])
    def test_get_role_validity_subquery(self, account_role, validity_date):
        assert AccountRole.objects.count() == 1
        assert (
            AccountRole.objects.annotate(is_valid=AccountRoleValidity.get_role_validity_subquery(validity_date))
            .filter(is_valid=True)
            .count()
            == 1
        )

        validity = account_role.validity_set.first()
        validity.timespan = DateRange(date.min, validity_date - timedelta(days=1))
        validity.save()
        assert (
            not AccountRole.objects.annotate(is_valid=AccountRoleValidity.get_role_validity_subquery(validity_date))
            .filter(is_valid=True)
            .exists()
        )
