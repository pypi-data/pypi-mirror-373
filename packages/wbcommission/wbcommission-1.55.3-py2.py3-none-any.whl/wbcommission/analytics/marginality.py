from datetime import date, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
from django.db.models import Case, OuterRef, Subquery, Value, When
from django.db.models.functions import Coalesce
from pandas._libs.tslibs.offsets import BDay
from wbcore.contrib.currency.models import CurrencyFXRates
from wbfdm.models import InstrumentPrice
from wbportfolio.models import Fees

from wbcommission.models import CommissionType, Rebate


class MarginalityCalculator:
    FEE_MAP = {
        "MANAGEMENT": "management",
        "PERFORMANCE": "performance",
        "PERFORMANCE_CRYSTALIZED": "performance",
    }

    def __init__(self, products, from_date: date, to_date: date):
        bday_from_date = (from_date + timedelta(days=1) - BDay(1)).date()
        bday_to_date = (to_date - timedelta(days=1) + BDay(1)).date()

        products = products.annotate(
            fx_rate=Coalesce(
                Subquery(
                    CurrencyFXRates.objects.filter(
                        currency=OuterRef("currency"), date=OuterRef("last_valuation_date")
                    ).values("value")[:1]
                ),
                Decimal(1.0),
            )
        )

        self.fx_rates = (
            pd.DataFrame(products.values_list("id", "fx_rate"), columns=["id", "fx_rate"])
            .set_index("id")["fx_rate"]
            .astype(float)
        )

        # compute net marginality
        self.df_aum = pd.DataFrame(
            InstrumentPrice.objects.annotate_base_data()
            .filter(instrument__in=products, date__gte=bday_from_date, date__lte=bday_to_date)
            .values_list("calculated", "net_value_usd", "date", "outstanding_shares", "instrument"),
            columns=["calculated", "net_value_usd", "date", "outstanding_shares", "instrument"],
        ).rename(columns={"instrument": "id"})
        self.df_aum["date"] = pd.to_datetime(self.df_aum["date"])
        self.df_aum = (
            self.df_aum.sort_values(by="calculated")
            .groupby(["id", "date"])
            .agg({"net_value_usd": "last", "outstanding_shares": "first"})
        )
        self.df_aum = (self.df_aum.net_value_usd * self.df_aum.outstanding_shares).astype(float)
        self.df_aum = self.df_aum.reindex(
            pd.MultiIndex.from_product(
                [
                    self.df_aum.index.levels[0],
                    pd.date_range(
                        self.df_aum.index.get_level_values("date").min(),
                        self.df_aum.index.get_level_values("date").max(),
                    ),
                ],
                names=["id", "date"],
            ),
            method="ffill",
        ).dropna()

        # Build the fees dataframe where product id is the index and colum are the every fees type available and value are the amount.
        fees = Fees.valid_objects.filter(
            fee_date__lte=bday_to_date,
            fee_date__gte=bday_from_date,
            transaction_subtype__in=self.FEE_MAP.keys(),
            product__in=products,
        ).annotate(
            fee_type=Case(
                *[When(transaction_subtype=k, then=Value(v)) for k, v in self.FEE_MAP.items()],
                default=Value("management"),
            )
        )
        self.df_fees = pd.DataFrame(
            fees.values_list("product", "fee_type", "total_value", "fee_date", "calculated"),
            columns=["product", "fee_type", "total_value", "fee_date", "calculated"],
        ).rename(columns={"product": "id", "fee_date": "date"})
        self.df_fees["date"] = pd.to_datetime(self.df_fees["date"])

        self.df_fees = (
            self.df_fees[["fee_type", "total_value", "id", "date"]]
            .pivot_table(index=["id", "date"], columns="fee_type", values="total_value", aggfunc="sum")
            .astype("float")
            .round(4)
        )
        self.df_fees["total"] = self.df_fees.sum(axis=1)
        self.df_fees = self.df_fees.reindex(self.df_aum.index, fill_value=0)
        self.df_fees = self._rolling_average_monday(self.df_fees)
        self.df_fees = self.df_fees[
            (self.df_fees.index.get_level_values(1) >= pd.Timestamp(from_date))
            & (self.df_fees.index.get_level_values(1) <= pd.Timestamp(to_date))
        ]

        # Build the fees dataframe where product id is the index and colum are the every fees type available and value are the amount.
        self.df_rebates = pd.DataFrame(
            Rebate.objects.filter(date__gte=bday_from_date, date__lte=bday_to_date, product__in=products).values_list(
                "product", "value", "date", "commission_type__key"
            ),
            columns=["product", "value", "date", "commission_type__key"],
        ).rename(columns={"product": "id"})
        self.df_rebates["date"] = pd.to_datetime(self.df_rebates["date"])

        self.df_rebates = (
            pd.pivot_table(
                self.df_rebates,
                index=["id", "date"],
                columns="commission_type__key",
                values="value",
                aggfunc="sum",
                fill_value=0,
            )
            .astype("float")
            .round(4)
        )
        self.df_rebates = self.df_rebates.reindex(self.df_aum.index, fill_value=0)
        self.df_rebates["total"] = self.df_rebates.sum(axis=1)
        self.df_rebates = self._rolling_average_monday(self.df_rebates)
        self.df_rebates = self.df_rebates[
            (self.df_rebates.index.get_level_values(1) >= pd.Timestamp(from_date))
            & (self.df_rebates.index.get_level_values(1) <= pd.Timestamp(to_date))
        ]
        # Initialize basic column
        self.df_aum = self.df_aum[
            (self.df_aum.index.get_level_values(1) >= pd.Timestamp(from_date))
            & (self.df_aum.index.get_level_values(1) <= pd.Timestamp(to_date))
        ]
        self.empty_column = pd.Series(0.0, dtype="float64", index=self.df_aum.index)
        self._set_basics_statistics()

    def _set_basics_statistics(self):
        groupby_fees = self.df_fees.groupby(level=0).sum(numeric_only=True)
        groupby_rebates = self.df_rebates.groupby(level=0).sum(numeric_only=True)
        for key in [*CommissionType.objects.values_list("key", flat=True), "total"]:
            fees = groupby_fees.get(key, self.empty_column)
            rebates = groupby_rebates.get(key, self.empty_column)
            fees_usd = fees * self.fx_rates
            rebates_usd = rebates * self.fx_rates
            marginality = fees - rebates
            marginality_usd = fees_usd - rebates_usd
            marginality_percent = (fees - rebates) / fees.replace(0, np.nan)
            marginality_percent_usd = (fees_usd - rebates_usd) / fees_usd.replace(0, np.nan)

            setattr(self, f"{key}_fees", fees.rename(f"{key}_fees"))
            setattr(self, f"{key}_rebates", rebates.rename(f"{key}_rebates"))
            setattr(self, f"{key}_fees_usd", fees_usd.rename(f"{key}_fees_usd"))
            setattr(self, f"{key}_rebates_usd", rebates_usd.rename(f"{key}_rebates_usd"))
            setattr(self, f"{key}_marginality", marginality.rename(f"{key}_marginality"))
            setattr(self, f"{key}_marginality_usd", marginality_usd.rename(f"{key}_marginality_usd"))
            setattr(self, f"{key}_marginality_percent", marginality_percent.rename(f"{key}_marginality_percent"))
            setattr(
                self,
                f"{key}_marginality_percent_usd",
                marginality_percent_usd.rename(f"{key}_marginality_percent_usd"),
            )

    def _rolling_average_monday(self, df):
        """
        This utility method take a dataframe and assum the values on Mondays are accumulated over the weekend. So we need to average every Saturday, Sunday and Monday together.
        """

        monday = df[df.index.get_level_values("date").weekday == 0] / 3
        monday = monday.reindex(df.index, method="bfill")
        df[df.index.get_level_values("date").weekday.isin([5, 6, 0])] = monday[
            df.index.get_level_values("date").weekday.isin([5, 6, 0])
        ]
        return df

    def get_net_marginality(self, type: str) -> pd.Series:
        return (
            ((self.df_fees.get(type, self.empty_column) - self.df_rebates.get(type, self.empty_column)) / self.df_aum)
            .groupby("id")
            .mean()
        ) * 360

    def get_aggregated_net_marginality(self, type: str) -> pd.Series:
        # we compute the total net marginality for management for the aggregate function
        total_aum = self.df_aum.groupby(level=1).sum()
        return (
            (
                (
                    self.df_fees.get(type, self.empty_column).groupby(level=1).sum()
                    - self.df_rebates.get(type, self.empty_column).groupby(level=1).sum()
                )
                / total_aum
            ).mean(axis=0)
        ) * 360
