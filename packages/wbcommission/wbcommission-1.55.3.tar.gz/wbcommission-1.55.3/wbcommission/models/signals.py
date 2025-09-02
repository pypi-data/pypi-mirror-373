from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver
from dynamic_preferences.registries import global_preferences_registry
from wbcrm.models.accounts import Account
from wbportfolio.models import Claim

from .rebate import manage_rebate_as_task


# This file contains the different receiver directly linked to wbportfolio. In a future iteration, this will be moved outside of wbcommission and we will use a generic commission signal
@receiver(post_save, sender="wbportfolio.Claim")
def post_claim_save_for_rebate_computation(sender, instance, created, **kwargs):
    # if a new commission line is created, we create a general rule
    if instance.status == Claim.Status.APPROVED and instance.account and (root_account := instance.account.get_root()):
        if isinstance(
            instance.date, str
        ):  # we need to do this in case claim are created manually with date as string (allowed). This corner case led to date being still a string when it hits this signal
            instance.refresh_from_db()
        manage_rebate_as_task.delay(
            root_account.id,
            start_date=instance.date,
            only_content_object_ids=[instance.product.id],
            terminal_account_id=instance.account.id,
        )


@receiver(post_save, sender="wbportfolio.Fees")
def post_fees_save_for_rebate_computation(sender, instance, created, **kwargs):
    # if a new commission line is created, we create a general rule
    if (
        created
        and (date.today() - instance.fee_date).days
        <= global_preferences_registry.manager()["wbcommission__days_to_recompute_rebate_from_fees_threshold"]
    ):  # we make sure that the fee won't trigger rebate computation if they are created too much in the past
        for root_account in Account.objects.filter(level=0):
            if Claim.objects.filter(
                account__in=root_account.get_descendants(include_self=True), product=instance.product
            ).exists():
                manage_rebate_as_task.delay(
                    root_account.id,
                    start_date=instance.fee_date,
                    only_content_object_ids=[instance.product.id],
                )
