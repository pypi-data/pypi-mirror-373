from datetime import date as date_lib
from decimal import Decimal
from typing import Any, Optional

from celery import shared_task
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Exists, OuterRef, QuerySet
from django.dispatch import receiver
from wbcore.contrib.authentication.models import User
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.signals import pre_merge
from wbcore.utils.enum import ChoiceEnum
from wbcrm.models.accounts import Account

from .commission import Commission, CommissionType


class BookingEntryCalculatedValueMixin:
    @classmethod
    def get_accounting_sum(cls, related_data: dict[str, str], queryset: QuerySet) -> float:
        raise NotImplementedError

    def update_calculated_value_of_booking_entry(self):
        raise NotImplementedError


class RebateGroupbyChoice(ChoiceEnum):
    ROOT_ACCOUNT = "Root Account"
    ACCOUNT = "Account"
    ROOT_ACCOUNT_OWNER = "Root Account Owner"
    ACCOUNT_OWNER = "Account Owner"
    PRODUCT = "Product"
    PRODUCT_GROUP = "ProductGroup"
    CLASSIFICATION = "Classification"
    RECIPIENT = "Recipient"

    @classmethod
    @property
    def map(cls) -> dict[str, dict[str, Any]]:
        """
        Field map used in the groupby filter in the rebate table view
        """
        return {
            "ROOT_ACCOUNT": {
                "pk": "root_account",
                "title_key": "root_account_repr",
                "search_fields": ["root_account_repr"],
            },
            "ACCOUNT": {
                "pk": "account",
                "title_key": "account__computed_str",
                "search_fields": ["account__computed_str"],
            },
            "ROOT_ACCOUNT_OWNER": {
                "pk": "root_account_owner",
                "title_key": "root_account_owner_repr",
                "search_fields": ["root_account_owner_repr"],
            },
            "ACCOUNT_OWNER": {
                "pk": "account__owner",
                "title_key": "account__owner__computed_str",
                "search_fields": ["account__owner__computed_str"],
            },
            "PRODUCT": {
                "pk": "product",
                "title_key": "product__computed_str",
                "search_fields": ["product__computed_str"],
            },
            "PRODUCT_GROUP": {
                "pk": "product__parent",
                "title_key": "product__parent__name",
                "search_fields": ["product__parent__name"],
            },
            "CLASSIFICATION": {
                "pk": "classification_id",
                "title_key": "classification_title",
                "search_fields": ["classification_title"],
            },
            "RECIPIENT": {
                "pk": "recipient__id",
                "title_key": "recipient__computed_str",
                "search_fields": ["recipient__computed_str"],
            },
        }


class RebateDefaultQueryset(QuerySet):
    def filter_for_user(self, user: User, validity_date: date_lib | None = None) -> QuerySet:
        """
        Protect the chained queryset and filter the rebates that this user cannot see based on the following rules:

        * not-hidden commission: Ever user with a direct valid account role on the commission's account
        * hidden: only user with a direct commission role on that commission line
        * in any case, all user with direct commission role
        """
        if not validity_date:
            validity_date = date_lib.today()
        if user.has_perm("wbcommission.administrate_commission"):
            return self
        allowed_commission_lines = Commission.objects.filter_for_user(user, validity_date=validity_date)
        return self.annotate(
            can_see_commission=Exists(allowed_commission_lines.filter(id=OuterRef("commission"))),
        ).filter(can_see_commission=True)


class RebateManager(models.Manager):
    def get_queryset(self) -> RebateDefaultQueryset:
        return RebateDefaultQueryset(self.model)

    def filter_for_user(self, user: User, validity_date: date_lib | None = None) -> QuerySet:
        return self.get_queryset().filter_for_user(user, validity_date=validity_date)


class Rebate(BookingEntryCalculatedValueMixin, models.Model):
    """The fees that get rebated to a recipient"""

    int: Optional[int]
    date = models.DateField(verbose_name="Date")
    account = models.ForeignKey(
        "wbcrm.Account",
        related_name="rebates",
        on_delete=models.CASCADE,
        verbose_name="Account",
        limit_choices_to=models.Q(("is_terminal_account", True)),
    )
    product = models.ForeignKey(
        "wbportfolio.Product", related_name="rebates", on_delete=models.CASCADE, verbose_name="Product"
    )
    recipient = models.ForeignKey(
        "directory.Entry", related_name="recipient_rebates", on_delete=models.PROTECT, verbose_name="Recipient"
    )
    commission_type = models.ForeignKey(
        "wbcommission.CommissionType",
        on_delete=models.PROTECT,
        related_name="rebates",
        verbose_name="Commission Type",
    )

    commission = models.ForeignKey(
        "wbcommission.Commission",
        related_name="rebates",
        on_delete=models.PROTECT,
        verbose_name="Commission Line",
    )

    value = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal(0.0), verbose_name="Value")

    audit_log = models.JSONField(default=dict, verbose_name="Audit Log", encoder=DjangoJSONEncoder)
    objects = RebateManager()

    class Meta:
        verbose_name = "Rebate"
        verbose_name_plural = "Rebates"
        unique_together = ("date", "recipient", "account", "product", "commission_type")
        index_together = [
            # ("date", "recipient", "product"),
            ("commission_type", "date", "recipient", "product", "account"),
            #             ("date", "recipient", "product", "commission"),
        ]
        notification_types = [
            create_notification_type(
                "wbcommission.rebate.computation_done",
                "Rebate Computation Done",
                "Sends a notification to notify rebate computation requester that the calculation is done",
                True,
                True,
                False,
            ),
        ]

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.date:%d.%m.%Y}: {self.recipient.computed_str} {self.account.title}"

    @classmethod
    def manage_rebate(
        cls,
        main_account: Account,
        prune_existing: bool = False,
        start_date: date_lib | None = None,
        only_content_object_ids: list[int] | None = None,
        **filter_kwargs,
    ):
        """
        Utility method to generate rebate for all commission types for the given root account.

        This method get the rebate information from the commission type's rebate manager and decide wether to create a new rebate or update an existing one

        Args:
            main_account: root account to generate rebates from
            prune_existing: If true, will delete all existing rebates for that account and its children. Default to False. Note: For optimization, the rebate manager will yield only valid rebate information and thus, existing obselete rebate might never be overidden with a zero value.
            **filter_kwargs: these key-word arguments are passed down the rebate manager for as keyword argument for the iterator function

        """
        if prune_existing:
            rebates_to_pruned = cls.objects.filter(account__in=main_account.get_descendants(include_self=True))
            if only_content_object_ids:
                rebates_to_pruned = rebates_to_pruned.filter(product__in=only_content_object_ids)
            if start_date:
                rebates_to_pruned = rebates_to_pruned.filter(date__gte=start_date)
            rebates_to_pruned.delete()
        updated_objs = []
        created_objs = []
        for commission_type in CommissionType.objects.all():
            for (
                terminal_account,
                compute_date,
                commission,
                content_object,
                recipient,
                recipient_fees,
                audit_log,
            ) in commission_type.compute_rebates(
                main_account, start_date=start_date, only_content_object_ids=only_content_object_ids, **filter_kwargs
            ):
                try:
                    rebate = Rebate.objects.get(
                        date=compute_date,
                        recipient=recipient,
                        account=terminal_account,
                        product=content_object,
                        commission_type=commission_type,
                    )
                    rebate.value = recipient_fees
                    rebate.commission = commission
                    rebate.audit_log = audit_log
                    updated_objs.append(rebate)
                except cls.DoesNotExist:
                    rebate = Rebate(
                        date=compute_date,
                        recipient=recipient,
                        account=terminal_account,
                        product=content_object,
                        commission_type=commission_type,
                        commission=commission,
                        value=recipient_fees,
                        audit_log=audit_log,
                    )
                    created_objs.append(rebate)

        cls.objects.bulk_update(updated_objs, ["value", "commission"], batch_size=10000)
        cls.objects.bulk_create(created_objs, batch_size=10000, ignore_conflicts=True)

    @classmethod
    def get_accounting_sum(cls, related_data: dict[str, str], queryset: QuerySet) -> float:
        return (queryset.aggregate(s=models.Sum(related_data["field"]))["s"] or 0) * -1

    def update_calculated_value_of_booking_entry(self):
        try:
            BookingEntry = apps.get_model("wbaccounting", "BookingEntry")  # type: ignore
            booking_entries = BookingEntry.objects.filter(  # type: ignore
                related_data__model="wbcommission.Rebate",
                related_data__data__date_gte__lte=self.date.strftime("%Y-%m-%d"),
                related_data__data__date_lte__gte=self.date.strftime("%Y-%m-%d"),
                related_data__data__recipient_id=self.recipient.id,
                related_data__data__product_id=self.product.id,
            )

            for booking_entry in booking_entries:
                booking_entry.calculated_value = booking_entry.get_related_data_accounting_sum()  # type: ignore
                booking_entry.save()  # type: ignore
        except LookupError:
            pass


# ----------- TASKS -----------


@shared_task(queue="commission")
def manage_rebate_as_task(
    main_account_id: int,
    start_date: date_lib | None = None,
    only_content_object_ids: list[int] | None = None,
    terminal_account_id: int | None = None,
    user: User | None = None,
    **kwargs,
):
    account = Account.objects.get(id=main_account_id)
    terminal_account_filter_dict = dict(id=terminal_account_id) if terminal_account_id else dict()
    Rebate.manage_rebate(
        main_account=account,
        start_date=start_date,
        only_content_object_ids=only_content_object_ids,
        terminal_account_filter_dict=terminal_account_filter_dict,
        **kwargs,
    )
    if user:
        send_notification(
            code="wbcommission.rebate.computation_done",
            title="Rebate Computation Done",
            body=f"The rebate computation for root account {account} is done",
            user=user,
        )


@receiver(pre_merge, sender="wbcrm.Account")
def handle_pre_merge_account_for_rebate(sender: models.Model, merged_object: Account, main_object: Account, **kwargs):
    """
    Aggregate the rebate if it exists already for the main account. Otherwise, reassign the account to point to the main account
    """
    for rebate in Rebate.objects.filter(account=merged_object).select_for_update():
        try:
            existing_rebate = Rebate.objects.get(
                date=rebate.date,
                recipient=rebate.recipient,
                account=main_object,
                product=rebate.product,
                commission_type=rebate.commission_type,
            )
            existing_rebate.value += rebate.value
            existing_rebate.save()
            rebate.delete()
        except Rebate.DoesNotExist:
            rebate.account = main_object
            rebate.save()
