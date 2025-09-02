from collections import defaultdict
from datetime import date
from decimal import Decimal

import numpy as np
import pandas as pd
from django.contrib.messages import warning
from django.db.models import Exists, ExpressionWrapper, F, FloatField, OuterRef, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import serializers as wb_serializers
from wbcore import viewsets
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import IsInternalUser
from wbcore.serializers import decorator
from wbcore.utils.date import get_date_interval_from_request
from wbcore.utils.strings import format_number
from wbcrm.models.accounts import Account
from wbfdm.models import Classification, ClassificationGroup, InstrumentPrice
from wbfdm.preferences import get_default_classification_group
from wbportfolio.models import Product

from wbcommission.filters import (
    CustomerRebateGroupByFilter,
    RebateDateFilter,
    RebateGroupByFilter,
    RebateMarginalityFilter,
)
from wbcommission.models import CommissionType, Rebate
from wbcommission.models.rebate import RebateGroupbyChoice, manage_rebate_as_task
from wbcommission.reports.audit_report import create_audit_report_and_send_as_task
from wbcommission.reports.customer_report import create_customer_report_and_send_as_task
from wbcommission.serializers import RebateModelSerializer
from wbcommission.viewsets.buttons.rebate import RebateTableButtonConfig
from wbcommission.viewsets.display.rebate import (
    RebatePandasViewDisplayConfig,
    RebateProductMarginalityDisplayConfig,
)
from wbcommission.viewsets.endpoints.rebate import (
    RebatePandasViewEndpointConfig,
    RebateProductMarginalityEndpointConfig,
)
from wbcommission.viewsets.titles.rebate import (
    RebatePandasViewTitleConfig,
    RebateProductMarginalityTitleConfig,
)

from ..analytics.marginality import MarginalityCalculator
from ..permissions import IsCommissionAdmin
from .mixins import RebatePermissionMixin


class RebateModelViewSet(RebatePermissionMixin, viewsets.ModelViewSet):
    serializer_class = RebateModelSerializer
    queryset = Rebate.objects.all()
    filterset_class = RebateDateFilter

    endpoint_config_class = RebatePandasViewEndpointConfig

    def get_aggregates(self, queryset, paginated_queryset):
        return {"value_usd": {"Σ": format_number(queryset.aggregate(s=Sum(F("value_usd")))["s"] or 0)}}

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                fx_rate=Coalesce(CurrencyFXRates.get_fx_rates_subquery("date"), Decimal(1)),
                value_usd=ExpressionWrapper(F("value") * F("fx_rate"), output_field=FloatField()),
            )
        )

    @action(detail=False, methods=["PATCH"], permission_classes=[IsCommissionAdmin])
    def recompute(self, request, pk=None):
        if "start_date" in request.POST:
            prune_existing = request.POST.get("prune_existing", "false") == "true"
            start_date = parse_date(request.POST["start_date"])
            if only_account_ids_repr := request.POST.get("only_accounts", None):
                only_account_ids = only_account_ids_repr.split(",")
                accounts = Account.objects.filter(id__in=only_account_ids, level=0)
            else:
                accounts = Account.objects.filter(level=0)
            for account in accounts:
                manage_rebate_as_task.delay(
                    account.id, start_date=start_date, prune_existing=prune_existing, user=request.user
                )
            return Response({"status": f"{accounts.count()} are being recomputed"}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["GET", "PATCH"], permission_classes=[IsInternalUser])
    def customerreport(self, request, pk=None):
        start, end = get_date_interval_from_request(request, request_type="POST")
        user = request.user
        recipient = get_object_or_404(Entry, pk=request.GET.get("recipient_id", None))
        create_customer_report_and_send_as_task.delay(user.id, recipient.id, start, end)
        return Response({"__notification": {"title": "Report send."}}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET", "PATCH"], permission_classes=[IsCommissionAdmin])
    def auditreport(self, request, pk=None):
        start, end = get_date_interval_from_request(request, request_type="POST")
        user = request.user
        recipient = get_object_or_404(Entry, pk=request.GET.get("recipient_id", None))
        create_audit_report_and_send_as_task.delay(user.id, recipient.id, start, end)
        return Response({"__notification": {"title": "Report send."}}, status=status.HTTP_200_OK)


class RebatePandasView(RebatePermissionMixin, ExportPandasAPIViewSet):
    queryset = Rebate.objects.all()

    filterset_class = RebateGroupByFilter

    search_fields = ["title"]

    display_config_class = RebatePandasViewDisplayConfig
    title_config_class = RebatePandasViewTitleConfig
    endpoint_config_class = RebatePandasViewEndpointConfig
    button_config_class = RebateTableButtonConfig

    def get_ordering_fields(self):
        return ["rebate_total", *map(lambda x: f"rebate_{x}", self.rebate_types.keys())]

    def get_pandas_fields(self, request):
        fields = [pf.PKField(key="id", label="ID"), pf.CharField(key="title", label="Title")]
        for key, label in self.rebate_types.items():
            fields.append(
                pf.FloatField(
                    key="rebate_" + key,
                    label=label,
                    precision=2,
                    decorators=[decorator(decorator_type="text", position="left", value="$")],
                )
            )
        fields.append(
            pf.FloatField(
                key="rebate_total",
                label="Total Rebate",
                precision=2,
                decorators=[decorator(decorator_type="text", position="left", value="$")],
            )
        )
        return pf.PandasFields(fields=fields)

    @cached_property
    def groupby_classification_group(self) -> ClassificationGroup:
        try:
            return ClassificationGroup.objects.get(id=self.request.GET["groupby_classification_group"])
        except (ValueError, KeyError):
            return get_default_classification_group()

    @cached_property
    def rebate_types(self):
        return dict(CommissionType.objects.values_list("key", "name"))

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .annotate(
                fx_rate=CurrencyFXRates.get_fx_rates_subquery("date", lookup_expr="exact"),
                value_usd=F("value") * F("fx_rate"),
            )
        )
        qs = Account.annotate_root_account_info(qs)
        qs = self.groupby_classification_group.annotate_queryset(qs, 0, "product")
        return (
            qs.select_related("product")
            .prefetch_related("product__currency")
            .prefetch_related("product__parent")
            .select_related("recipient")
        )

    def get_dataframe(self, request, queryset, **kwargs):
        groupby = self.request.GET.get("group_by", "PRODUCT")
        groupby_map = RebateGroupbyChoice.map[groupby]
        pivot = groupby_map["pk"]
        pivot_label = groupby_map["title_key"]
        if pivot == "classification_id":
            df = pd.DataFrame(
                queryset.values_list(
                    "value_usd",
                    "commission_type__key",
                    "classifications",
                ),
                columns=["value_usd", "commission_type__key", "classifications"],
            )
            df = (
                df.explode("classifications")
                .rename(columns={"classifications": "classification_id"})
                .replace([np.inf, -np.inf, np.nan], None)
            )
            df["classification_title"] = df.classification_id.map(
                dict(Classification.objects.filter(id__in=df.classification_id.unique()).values_list("id", "name")),
                na_action="ignore",
            )
        else:
            df = pd.DataFrame(
                queryset.values_list(
                    "value_usd",
                    "commission_type__key",
                    pivot,
                    pivot_label,
                ),
                columns=["value_usd", "commission_type__key", pivot, pivot_label],
            )
        df = df.rename(columns={pivot: "id", pivot_label: "title"})
        df = pd.pivot_table(
            df,
            index=["id", "title"],
            columns="commission_type__key",
            values="value_usd",
            aggfunc="sum",
            fill_value=0,
        )
        df["total"] = df.sum(axis=1)
        # Ensure all type are always present as a columns
        for commission_type in self.rebate_types.keys():
            if commission_type not in df.columns:
                df[commission_type] = 0
        df = df.add_prefix("rebate_").reset_index()
        df.id = df.id.fillna(0)
        df.title = df.title.fillna("None")
        df[df.columns.difference(["id", "title"])] = df[df.columns.difference(["id", "title"])].astype("float")
        return df

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        return {
            **{
                "rebate_" + commission_type.key: {
                    "Σ": format_number(df["rebate_" + commission_type.key].sum()),
                }
                for commission_type in CommissionType.objects.all()
            },
            "rebate_total": {
                "Σ": format_number(df["rebate_total"].sum()),
            },
        }

    def get_filterset_class(self, request):
        profile = request.user.profile
        if profile.is_internal or request.user.is_superuser:
            return RebateGroupByFilter
        return CustomerRebateGroupByFilter


class RebateProductMarginalityViewSet(ExportPandasAPIViewSet):
    IDENTIFIER = "wbcommission:product-marginality"

    filterset_class = RebateMarginalityFilter

    pandas_fields = pf.PandasFields(
        fields=[
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="title", label="title"),
            pf.CharField(key="currency_symbol", label="Currency"),
            pf.FloatField(key="base_management_fees_percent", label="Base Management Fees", percent=True),
            pf.FloatField(
                key="management_fees",
                label="management_fees",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="management_rebates",
                label="management_rebates",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="management_marginality",
                label="management_marginality",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(key="base_performance_fees_percent", label="Base Performance Fees", percent=True),
            pf.FloatField(
                key="performance_fees",
                label="performance_fees",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="performance_rebates",
                label="performance_rebates",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="performance_marginality",
                label="performance_marginality",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="total_fees",
                label="total_fees",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="total_rebates",
                label="total_rebates",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}"),
                ],
            ),
            pf.FloatField(key="total_marginality_percent", label="total_marginality_percent", percent=True),
            pf.FloatField(
                key="total_fees_usd",
                label="total_fees_usd",
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(
                key="total_rebates_usd",
                label="total_rebates_usd",
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(
                key="total_marginality_usd",
                label="total_marginality_usd",
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(key="net_management_marginality", label="net_management_marginality", percent=True),
            pf.FloatField(key="net_performance_marginality", label="net_performance_marginality", percent=True),
        ]
    )
    queryset = Product.objects.all()
    ordering_fields = [
        "title",
        "base_management_fees_percent",
        "base_performance_fees_percent",
        "management_fees",
        "management_rebates",
        "management_marginality",
        "performance_fees",
        "performance_rebates",
        "performance_marginality",
        "total_fees",
        "total_rebates",
        "total_marginality_percent",
        "total_fees_usd",
        "total_rebates_usd",
        "total_marginality_usd",
        "net_management_marginality",
    ]
    search_fields = ["title", "bank_title"]
    ordering = ["title"]

    display_config_class = RebateProductMarginalityDisplayConfig
    title_config_class = RebateProductMarginalityTitleConfig
    endpoint_config_class = RebateProductMarginalityEndpointConfig

    def get_aggregates(self, request, df):
        aggregates = {}
        if not df.empty:
            total_fees = df.total_fees.sum()
            total_rebates = df.total_rebates.sum()
            total_marginality_percent = 1 - total_rebates / total_fees if total_fees != 0 else 0

            aggregates = {
                "total_marginality_percent": {"Σ": format_number(total_marginality_percent)},
                "total_fees_usd": {"Σ": format_number(df.total_fees_usd.sum())},
                "total_rebates_usd": {"Σ": format_number(df.total_rebates_usd.sum())},
                "total_marginality_usd": {"Σ": format_number(df.total_marginality_usd.sum())},
            }
            if aggregated_net_management_marginality := getattr(self, "aggregated_net_management_marginality", None):
                aggregates["net_management_marginality"] = {
                    "Σ": format_number(aggregated_net_management_marginality, decimal=4)
                }
            if aggregated_net_performance_marginality := getattr(self, "aggregated_net_performance_marginality", None):
                aggregates["net_performance_marginality"] = {
                    "Σ": format_number(aggregated_net_performance_marginality, decimal=4)
                }
            currency_aggregates = defaultdict(dict)
            for currency_symbol in df["currency_symbol"].unique():
                for field in [
                    "management_fees",
                    "management_rebates",
                    "performance_fees",
                    "performance_rebates",
                    "total_fees",
                    "total_rebates",
                    "management_marginality",
                    "performance_marginality",
                ]:
                    currency_aggregates[field][currency_symbol] = format_number(
                        df.loc[df["currency_symbol"] == currency_symbol, field].sum()
                    )
            aggregates.update(currency_aggregates)
        return aggregates

    @cached_property
    def start(self) -> date | None:
        return get_date_interval_from_request(self.request, exclude_weekend=False)[0]

    @cached_property
    def end(self) -> date | None:
        return get_date_interval_from_request(self.request, exclude_weekend=False)[1]

    def get_queryset(self):
        if self.request.user.has_perm("wbcommission.administrate_commission"):
            has_aum_subquery = InstrumentPrice.objects.filter(instrument=OuterRef("pk"), outstanding_shares__gt=0)
            if self.start and self.end:
                has_aum_subquery = has_aum_subquery.filter(
                    date__gte=self.start,
                    date__lte=self.end,
                )
            return super().get_queryset().annotate(has_aum=Exists(has_aum_subquery))
        return Product.objects.none()

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if queryset.exists() and self.start and self.end:
            if self.start.weekday() in (5, 6) or self.end.weekday() in (5, 6):
                warning(
                    request,
                    _(
                        "The selected date range includes a Saturday or Sunday. Please note that fees and rebates are normalized over the weekend, as fees continue to accumulate during this period."
                    ),
                )
            marginality_calculator = MarginalityCalculator(queryset, self.start, self.end)
            df_products = (
                pd.DataFrame(
                    queryset.values(
                        "id", "computed_str", "current_management_fees", "current_performance_fees", "currency__symbol"
                    )
                )
                .set_index("id")
                .rename(
                    columns={
                        "currency__symbol": "currency_symbol",
                        "computed_str": "title",
                        "current_management_fees": "base_management_fees_percent",
                        "current_performance_fees": "base_performance_fees_percent",
                    }
                )
            )
            # Concat dataframe and add extra statistic columns
            df = pd.concat(
                [
                    df_products["title"],
                    df_products["base_management_fees_percent"],
                    df_products["base_performance_fees_percent"],
                    df_products["currency_symbol"],
                    marginality_calculator.management_fees,
                    marginality_calculator.performance_fees,
                    marginality_calculator.total_fees,
                    marginality_calculator.total_rebates,
                    marginality_calculator.total_marginality_percent,
                    marginality_calculator.management_rebates,
                    marginality_calculator.performance_rebates,
                    marginality_calculator.management_marginality,
                    marginality_calculator.performance_marginality,
                    marginality_calculator.management_marginality_percent,
                    marginality_calculator.total_fees_usd,
                    marginality_calculator.total_rebates_usd,
                    marginality_calculator.total_marginality_usd,
                ],
                axis=1,
            )
            df["net_management_marginality"] = marginality_calculator.get_net_marginality("management")
            df["net_performance_marginality"] = marginality_calculator.get_net_marginality("performance")
            self.aggregated_net_management_marginality = marginality_calculator.get_aggregated_net_marginality(
                "management"
            )
            self.aggregated_net_performance_marginality = marginality_calculator.get_aggregated_net_marginality(
                "performance"
            )
            # Sanitize
            df = df.replace([np.inf, -np.inf, np.nan], 0).reset_index()
            df = df[(df["total_fees"] != 0) | (df["total_rebates"] != 0)]
            return df
        return df
