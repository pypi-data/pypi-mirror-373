from django.db.models import Q
from django.dispatch import receiver
from wbcore import filters as wb_filters
from wbcore.contrib.directory.filters import EntryFilter
from wbcore.signals.filters import add_filters
from wbcrm.models.accounts import Account
from wbportfolio.contrib.company_portfolio.filters import PersonFilter


@receiver(add_filters, sender=EntryFilter)
def add_account_filter(sender, request=None, *args, **kwargs):
    def filter_account(queryset, name, value):
        if value:
            return queryset.filter(account_customers__account=value)
        return queryset

    return {
        "account": wb_filters.ModelChoiceFilter(
            label="Account",
            field_name="account",
            queryset=Account.objects.all(),
            endpoint=Account.get_representation_endpoint(),
            value_key=Account.get_representation_value_key(),
            label_key=Account.get_representation_label_key(),
            method=filter_account,
        )
    }


@receiver(add_filters, sender=PersonFilter)
def add_has_user_account_filter(sender, request=None, *args, **kwargs):
    def filter_has_user_account(queryset, name, value):
        if value is True:
            return queryset.filter(Q(user_account__isnull=False))
        elif value is False:
            return queryset.filter(Q(user_account__isnull=True))
        else:
            return queryset

    return {
        "has_user_account": wb_filters.BooleanFilter(
            field_name="has_user_account", label="Has User Account", method=filter_has_user_account
        )
    }
