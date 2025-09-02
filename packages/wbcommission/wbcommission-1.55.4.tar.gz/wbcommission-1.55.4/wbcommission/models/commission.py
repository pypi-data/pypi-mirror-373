import math
from contextlib import suppress
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Generator, Optional

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import (
    DateRangeField,
    DecimalRangeField,
    RangeOperators,
)
from django.db import models
from django.db.models import Exists, OuterRef, Q, QuerySet, Sum, UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from ordered_model.models import OrderedModel, OrderedModelManager, OrderedModelQuerySet
from psycopg.types.range import DateRange, NumericRange
from tqdm import tqdm
from wbcore.contrib.directory.models import Entry
from wbcore.models import WBModel
from wbcore.signals import pre_merge
from wbcore.utils.models import ComplexToStringMixin
from wbcrm.models.accounts import (
    Account,
    AccountRole,
    AccountRoleType,
    AccountRoleValidity,
)
from wbportfolio.models import PortfolioRole

from .account_service import AccountRebateManager

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

from wbcore.contrib.authentication.models import User


class CommissionDefaultQueryset(OrderedModelQuerySet):
    def filter_for_user(self, user: User, validity_date: date | None = None) -> QuerySet:
        """
        Protect the chained queryset and filter the commission this user cannot see based on the following rules:

        * not-hidden commission: Ever user with a direct valid account role on the commission's account
        * hidden: only user with a direct commission role on that commission line
        * in any case, all user with direct commission role or recipient of the commission
        """
        if not validity_date:
            validity_date = date.today()
        if user.has_perm("wbcommission.administrate_commission"):
            return self
        valid_accounts = Account.objects.filter_for_user(user, validity_date=validity_date, strict=True)
        return self.annotate(
            can_see_account=Exists(valid_accounts.filter(id=OuterRef("account"))),
            has_direct_commission_role=Exists(
                CommissionRole.objects.filter(person=user.profile, commission=OuterRef("pk"))
            ),
        ).filter(
            (Q(is_hidden=False) & Q(can_see_account=True))
            | Q(has_direct_commission_role=True)
            | Q(crm_recipient=user.profile.entry_ptr)
        )


class CommissionManager(OrderedModelManager):
    def get_queryset(self) -> CommissionDefaultQueryset:
        return CommissionDefaultQueryset(self.model)

    def filter_for_user(self, user: User, validity_date: date | None = None) -> QuerySet:
        return self.get_queryset().filter_for_user(user, validity_date=validity_date)


class CommissionType(WBModel):
    id: Optional[int]
    name = models.CharField(max_length=256, verbose_name="Name")
    key = models.CharField(max_length=256, unique=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.name.lower()
        super().save(*args, **kwargs)

    def get_valid_commissions(
        self,
        terminal_account: "Account",
        compute_date: date,
        content_object: models.Model,
        root_account_total_holding: Decimal,
    ) -> Generator[tuple["Commission", Decimal], None, None]:
        """
        Retrieve valid commissions for the given terminal account and parameters.

        This function filters and retrieves valid commissions for a specific terminal account
        based on the provided parameters. It iterates through the applicable commissions,
        validates them, and yields tuples of valid commissions along with their calculated percentages.

        Args:
            terminal_account (Account): The terminal account for which to retrieve valid commissions.
            compute_date (date): The date for which to compute the rebates.
            content_object (models.Model): The content object for which to compute rebates.
            root_account_total_holding (Decimal): The total holding of the root account.

        Yields:
            tuple: A tuple containing a valid Commission instance and its corresponding actual percentage.
        """

        applicable_commissions = Commission.objects.filter(
            account__in=terminal_account.get_ancestors(include_self=True).filter(is_active=True), commission_type=self
        ).order_by("order")
        available_percent = Decimal(1)
        for order in applicable_commissions.values("order").distinct("order"):
            # in case there is duplicates, we get the lower commissison in the account tree
            commission = applicable_commissions.filter(order=order["order"]).order_by("-account__level").first()
            if commission.is_valid(compute_date, content_object, root_account_total_holding):
                actual_percent = (
                    available_percent * commission.validated_percent
                    if commission.validated_net_commission
                    else commission.validated_percent
                )
                actual_percent = max(min(available_percent, actual_percent), Decimal(0))
                available_percent -= actual_percent
                if actual_percent > 0:
                    yield commission, actual_percent

    def compute_rebates(
        self, root_account: "Account", verbose: bool = False, **iterator_kwargs
    ) -> Generator[tuple["Account", date, "Commission", models.Model, "Entry", Decimal], None, None]:
        """
        Generate rebate information for terminal accounts based on given parameters.

        This method calculates and yields rebate information for terminal accounts based on the provided
        root_account, and iterator_kwargs.

        It iterates through active terminal accounts,
        computes rebates, and returns the results as a generator of tuples containing terminal account,
        compute date, commission, content object, recipient entry, and rebate amount.

        Args:
            root_account (Account): The root account for rebate calculations.
            verbose (bool): debugging option. Default to false.
            **iterator_kwargs: Additional keyword arguments for filtering.

        Yields:
            Generator[tuple]: A generator yielding rebate information tuples with components:
                - Terminal account (Account)
                - Compute date (date)
                - Commission (Commission)
                - Content object (models.Model)
                - Recipient entry (Entry)
                - Rebate amount (Decimal)

        """
        rebate_manager = AccountRebateManager(
            root_account, self.key
        )  # This will be loaded dynamically in a future iteration
        rebate_manager.initialize()
        # Iterate through active terminal accounts
        iterator = rebate_manager.get_iterator(**iterator_kwargs)
        if verbose:
            iterator = list(iterator)
            iterator = tqdm(iterator, total=len(iterator))

        for terminal_account, content_object, compute_date in iterator:
            root_account_total_holding = rebate_manager.get_root_account_total_holding(compute_date)
            terminal_account_holding_ratio = rebate_manager.get_terminal_account_holding_ratio(
                terminal_account,
                content_object,
                compute_date,
            )

            # Calculate rebates for the current terminal account
            if terminal_account_holding_ratio:
                for commission, actual_percent in self.get_valid_commissions(
                    terminal_account, compute_date, content_object, root_account_total_holding
                ):
                    # total commission pool for the given object that day
                    commission_pool = rebate_manager.get_commission_pool(content_object, compute_date)
                    commission_pool_sign = math.copysign(
                        1, commission_pool
                    )  # in case the pool is negative, the gain is a credit
                    commission_pool = abs(commission_pool)
                    account_gain = (
                        terminal_account_holding_ratio * commission_pool
                    )  # total account gain that account can get from the total commission pool for that day
                    if account_gain == 0:
                        continue

                    leftover_fees = account_gain

                    # Iterate through recipients and calculate rebates for each
                    for recipient, weighting in commission.get_recipients(
                        terminal_account, content_object, compute_date
                    ):
                        recipient_percent = actual_percent * weighting
                        recipient_fees = max(min(leftover_fees, account_gain * recipient_percent), Decimal(0))
                        leftover_fees -= recipient_fees

                        rebate_gain = Decimal(
                            math.copysign(recipient_fees, commission_pool_sign)
                        )  # If fees are negative, then we need to return the negative of the recipient fees

                        # Yield rebate information
                        yield (
                            terminal_account,
                            compute_date,
                            commission,
                            content_object,
                            recipient,
                            rebate_gain,
                            {
                                "terminal_account_holding_ratio": terminal_account_holding_ratio,
                                "root_account_total_holding": root_account_total_holding,
                                "commission_percent": actual_percent,
                                "commission_pool": commission_pool,
                                "recipient_percent": recipient_percent,
                            },
                        )

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcommission:commissiontype"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcommission:commissiontyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class Commission(OrderedModel, WBModel):
    """Holds all the information on how fees are distributed"""

    id: Optional[int]
    account = models.ForeignKey[Account](
        to="wbcrm.Account",
        related_name="account_commissions",
        on_delete=models.CASCADE,
        verbose_name="Account",
    )
    crm_recipient = models.ForeignKey[Entry](
        to="directory.Entry",
        related_name="recipient_commissions",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Recipient",
    )
    portfolio_role_recipient = models.CharField(
        max_length=32, choices=PortfolioRole.RoleType.choices, null=True, blank=True, verbose_name="Recipient Role"
    )
    account_role_type_recipient = models.ForeignKey[AccountRoleType](
        to="wbcrm.AccountRoleType",
        related_name="recipient_commissions",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Account Role Type Recipient",
    )

    net_commission = models.BooleanField(default=True, verbose_name="Net Commission Rule")
    commission_type = models.ForeignKey[CommissionType](
        "wbcommission.CommissionType",
        on_delete=models.PROTECT,
        related_name="commissions",
        verbose_name="Commission Type",
    )
    is_hidden = models.BooleanField(
        default=True,
        verbose_name="Hidden Commission Rule",
        help_text="If False, this commission rule can be seen by anoyone that can access the related account. Otherwise, only an explicit role will grant access",
    )
    exclusion_rule_account_role_type = models.ForeignKey[AccountRoleType](  # TODO think if this is the best approach
        to="wbcrm.AccountRoleType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Account Role to decide with exclusion rule applies",
    )
    objects = CommissionManager()

    if TYPE_CHECKING:
        rules = RelatedManager["CommissionRule"]()

    class Meta(OrderedModel.Meta):
        verbose_name = "Commission"
        verbose_name_plural = "Commissions"
        permissions = (("administrate_commission", "Can administrate Commission"),)
        constraints = [
            UniqueConstraint(
                name="unique_crm_recipient_account",
                fields=["commission_type", "account", "crm_recipient"],
                condition=Q(crm_recipient__isnull=False),
            ),
            UniqueConstraint(
                name="unique_portfolio_role_recipient_account",
                fields=["commission_type", "account", "portfolio_role_recipient"],
                condition=Q(portfolio_role_recipient__isnull=False),
            ),
            UniqueConstraint(
                name="unique_account_role_type_recipient_account",
                fields=["commission_type", "account", "account_role_type_recipient"],
                condition=Q(account_role_type_recipient__isnull=False),
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        crm_recipient__isnull=False,
                        portfolio_role_recipient__isnull=True,
                        account_role_type_recipient__isnull=True,
                    )
                    | Q(
                        crm_recipient__isnull=True,
                        portfolio_role_recipient__isnull=False,
                        account_role_type_recipient__isnull=True,
                    )
                    | Q(
                        crm_recipient__isnull=True,
                        portfolio_role_recipient__isnull=True,
                        account_role_type_recipient__isnull=False,
                    )
                ),
                name="Only one recipient type set",
            ),
        ]

    @property
    def recipient_repr(self) -> str:
        if self.crm_recipient:
            return f"Profile {self.crm_recipient.computed_str}"
        elif self.portfolio_role_recipient:
            return f"Portfolio Role: {PortfolioRole.RoleType[self.portfolio_role_recipient].label}"
        else:
            return f"Account Role Type: {self.account_role_type_recipient.title}"

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"Net: {self.net_commission} - {self.account.title} - {self.order} - {self.commission_type} - {self.recipient_repr} (id: {self.id})"

    @property
    def validated_percent(self) -> Decimal:
        if not hasattr(self, "_validated_percent"):
            raise AssertionError("You must call `.is_valid()` before accessing `.validated_percent`.")
        return self._validated_percent

    @property
    def validated_net_commission(self) -> bool:
        if not hasattr(self, "_validated_net_commission"):
            raise AssertionError("You must call `.is_valid()` before accessing `.validated_net_commission`.")
        return self._validated_net_commission

    def is_valid(self, validity_date: date, product: models.Model, asset_under_management: Decimal) -> bool:
        """
        Check if the commission rule is valid for given parameters.

        This method determines if the commission rule is valid based on the provided parameters.
        It checks the validity date, the product, and the asset under management against the rules
        associated with the commission. If a valid rule is found, the method sets the validated
        percentage and net commission and handles any overriding exclusion rules.

        Args:
            validity_date (date): The date for which the validity is checked.
            product (models.Model): The product associated with the commission rule.
            asset_under_management (Decimal): The asset under management for the account.

        Returns:
            bool: True if the commission rule is valid, False otherwise.
        """
        try:
            valid_rule = self.rules.get(
                Q(timespan__startswith__lte=validity_date)
                & Q(timespan__endswith__gt=validity_date)
                & Q(assets_under_management_range__startswith__lte=asset_under_management)
                & (
                    Q(assets_under_management_range__endswith__gt=asset_under_management)
                    | Q(assets_under_management_range__endswith__isnull=True)
                )
                & (Q(percent__gt=0) | (Q(percent=0) & Q(consider_zero_percent_for_exclusion=True)))
            )
            self._validated_percent = valid_rule.percent
            self._validated_net_commission = self.net_commission
            with suppress(CommissionExclusionRule.DoesNotExist):
                overriding_rule = CommissionExclusionRule.objects.get(
                    timespan__startswith__lte=validity_date,
                    timespan__endswith__gt=validity_date,
                    product=product,
                    commission_type=self.commission_type,
                    account_role_type=self.exclusion_rule_account_role_type,
                )
                self._validated_percent = overriding_rule.overriding_percent
                self._validated_net_commission = overriding_rule.get_net_or_gross(self.net_commission)
            return True
        except CommissionRule.DoesNotExist:
            return False

    def get_recipients(
        self, account: "Account", product: models.Model, val_date: date
    ) -> Generator[tuple["Entry", Decimal], None, None]:
        """
        This function generates recipients and their respective weightings for distributing
        commissions based on the provided account, product, and validation date.

        Args:
            account (Account): The account for which recipients are being generated. Only used for account role type typed commission
            product (models.Model): The product model for which recipients are being generated. Only used for portfolio role typed commission
            val_date (date): The date for which the recipients are being generated. Used to determine the role validity

        Yields:
            tuple[Entry, Decimal]: A tuple containing a recipient entry and its associated weighting.

        Note:
            The generated recipients and weightings depend on different conditions, including CRM recipients,
            account role type recipients, and portfolio role recipients.

        Raises:
            AccountRoleValidity.DoesNotExist: If no validity data is available for any account role,
                                             the exception will be caught, and recipients will not be generated.
            KeyError: If no recipient data is available for any condition,
                      a KeyError will be caught, and no recipients will be generated.
        """
        if self.crm_recipient:
            yield self.crm_recipient, Decimal(1.0)
        elif self.account_role_type_recipient:
            account_roles = AccountRole.objects.annotate(
                is_valid=AccountRoleValidity.get_role_validity_subquery(val_date)
            ).filter(
                is_valid=True,
                account__in=account.get_ancestors(include_self=True).filter(level__gte=self.account.level),
                role_type=self.account_role_type_recipient,
            )
            total_weighting = Decimal(account_roles.aggregate(s=Sum("weighting"))["s"] or 0)
            for account_role in account_roles:
                yield (
                    account_role.entry,
                    Decimal(account_role.weighting) / total_weighting if total_weighting else Decimal(0),
                )
        else:
            role_recipients = PortfolioRole.objects.exclude(
                weighting=0
            ).filter(
                (Q(role_type=self.portfolio_role_recipient) & (Q(instrument=product) | Q(instrument__isnull=True)))
                & (Q(start__lte=val_date) | Q(start__isnull=True))
                & (
                    Q(end__gte=val_date) | Q(end__isnull=True)
                )  # This breaks the date range default upper range exclusion, will need to change if we ever move to a data range field
            )
            total_weighting = Decimal(role_recipients.aggregate(s=Sum("weighting"))["s"] or 0)
            for portfolio_role in role_recipients:
                yield (
                    portfolio_role.person.entry_ptr,
                    Decimal(Decimal(portfolio_role.weighting) / total_weighting) if total_weighting else Decimal(0),
                )

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcommission:commission"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcommission:commissionrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{id}}"


class CommissionExclusionRule(models.Model):
    class NetOrGrossCommissionOverridingType(models.TextChoices):
        NET = "NET", "Net"
        GROSS = "GROSS", "Gross"
        DEFAULT = "DEFAULT", "Default"

    id: Optional[int]
    product = models.ForeignKey(
        to="wbportfolio.Product",
        on_delete=models.CASCADE,
        verbose_name="Product",
    )
    timespan = DateRangeField(verbose_name="Timespan")
    commission_type = models.ForeignKey(
        CommissionType,
        on_delete=models.PROTECT,
        related_name="commission_exclusion_rules",
        verbose_name="Commission Type",
    )
    account_role_type = models.ForeignKey(
        to="wbcrm.AccountRoleType",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Account Role Type Recipient",
    )
    overriding_percent = models.DecimalField(verbose_name="Overriding Percent", max_digits=4, decimal_places=3)
    overriding_net_or_gross_commission = models.CharField(
        default=NetOrGrossCommissionOverridingType.DEFAULT,
        choices=NetOrGrossCommissionOverridingType.choices,
        max_length=16,
        verbose_name="Overriding Net or Gross Commission Rule",
    )

    def save(self, *args, **kwargs):
        if not self.timespan:
            self.timespan = DateRange(date.min, date.max)  # type: ignore
        super().save(*args, **kwargs)

    def get_net_or_gross(self, net_commission: bool) -> bool:
        """
        Determine whether to use net or gross commission based on overriding settings.

        This function determines whether to use net or gross commission based on the
        provided `net_commission` parameter and the overriding settings.

        Args:
            net_commission (bool): The original commission type, True for net commission, False for gross commission.

        Returns:
            bool: The determined commission type after considering the overriding settings.
        """
        return {
            self.NetOrGrossCommissionOverridingType.DEFAULT.name: net_commission,
            self.NetOrGrossCommissionOverridingType.GROSS.name: False,
        }.get(self.overriding_net_or_gross_commission, True)

    class Meta:
        verbose_name = "Commission Exclusion Rule"
        verbose_name_plural = "Commissions Exclusion Rules"
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_exclusion_rules",
                expressions=[
                    ("timespan", RangeOperators.OVERLAPS),
                    ("product", RangeOperators.EQUAL),
                    ("commission_type", RangeOperators.EQUAL),
                    ("account_role_type", RangeOperators.EQUAL),
                ],
            ),
        ]


class CommissionRule(ComplexToStringMixin, WBModel):
    id: Optional[int]
    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, related_name="rules", verbose_name="Commission Line"
    )
    timespan = DateRangeField(verbose_name="Timespan")
    assets_under_management_range = DecimalRangeField(verbose_name="AUM Range")
    percent = models.DecimalField(verbose_name="Percent", default=Decimal(0), max_digits=4, decimal_places=3)
    consider_zero_percent_for_exclusion = models.BooleanField(
        default=False,
        verbose_name="Consider 0 percent for exclusion",
        help_text="If true, the commission rule with percent 0 (initially consider disabled), will be considered for exclusion rule matching",
    )

    def save(self, *args, **kwargs):
        if not self.timespan:
            self.timespan = DateRange(date.min, date.max)  # type: ignore
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_rules",
                expressions=[
                    ("timespan", RangeOperators.OVERLAPS),
                    ("assets_under_management_range", RangeOperators.OVERLAPS),
                    ("commission", RangeOperators.EQUAL),
                ],
            ),
        ]

    def compute_str(self) -> str:
        return f"{self.commission} - {self.percent:.2%}: date range = [{self.timespan.lower} - {self.timespan.upper}[, aum range=[{self.assets_under_management_range.lower} - {self.assets_under_management_range.upper}["  # type: ignore

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcommission:commissionrule"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcommission:commissionrulerepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"


class CommissionRole(ComplexToStringMixin, WBModel):
    class Meta:
        verbose_name = "Commission Role"
        verbose_name_plural = "Commission Roles"

    def compute_str(self) -> str:
        return f"{self.person} -> {self.commission}"

    id: Optional[int]
    person = models.ForeignKey(
        "directory.Person", related_name="rebates_account_roles", on_delete=models.PROTECT, verbose_name="Person"
    )
    commission = models.ForeignKey(
        Commission, related_name="roles", on_delete=models.CASCADE, verbose_name="Commission Line"
    )

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcommission:commissionrole"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcommission:commissionrolerepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"


@receiver(post_save, sender="wbcommission.Commission")
def post_commission_creation(sender, instance, created, **kwargs):
    # if a new commission line is created, we create a general rule
    if created:
        CommissionRule.objects.create(
            commission=instance,
            timespan=DateRange(date.min, date.max),  # type: ignore
            assets_under_management_range=NumericRange(0, None),  # type: ignore
        )


@receiver(pre_merge, sender="wbcrm.Account")
def handle_pre_merge_account_for_commission(
    sender: models.Model, merged_object: Account, main_object: Account, **kwargs
):
    """
    Loop over all commission lines assigned to the account to be merged and reassign them to the remaining account. Handle also the commission roles and rules.
    """
    for commission in merged_object.account_commissions.all():
        defaults = {
            "order": commission.order,
            "net_commission": commission.net_commission,
            "is_hidden": commission.is_hidden,
            "exclusion_rule_account_role_type": commission.exclusion_rule_account_role_type,
        }
        if commission.crm_recipient:
            new_commission, created = Commission.objects.get_or_create(
                crm_recipient=commission.crm_recipient,
                account=main_object,
                commission_type=commission.commission_type,
                defaults=defaults,
            )
        elif commission.portfolio_role_recipient:
            new_commission, created = Commission.objects.get_or_create(
                portfolio_role_recipient=commission.portfolio_role_recipient,
                account=main_object,
                commission_type=commission.commission_type,
                defaults=defaults,
            )
        else:
            new_commission, created = Commission.objects.get_or_create(
                account_role_type_recipient=commission.account_role_type_recipient,
                account=main_object,
                commission_type=commission.commission_type,
                defaults=defaults,
            )
        for role in commission.roles.all():
            if not new_commission.roles.filter(person=role.person).exists():
                role.commission = new_commission
                role.save()
        if created:
            new_commission.rules.all().delete()
        for rule in commission.rules.all():
            if not new_commission.rules.filter(
                timespan__overlap=rule.timespan,
                assets_under_management_range__overlap=rule.assets_under_management_range,
            ).exists():
                rule.commission = new_commission
                rule.save()
        commission.rebates.update(commission=new_commission)
        commission.delete()
