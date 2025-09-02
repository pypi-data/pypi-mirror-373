from contextlib import suppress
from datetime import date, timedelta
from typing import Iterable

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Exists, OuterRef, Q, QuerySet, Subquery
from django.db.models.constraints import UniqueConstraint
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from psycopg.types.range import DateRange
from slugify import slugify
from wbcore.contrib.ai.llm.decorators import llm
from wbcore.contrib.authentication.models import User
from wbcore.contrib.directory.models import EmployerEmployeeRelationship, Entry
from wbcore.contrib.directory.signals import deactivate_profile
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.models import WBModel
from wbcore.signals import pre_merge
from wbcore.utils.models import (
    ComplexToStringMixin,
    DeleteToDisableMixin,
)

from wbcrm.models.llm.analyze_relationship import analyze_relationship


class AccountDefaultQueryset(QuerySet):
    def filter_for_user(self, user: User, validity_date: date | None = None, strict: bool = False) -> QuerySet:
        """
        Filters related accounts based on the user's permissions and roles.

        Args:
            user (User): The user for whom related accounts need to be filtered.
            validity_date (date | None, optional): The validity date for role filtering. Defaults to None.
            strict (bool, optional): If True, filtering will be strict based on roles; otherwise, relaxed. Defaults to False.

        Returns:
            QuerySet: A queryset of related accounts filtered based on the user's permissions and roles.
        """
        if user.has_perm("wbcrm.administrate_account"):
            return self
        if not validity_date:
            validity_date = date.today()

        valid_roles = AccountRole.objects.filter_for_user(user, validity_date=validity_date, strict=strict).filter(
            is_currently_valid=True
        )
        if (user.profile.is_internal or user.is_superuser) and not strict:
            return self.filter(Q(id__in=valid_roles.values("account")) | Q(is_public=True))
        return self.annotate(
            has_direct_role=Exists(valid_roles.filter(account=OuterRef("id"))),
            has_descending_roles=Exists(
                valid_roles.filter(
                    account__tree_id=OuterRef("tree_id"),
                    account__lft__lte=OuterRef("lft"),
                    account__rght__gte=OuterRef("rght"),
                )
            ),
        ).filter((Q(is_public=True) & Q(has_descending_roles=True)) | Q(has_direct_role=True))


class AccountManager(models.Manager):
    def get_queryset(self) -> AccountDefaultQueryset:
        return AccountDefaultQueryset(self.model)

    def filter_for_user(self, user: User, validity_date: date | None = None, strict: bool = False) -> QuerySet:
        return self.get_queryset().filter_for_user(user, validity_date=validity_date, strict=strict)


class ActiveAccountManager(AccountManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class OpenAccountObjectManager(AccountManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Account.Status.OPEN, is_active=True)


@llm([analyze_relationship])
class Account(ComplexToStringMixin, DeleteToDisableMixin, WBModel, MPTTModel):
    tree_id: int

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        OPEN = "OPEN", _("Open")
        CLOSE = "CLOSE", _("Close")

    relationship_status = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Relationship Status"),
        help_text=_("The Relationship Status from 1 to 5. 1 being the cold and 5 being the hot."),
        blank=True,
        null=True,
    )
    relationship_summary = models.TextField(default="", blank=True)
    action_plan = models.TextField(default="", blank=True)

    reference_id = models.PositiveIntegerField(unique=True, blank=True)
    title = models.CharField(max_length=255, verbose_name="Title")
    status = FSMField(default=Status.OPEN, choices=Status.choices, verbose_name="Status")
    parent = TreeForeignKey(
        "wbcrm.Account",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent Account"),
    )
    is_terminal_account = models.BooleanField(
        default=False,
        verbose_name="Terminal Account",
        help_text="If true, sales or revenue can happen in this account",
    )
    is_public = models.BooleanField(
        default=True, verbose_name="Public", help_text="If True, all internal users can access this account"
    )
    owner = models.ForeignKey(
        "directory.Entry",
        related_name="accounts",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("Owner"),
    )

    @transition(
        status,
        Status.PENDING,
        Status.OPEN,
        permission=lambda account, user: account.can_administrate(user),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:account",),
                icon=WBIcon.APPROVE.icon,
                key="approve",
                label="Approve",
                action_label="Approve",
                description_fields="<p>Are you sure you want to open this account?</p>",
            )
        },
    )
    def approve(self, **kwargs):
        pass

    @transition(
        status,
        Status.PENDING,
        Status.CLOSE,
        permission=lambda account, user: account.can_administrate(user),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:account",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label="Deny",
                action_label="Deny",
                description_fields="<p>Are you sure you want to close this account?</p>",
            )
        },
    )
    def deny(self, **kwargs):
        pass

    @transition(
        status,
        Status.OPEN,
        Status.CLOSE,
        permission=lambda account, user: account.can_administrate(user),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:account",),
                icon=WBIcon.LOCK.icon,
                key="close",
                label="Close",
                action_label="Close",
                description_fields="<p>Are you sure you want to close this account?</p>",
            )
        },
    )
    def close(self, **kwargs):
        pass

    @transition(
        status,
        Status.CLOSE,
        Status.PENDING,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:account",),
                icon=WBIcon.LOCK.icon,
                key="reopen",
                label="Reopen",
                action_label="Reopen",
                description_fields="<p>Are you sure you want to reopen this account?</p>",
            )
        },
    )
    def reopen(self, **kwargs):
        pass

    def can_administrate(self, user: User):
        """Every superuser, valid manager and valid pm can lock a"""
        return user.has_perm("wbcrm.administrate_account")

    def compute_str(self) -> str:
        title = self.title or str(self.reference_id)
        if self.parent:
            title += f" ({self.parent.computed_str})"
        return title

    def merge(self, merged_account):
        if not merged_account.children.exists() and (
            merged_account.parent == self or merged_account.parent == self.parent
        ):  # we can merge only sibling accounts or child to parent
            with transaction.atomic():  # We want this to either succeed fully or fail
                for role in merged_account.roles.all():
                    try:
                        new_role = AccountRole.objects.get(entry=role.entry, account=self)
                        for validity in role.validity_set.all():
                            if not AccountRoleValidity.objects.filter(
                                role=new_role, timespan__overlap=validity.timespan
                            ).exists():
                                validity.role = new_role
                                validity.save()
                        for user in role.authorized_hidden_users.all():
                            new_role.authorized_hidden_users.add(user)
                        role.delete()
                    except AccountRole.DoesNotExist:
                        role.account = self
                        role.save()

                # Get the base
                pre_merge.send(
                    sender=Account, merged_object=merged_account, main_object=self
                )  # default signal dispatch for the Account class
                # We delete finally the merged account. All unlikage should have been done in the signal receivers function ( we refresh to be sure that no receiver modified the given object )
                self.refresh_from_db()
                merged_account.refresh_from_db()
                merged_account.delete(no_deletion=False)

                # copy fields

            # trigger save for post save logic (if any)
            self.save()

    def save(self, *args, **kwargs):
        if self.parent and not self.owner:
            self.owner = self.parent.owner
        if not self.reference_id:
            self.reference_id = Account.get_next_available_reference_id()
        # if not Account.objects.filter(parent=self).exists():
        #     self.is_terminal_account = True
        # else:
        #     self.is_terminal_account = False
        self.is_terminal_account = self.is_leaf_node()
        if not self.is_active:
            self.status = self.Status.CLOSE
        if self.status == self.Status.CLOSE:
            self.is_active = False
        super().save(*args, **kwargs)
        # self.children.update() TODO recompute str for all children
        # Account.objects.filter(id=self.id).update(computed_str=self.compute_str())

    def get_inherited_roles_for_account(self, include_self: bool = False) -> QuerySet:
        """
        Return account role from the parent accounts

        Args:
            include_self: MPTT argument

        Returns:
            The parent account roles
        """
        return AccountRole.objects.filter(account__in=self.get_ancestors(include_self=include_self))

    def can_see_account(self, user: User, validity_date: date | None = None) -> bool:
        """
        Checks if the user can see the account based on their permissions and roles.

        Args:
            user (User): The user for whom account visibility needs to be checked.
            validity_date (date | None, optional): The validity date for role filtering. Defaults to None.

        Returns:
            bool: True if the user can see the account, False otherwise.
        """
        if not validity_date:
            validity_date = date.today()
        return Account.objects.filter(id=self.id).filter_for_user(user, validity_date=validity_date).exists()

    @classmethod
    def get_next_available_reference_id(cls) -> int:
        if Account.objects.exists():
            reference_id = Account.all_objects.latest("reference_id").reference_id + 1
        else:
            reference_id = 1
        return reference_id

    @classmethod
    def annotate_root_account_info(cls, queryset: QuerySet) -> QuerySet:
        """
        Utility classmethod to annotate a queryset for the root account and its owner

        Args:
            queryset: Queryset to annotate

        Returns:
            A annotated queryset
        """
        return queryset.annotate(
            root_account=Subquery(
                Account.all_objects.filter(tree_id=OuterRef("account__tree_id"), level=0).values("id")[:1]
            ),
            root_account_repr=Subquery(
                Account.all_objects.filter(tree_id=OuterRef("account__tree_id"), level=0).values("computed_str")[:1]
            ),
            root_account_owner=Subquery(
                Account.all_objects.filter(tree_id=OuterRef("account__tree_id"), level=0).values("owner")[:1]
            ),
            root_account_owner_repr=Subquery(
                Account.all_objects.filter(tree_id=OuterRef("account__tree_id"), level=0).values(
                    "owner__computed_str"
                )[:1]
            ),
        )

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        permissions = [("administrate_account", "Administrate Account")]

    objects = ActiveAccountManager()
    all_objects = AccountManager()
    open_objects = OpenAccountObjectManager()
    tree_objects = TreeManager()

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcrm:account"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcrm:accountrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_accounts_for_customer(cls, entries: Entry | Iterable[Entry]) -> QuerySet:
        """
        Retrieves accounts associated with the given entry's ownership.

        Args:
            entries (Entry): The entry for which owned accounts are to be retrieved. Can be an iterable or an entry.

        Returns:
            QuerySet: A queryset of accounts owned by the provided entry.
        """
        if not isinstance(entries, Iterable):
            entries = [entries]

        # Get all root accounts owned by the entry
        root_accounts = cls.objects.filter(
            Q(owner__in=entries)
            | Q(
                owner__in=EmployerEmployeeRelationship.objects.filter(employee__id__in=[o.id for o in entries]).values(
                    "employer"
                )
            )
        )

        # Get root account and descendants account ids
        return cls.objects.annotate(
            is_direct_owner=Exists(root_accounts.filter(id=OuterRef("id"))),
            is_owner_of_descending_account=Exists(
                root_accounts.filter(tree_id=OuterRef("tree_id"), lft__lte=OuterRef("lft"), rght__gte=OuterRef("rght"))
            ),
        ).filter(Q(is_owner_of_descending_account=True) | Q(is_direct_owner=True))

    @classmethod
    def get_managed_accounts_for_entry(cls, entry: Entry) -> QuerySet:
        """
        Retrieves managed accounts associated with the given entry.

        Args:
            entry (Entry): The entry for which managed accounts are to be retrieved.

        Returns:
            QuerySet: A queryset of managed accounts associated with the provided entry.
        """
        roles = AccountRole.objects.filter(entry=entry)

        return cls.objects.annotate(
            has_direct_role=Exists(roles.filter(account=OuterRef("id"))),
            has_descending_roles=Exists(
                roles.filter(
                    account__tree_id=OuterRef("tree_id"),
                    account__lft__lte=OuterRef("lft"),
                    account__rght__gte=OuterRef("rght"),
                )
            ),
        ).filter((Q(is_public=True) & Q(has_descending_roles=True)) | Q(has_direct_role=True))


class AccountRoleType(models.Model):
    title = models.CharField(max_length=126, verbose_name="Title")
    key = models.CharField(max_length=126, unique=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = slugify(self.title)
        super().save(*args, **kwargs)

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcrm:accountroletyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"


class AccountRoleDefaultQueryset(QuerySet):
    def filter_for_user(self, user: User, validity_date: date | None = None, strict: bool = False) -> QuerySet:
        """
        Filters account roles related to the user based on permissions and roles.

        Args:
            user (User): The user for whom account roles need to be filtered.
            validity_date (date | None, optional): The validity date for role filtering. Defaults to None.
            strict (bool, optional): If True, filtering will be strict based on roles; otherwise, relaxed. Defaults to False.

        Returns:
            QuerySet: A queryset of account roles related to the user, filtered based on permissions and roles.
        """
        if not validity_date:
            validity_date = date.today()
        qs = self.annotate(is_currently_valid=AccountRoleValidity.get_role_validity_subquery(validity_date))
        if user.has_perm("wbcrm.administrate_account"):
            return qs
        if user.profile.is_internal and not strict:
            qs = qs.filter(
                Q(entry_id=user.profile.id)
                | (Q(account__is_public=True) & Q(is_hidden=False))
                | (Q(is_hidden=True) & Q(authorized_hidden_users=user))
            )
        else:
            qs = qs.filter(entry_id=user.profile.id)
        return qs


class AccountRoleManager(models.Manager):
    # Necessary because otherwise pyright cannot find method

    def get_queryset(self) -> AccountRoleDefaultQueryset:
        return AccountRoleDefaultQueryset(self.model)

    def filter_for_user(self, user: User, validity_date: date | None = None, strict: bool = False) -> QuerySet:
        return self.get_queryset().filter_for_user(user, validity_date=validity_date, strict=strict)


class AccountRole(ComplexToStringMixin, models.Model):
    """Model for Account Roles"""

    class Meta:
        verbose_name = "Account Role"
        verbose_name_plural = "Account Roles"
        constraints = [UniqueConstraint(fields=["account", "entry"], name="unique_account_entry_relationship")]

    role_type = models.ForeignKey(
        "wbcrm.AccountRoleType", related_name="roles", on_delete=models.PROTECT, verbose_name="Role Type"
    )
    entry = models.ForeignKey(
        "directory.Entry", related_name="account_roles", on_delete=models.PROTECT, verbose_name="Entry"
    )
    account = models.ForeignKey(
        "wbcrm.Account", related_name="roles", on_delete=models.CASCADE, verbose_name="Account"
    )

    is_hidden = models.BooleanField(
        default=False,
        verbose_name="Hidden",
        help_text="If True, this role is hidden and can be seen only by authorized people",
    )
    authorized_hidden_users = models.ManyToManyField(
        "authentication.User",
        related_name="authorized_hidden_roles",
        blank=True,
        verbose_name=_("authorized Hidden Users"),
        help_text=_("List of users that are allowed to see this hidden account role"),
    )

    weighting = models.FloatField(default=1, verbose_name="Weight")

    objects = AccountRoleManager()

    def compute_str(self) -> str:
        rel = f"Role {self.role_type} for {self.entry} on {self.account}"
        if self.is_hidden:
            rel += " (Hidden)"
        return rel

    def save(self, *args, **kwargs):
        # if the role is hidden and the account is public, we ensure it becomes private so that the hidden rule is respected
        if self.is_hidden and self.account.is_public:
            self.account.is_public = False
            self.account.save()

        super().save(*args, **kwargs)

    def deactivate(self, deactivation_date: date | None = None):
        """
        Utility function to disable a account role at a given time

        Args:
            deactivation_date: The time at which the role will be deactivated. Default to today
        """
        if not deactivation_date:
            deactivation_date = date.today()
        with suppress(AccountRoleValidity.DoesNotExist):
            val = AccountRoleValidity.objects.get(
                role=self,
                timespan__startswith__lte=deactivation_date,
                timespan__endswith__gt=deactivation_date,
            )
            val.timespan = DateRange(val.timespan.lower, deactivation_date)
            val.save()


class AccountRoleValidity(models.Model):
    role = models.ForeignKey(
        "wbcrm.AccountRole", related_name="validity_set", on_delete=models.CASCADE, verbose_name="Account Role"
    )
    timespan = DateRangeField(verbose_name="Timespan")

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_roles",
                expressions=[
                    ("timespan", RangeOperators.OVERLAPS),
                    ("role", RangeOperators.EQUAL),
                ],
            ),
        ]

    def __str__(self):
        return f"[{self.timespan.lower} - {self.timespan.upper}["  # type: ignore

    @classmethod
    def get_role_validity_subquery(cls, validity_date: date, role_label_key: str = "pk") -> Subquery:
        """
        Return a subquery that will define wether a account role is valid
        Args:
            validity_date: The validity date
            role_label_key: The related name for the account role foreign key

        Returns:
            A subquery expression of type boolean
        """
        return Exists(
            AccountRoleValidity.objects.filter(
                role=OuterRef(role_label_key),
                timespan__startswith__lte=validity_date,
                timespan__endswith__gt=validity_date,
            )
        )


@receiver(deactivate_profile)
def handle_user_deactivation(sender, instance, substitute_profile=None, **kwargs):
    deactivation_date = date.today() - timedelta(days=1)
    for profile_role in AccountRole.objects.filter(entry_id=instance.id):
        for validity in profile_role.validity_set.all():
            if validity.timespan.upper >= deactivation_date:  # type: ignore
                validity.timespan = DateRange(
                    validity.timespan.lower,
                    max([deactivation_date, validity.timespan.lower]),  # type: ignore
                )
                validity.save()
                if substitute_profile and validity.timespan.lower <= deactivation_date:  # type: ignore
                    substitute_role, created = AccountRole.objects.get_or_create(
                        account=profile_role.account,
                        entry_id=substitute_profile.id,
                        defaults={"role_type": profile_role.role_type},
                    )
                    if created:
                        v = substitute_role.validity_set.filter(
                            timespan__startswith__lt=deactivation_date,
                            timespan__endswith__gt=deactivation_date,
                        ).first()
                        v.timespan = DateRange(deactivation_date, date.max)  # type: ignore
                        v.save()


@receiver(post_save, sender="wbcrm.Account")
def post_account_creation(sender, instance, created, **kwargs):
    # disabling parent account disable children as well
    if not instance.is_active:
        instance.get_descendants().update(is_active=False)
    # check that if an account is private, all its children are private as well
    if not instance.is_public:
        instance.get_descendants().update(is_public=False)
    # if an new account is created and it's a leaf node, we assume it's a terminal account. Can be changed afterwards
    if created:
        # we create a role for the owner by default upon creation
        if instance.owner:
            owner_role_type = AccountRoleType.objects.get_or_create(key="customer", defaults={"title": "Customer"})[0]
            AccountRole.objects.get_or_create(
                account=instance, entry=instance.owner, defaults={"role_type": owner_role_type}
            )
        if instance.is_terminal_account and instance.parent:
            instance.get_ancestors().update(is_terminal_account=False)


@receiver(post_delete, sender="wbcrm.Account")
def post_delete_account(sender, instance, **kwargs):
    if (parent := instance.parent) and not parent.children.exists():
        parent.is_terminal_account = True
        parent.save()


@receiver(post_save, sender="wbcrm.AccountRole")
def post_account_role_creation(sender, instance, created, **kwargs):
    # if an new account is created and it's a leaf node, we assume it's a terminal account. Can be changed afterwards
    if created:
        AccountRoleValidity.objects.create(role=instance, timespan=DateRange(date.min, date.max))  # type: ignore
