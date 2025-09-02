from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Generator

import pandas as pd
from wbcrm.models import Account
from wbfdm.models.instruments.instrument_prices import InstrumentPrice
from wbportfolio.models.products import Product
from wbportfolio.models.transactions import Claim, Fees


class AccountRebateManager:
    FEE_MAP = {"management": ["MANAGEMENT"], "performance": ["PERFORMANCE", "PERFORMANCE_CRYSTALIZED"]}

    def __init__(self, root_account: Account, commission_type_key: str):
        self.root_account = root_account
        self.commission_type_key = commission_type_key
        self.terminal_accounts = root_account.get_descendants(include_self=True).filter(
            is_terminal_account=True, is_active=True
        )

    def initialize(self):
        """
        This method aims to initalize the various dataframe used for this Account Rebate Manager
        """
        account_claims = Claim.get_valid_and_approved_claims(account=self.root_account)
        # Get products that are among the tree accounts claims
        claim_products = account_claims.values("product").distinct("product")

        # get the fees as a multi-index matrix
        self.df_fees = pd.DataFrame(
            Fees.valid_objects.filter(
                product__in=claim_products,
                transaction_subtype__in=self.FEE_MAP[self.commission_type_key],
            ).values("product", "fee_date", "total_value")
        )
        if not self.df_fees.empty:
            self.df_fees = (
                self.df_fees.rename(columns={"product": "product", "fee_date": "date"})
                .groupby(["product", "date"])
                .sum()
                .total_value.astype(float)
            )

        # get the shares for the terminal accounts as a multi index matrix
        df_shares = pd.DataFrame(account_claims.values("date_considered", "product", "account", "shares")).rename(
            columns={"date_considered": "date"}
        )

        df_net_value_usd = pd.DataFrame(
            InstrumentPrice.objects.annotate_base_data()
            .filter(instrument__in=claim_products, calculated=False)
            .values("net_value_usd", "date", "instrument")
        ).rename(columns={"instrument": "product"})

        if not df_shares.empty:
            if not self.df_fees.empty:
                timeline = pd.date_range(
                    self.df_fees.index.get_level_values("date").min() - timedelta(days=1),
                    self.df_fees.index.get_level_values("date").max(),
                )
            else:
                timeline = pd.date_range(df_shares["date"].min(), date.today())
            timeline = [ts.date() for ts in timeline]  # Don't know how to do any different but look inefficient to me
            self.df_shares = (
                df_shares[["date", "product", "account", "shares"]]
                .groupby(["account", "product", "date"])
                .sum()
                .astype(float)
            )
            self.df_shares = self.df_shares.reindex(
                pd.MultiIndex.from_product(
                    [self.df_shares.index.levels[0], self.df_shares.index.levels[1], timeline],
                    names=["account", "product", "date"],
                ),
                fill_value=0,
            )
            self.df_shares["shares"] = (
                self.df_shares.groupby(level=["account", "product"])["shares"].cumsum().astype(float)
            )
            if not df_net_value_usd.empty:
                df_net_value_usd = df_net_value_usd.set_index(["product", "date"]).sort_index().astype(float)
                self.df_aum = self.df_shares.join(df_net_value_usd, on=["product", "date"])
                self.df_aum["aum"] = self.df_aum["shares"] * self.df_aum["net_value_usd"]
                self.df_aum = self.df_aum.groupby(["account", "product"]).bfill()["aum"]
            self.df_shares = self.df_shares["shares"]

    def get_iterator(
        self,
        only_content_object_ids: list[int] | None = None,
        start_date: date | None = None,
        terminal_account_filter_dict: dict[str, Any] | None = None,
        **kwargs,
    ) -> Generator[tuple[Account, Product, date], None, None]:
        """
        Given the parameters and the instance root account and commission type, yield all valid terminal account, product and date
        where rebate are expected to be computed

        Args:
            only_content_object_ids: list of product to consider. Default to empty (i.e. all tree accounts products)
            start_date: If specified, filter iterator to start only at the given date. Default to None.
            terminal_account_filter_dict: Divers query filter paramters to be filter out terminal accounts
            **kwargs: Optional keyword argument

        Returns:
            yield the valid terminal account, product and date as a tuple
        """

        terminal_accounts = self.terminal_accounts.all()
        if terminal_account_filter_dict:
            terminal_accounts = terminal_accounts.filter(**terminal_account_filter_dict)
        products_map = {p.id: p for p in Product.objects.all()}
        if (
            hasattr(self, "df_shares")
            and hasattr(self, "df_fees")
            and not self.df_fees.empty
            and not self.df_shares.empty
        ):
            for terminal_account in terminal_accounts:
                with suppress(KeyError):
                    # we mask the day where total shares are greater than 0
                    potential_df = self.df_shares.loc[(terminal_account.id, slice(None), slice(None))]
                    potential_df = potential_df[potential_df > 0]
                    # we remove days where there isn't any fees
                    potential_df = potential_df.mask(self.df_fees == 0, 0)
                    potential_df = potential_df[potential_df > 0].reset_index()
                    if not potential_df.empty:
                        if only_content_object_ids:
                            potential_df = potential_df[potential_df["product"].isin(only_content_object_ids)]
                        if start_date:
                            potential_df = potential_df[potential_df["date"] >= start_date]
                        potential_df["terminal_account"] = terminal_account
                        potential_df["product"] = potential_df["product"].map(products_map)
                        yield from tuple(potential_df[["terminal_account", "product", "date"]].to_records(index=False))

    def get_commission_pool(self, product: Product, compute_date: date) -> Decimal:
        """
        Calculate the commission pool for a specific product on a given date.

        This function calculates the commission pool associated with a specific product
        on a given compute date. The commission pool represents the accumulated fees
        for the product up to the specified date.

        Args:
            product (Product): The product for which to calculate the commission pool.
            compute_date (date): The date for which the commission pool is to be computed.

        Returns:
            Decimal: The commission pool amount for the specified product and date.

        Raises:
            KeyError: If no commission pool data is available for the given product and date,
                  a KeyError will be raised, and the function will return Decimal(0).
        """
        with suppress(KeyError):
            return Decimal(self.df_fees.loc[(product.id, compute_date)])
        return Decimal(0)

    def get_terminal_account_holding_ratio(
        self, terminal_account: Account, product: Product, compute_date: date
    ) -> Decimal:
        """
        Calculate the ratio of product shares held by a terminal account.

        This function calculates the ratio of product shares held by a specific terminal account
        on a given compute date, relative to the outstanding shares of the product on the same date.

        Args:
            terminal_account (Account): The terminal account for which to calculate the holding ratio.
            product (Product): The product for which the holding ratio is calculated.
            compute_date (date): The date for which the holding ratio is computed.

        Returns:
            Decimal: The ratio of product shares held by the terminal account on the given date,
                     relative to the outstanding shares of the product. The value is capped at 1.0.

        Raises:
            InstrumentPrice.DoesNotExist: If no price data is available for the given product and date,
                                         an exception will be caught, and the function will return Decimal(0).
            KeyError: If no holding ratio data is available for the given terminal account, product,
                      and date, a KeyError will be caught, and the function will return Decimal(0).
        """
        with suppress(InstrumentPrice.DoesNotExist, KeyError):
            product_shares = max(
                product.prices.get(date=compute_date, calculated=True).outstanding_shares or Decimal(0), Decimal(0)
            )
            account_shares = max(
                Decimal(self.df_shares.loc[(terminal_account.id, product.id, compute_date)]), Decimal(0)
            )
            if product_shares:
                return min(
                    account_shares / product_shares,
                    Decimal(1.0),  # Cannot have a account share greater than the total product shares
                )
        return Decimal(0)

    def get_root_account_total_holding(self, compute_date: date) -> Decimal:
        """
        Calculate the total assets under management (AUM) for the root account.

        This function calculates the total assets under management (AUM) for the root account
        across all terminal accounts on a specific compute date.

        Args:
            compute_date (date): The date for which the total AUM is calculated.

        Returns:
            Decimal: The total assets under management for the root account on the given date.

        Raises:
            KeyError: If no AUM data is available for any terminal account on the given date,
                      a KeyError will be caught, and the function will return Decimal(0).
        """
        account_aum = Decimal(0)
        for terminal_account in self.terminal_accounts:
            with suppress(KeyError):
                account_aum += Decimal(self.df_aum.loc[(terminal_account.id, slice(None), compute_date)].sum())
        return account_aum
