from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Company
from wbcore.filters.defaults import current_quarter_date_range
from wbcore.pandas.filterset import PandasFilterSetMixin
from wbfdm.models import ClassificationGroup
from wbfdm.preferences import get_default_classification_group
from wbportfolio.filters.transactions.claim import CommissionBaseFilterSet
from wbportfolio.models import Product

from wbcommission.models import Rebate
from wbcommission.models.rebate import RebateGroupbyChoice


class RebateDateFilter(CommissionBaseFilterSet):
    date = wb_filters.DateRangeFilter(
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        label="Date Range",
        required=True,
        clearable=False,
        initial=current_quarter_date_range,
    )

    class Meta:
        model = Rebate
        fields = {
            "date": ["exact"],
            "account": ["exact"],
            "product": ["exact"],
            "recipient": ["exact"],
            "commission_type": ["exact"],
        }


class RebateGroupByFilter(PandasFilterSetMixin, RebateDateFilter):
    group_by = wb_filters.ChoiceFilter(
        label="Group By",
        choices=RebateGroupbyChoice.choices(),
        initial=RebateGroupbyChoice.ACCOUNT.name,  # typing: ignore
        method=lambda queryset, label, value: queryset,
        clearable=False,
        required=True,
    )
    groupby_classification_group = wb_filters.ModelChoiceFilter(
        initial=lambda k, v, f: get_default_classification_group().id,
        method=lambda queryset, label, value: queryset,
        label="Group by Classification Group",
        queryset=ClassificationGroup.objects.all(),
        endpoint=ClassificationGroup.get_representation_endpoint(),
        value_key=ClassificationGroup.get_representation_value_key(),
        label_key=ClassificationGroup.get_representation_label_key(),
    )

    class Meta:
        model = Rebate
        fields = {"recipient": ["exact"]}
        df_fields = {
            "management__gte": wb_filters.NumberFilter(
                label="Management Fees (USD)", lookup_expr="gte", field_name="management"
            ),
            "management__lte": wb_filters.NumberFilter(
                label="Management Fees (USD)", lookup_expr="lte", field_name="management"
            ),
            "performance__gte": wb_filters.NumberFilter(
                label="Performance Fees (USD)", lookup_expr="gte", field_name="performance"
            ),
            "performance__lte": wb_filters.NumberFilter(
                label="Performance Fees (USD)", lookup_expr="lte", field_name="performance"
            ),
            "total_rebate__gte": wb_filters.NumberFilter(
                label="Total Fees (USD)", lookup_expr="gte", field_name="total_rebate"
            ),
            "total_rebate__lte": wb_filters.NumberFilter(
                label="Total Fees (USD)", lookup_expr="lte", field_name="total_rebate"
            ),
        }


class CustomerRebateGroupByFilter(RebateGroupByFilter):
    product = wb_filters.ModelChoiceFilter(
        label="Product",
        queryset=Product.objects.all(),
        endpoint=Product.get_representation_endpoint(),
        value_key=Product.get_representation_value_key(),
        label_key="{{title}} {{currency_repr}} - {{isin}}",
    )

    class Meta:
        model = Rebate
        fields = {
            # "price_start" : ["gte", "exact", "lte"],
            # "price_end" : ["gte", "exact", "lte"],
            "account": ["exact"],
            "product": ["exact"],
            "recipient": ["exact"],
        }


class RebateMarginalityFilter(PandasFilterSetMixin, wb_filters.FilterSet):
    date = wb_filters.DateRangeFilter(
        label="Date Range",
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        required=True,
        clearable=False,
        initial=current_quarter_date_range,
    )

    bank = wb_filters.ModelMultipleChoiceFilter(
        label="Bank",
        queryset=Company.objects.all(),
        endpoint=Company.get_representation_endpoint(),
        filter_params={"bank_product": True},
        value_key=Company.get_representation_value_key(),
        label_key=Company.get_representation_label_key(),
        method="filter_bank",
    )

    def filter_bank(self, queryset, name, value):
        if value:
            return queryset.filter(bank__in=value)
        return queryset

    class Meta:
        model = Product
        fields = {}
        df_fields = {
            "management_fees__gte": wb_filters.NumberFilter(
                field_name="management_fees", lookup_expr="gte", label="Sum Management Fees"
            ),
            "management_rebates__gte": wb_filters.NumberFilter(
                field_name="management_rebates", lookup_expr="gte", label="Sum Management Rebates"
            ),
            "management_marginality__gte": wb_filters.NumberFilter(
                field_name="management_marginality", lookup_expr="gte", label="Marginality Management"
            ),
            "performance_fees__gte": wb_filters.NumberFilter(
                field_name="performance_fees", lookup_expr="gte", label="Sum Performance Fees"
            ),
            "performance_rebates__gte": wb_filters.NumberFilter(
                field_name="performance_rebates", lookup_expr="gte", label="Sum Performance Rebates"
            ),
            "performance_marginality__gte": wb_filters.NumberFilter(
                field_name="performance_marginality", lookup_expr="gte", label="Marginality Performance"
            ),
            "total_fees__gte": wb_filters.NumberFilter(field_name="total_fees", lookup_expr="gte", label="Total Fees"),
            "total_rebates__gte": wb_filters.NumberFilter(
                field_name="total_rebates", lookup_expr="gte", label="Total Rebates"
            ),
            "total_marginality_percent__gte": wb_filters.NumberFilter(
                field_name="total_marginality_percent", lookup_expr="gte", label="Total Marginality"
            ),
            "total_fees_usd__gte": wb_filters.NumberFilter(
                field_name="total_fees_usd", lookup_expr="gte", label="Total Fees"
            ),
            "total_rebates_usd__gte": wb_filters.NumberFilter(
                field_name="total_rebates_usd", lookup_expr="gte", label="Total Rebates"
            ),
            "management_fees__lte": wb_filters.NumberFilter(
                field_name="management_fees", lookup_expr="lte", label="Sum Management Fees"
            ),
            "management_rebates__lte": wb_filters.NumberFilter(
                field_name="management_rebates", lookup_expr="lte", label="Sum Management Rebates"
            ),
            "management_marginality__lte": wb_filters.NumberFilter(
                field_name="management_marginality", lookup_expr="lte", label="Marginality Management"
            ),
            "performance_fees__lte": wb_filters.NumberFilter(
                field_name="performance_fees", lookup_expr="lte", label="Sum Performance Fees"
            ),
            "performance_rebates__lte": wb_filters.NumberFilter(
                field_name="performance_rebates", lookup_expr="lte", label="Sum Performance Rebates"
            ),
            "performance_marginality__lte": wb_filters.NumberFilter(
                field_name="performance_marginality", lookup_expr="lte", label="Marginality Performance"
            ),
            "total_fees__lte": wb_filters.NumberFilter(field_name="total_fees", lookup_expr="lte", label="Total Fees"),
            "total_rebates__lte": wb_filters.NumberFilter(
                field_name="total_rebates", lookup_expr="lte", label="Total Rebates"
            ),
            "total_marginality_percent__lte": wb_filters.NumberFilter(
                field_name="total_marginality_percent", lookup_expr="lte", label="Total Marginality"
            ),
            "total_fees_usd__lte": wb_filters.NumberFilter(
                field_name="total_fees_usd", lookup_expr="lte", label="Total Fees"
            ),
            "total_rebates_usd__lte": wb_filters.NumberFilter(
                field_name="total_rebates_usd", lookup_expr="lte", label="Total Rebates"
            ),
        }
