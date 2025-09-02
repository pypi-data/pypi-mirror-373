import random
from decimal import Decimal

import pytest
from faker import Faker
from pandas.tseries.offsets import BDay
from wbportfolio.models import Claim

from wbcommission.models.account_service import AccountRebateManager

from .mixins import AccountManagerFixture

fake = Faker()


@pytest.mark.django_db
class TestAccountService(AccountManagerFixture):
    def test_get_commission_pool(
        self, management_account_manager, fees_factory, claim_factory, customer_trade_factory
    ):
        mngt_fees = fees_factory.create(transaction_subtype="MANAGEMENT")
        perf_fees = fees_factory.create(  # noqa
            transaction_subtype="PERFORMANCE",
            fee_date=mngt_fees.fee_date,
            product=mngt_fees.product,
        )  # noqa
        claim_factory.create(
            account=management_account_manager.root_account,
            trade=customer_trade_factory.create(underlying_instrument=mngt_fees.product),
            status="APPROVED",
        )
        management_account_manager.initialize()

        assert (
            management_account_manager.get_commission_pool(mngt_fees.product, mngt_fees.fee_date)
            == mngt_fees.total_value
        )

    def test_get_commission_pool_performance(
        self, performance_account_manager, fees_factory, claim_factory, customer_trade_factory
    ):
        mngt_fees = fees_factory.create(transaction_subtype="MANAGEMENT")
        perf_fees = fees_factory.create(
            transaction_subtype="PERFORMANCE",
            fee_date=mngt_fees.fee_date,
            product=mngt_fees.product,
        )
        perf2_fees = fees_factory.create(
            transaction_subtype="PERFORMANCE_CRYSTALIZED",
            fee_date=mngt_fees.fee_date,
            product=mngt_fees.product,
        )

        claim_factory.create(
            account=performance_account_manager.root_account,
            trade=customer_trade_factory.create(underlying_instrument=mngt_fees.product),
            status="APPROVED",
        )
        performance_account_manager.initialize()

        assert (
            performance_account_manager.get_commission_pool(mngt_fees.product, mngt_fees.fee_date)
            == perf_fees.total_value + perf2_fees.total_value
        )

    def test_get_commission_pool_with_calculated(
        self, management_account_manager, fees_factory, claim_factory, customer_trade_factory
    ):
        # check that in case there is only calculate, we return the calculated fees value, but in case there is calculated and real fees, we use the real fees value
        calculated_fees = fees_factory.create(calculated=True, transaction_subtype="MANAGEMENT")
        claim_factory.create(
            account=management_account_manager.root_account,
            trade=customer_trade_factory.create(underlying_instrument=calculated_fees.product),
            status="APPROVED",
        )
        management_account_manager.initialize()

        assert (
            management_account_manager.get_commission_pool(calculated_fees.product, calculated_fees.fee_date)
            == calculated_fees.total_value
        )
        # Check that is there is a non calculated fees, it is used instead of the calculated one
        fees = fees_factory.create(transaction_subtype=calculated_fees.transaction_subtype, calculated=False)
        claim_factory.create(
            account=management_account_manager.root_account,
            trade=customer_trade_factory.create(underlying_instrument=fees.product),
            status="APPROVED",
        )
        management_account_manager.initialize()

        assert management_account_manager.get_commission_pool(fees.product, fees.fee_date) == fees.total_value

    @pytest.mark.parametrize("val_date", [fake.past_date()])
    def test_get_terminal_account_holding_ratio(
        self, account_factory, claim_factory, instrument_price_factory, product_factory, val_date, commission_type
    ):
        product1 = product_factory.create()
        product2 = product_factory.create()
        val_date = (val_date + BDay(0)).date()
        next_val_date = (val_date + BDay(1)).date()

        product1_price_val_date = instrument_price_factory.create(
            date=val_date, instrument=product1, outstanding_shares=Decimal(2e4), calculated=True
        )

        product1_price_next_val_date = instrument_price_factory.create(
            date=next_val_date, instrument=product1, outstanding_shares=Decimal(2e4), calculated=True
        )

        product2_price_val_date = instrument_price_factory.create(
            date=val_date, instrument=product2, outstanding_shares=Decimal(2e4), calculated=True
        )
        product2_price_next_val_date = instrument_price_factory.create(
            date=next_val_date, instrument=product2, outstanding_shares=Decimal(2e4), calculated=True
        )

        parent_account = account_factory.create(is_terminal_account=False, is_active=True)
        claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=parent_account,
        )  # ignore this claim because it's attached to a non terminal account

        child_terminal_account = account_factory.create(
            parent=parent_account, is_terminal_account=True, is_active=True
        )
        claim_factory.create(  # ignore this claim because it's not approved
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            account=child_terminal_account,
            trade__underlying_instrument=product1,
            status=random.choice([Claim.Status.DRAFT, Claim.Status.WITHDRAWN, Claim.Status.PENDING]),
        )
        unvalid_child_terminal_account = account_factory.create(parent=parent_account, is_active=False)
        claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=unvalid_child_terminal_account,
        )  # ignore this claim as the attached account is not active

        valid_claim1 = claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=child_terminal_account,
        )
        valid_claim2 = claim_factory.create(
            trade__value_date=next_val_date,
            trade__transaction_date=(next_val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=child_terminal_account,
        )
        valid_claim3 = claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product2,
            status=Claim.Status.APPROVED,
            account=child_terminal_account,
        )
        product1_price_val_date.refresh_from_db()
        product1_price_next_val_date.refresh_from_db()
        product2_price_val_date.refresh_from_db()
        product2_price_next_val_date.refresh_from_db()

        account_manager = AccountRebateManager(parent_account, commission_type.key)
        account_manager.initialize()
        assert account_manager.get_terminal_account_holding_ratio(
            child_terminal_account, product1, val_date
        ) == pytest.approx((valid_claim1.shares / product1_price_val_date.outstanding_shares), rel=Decimal(1e-6))
        assert account_manager.get_terminal_account_holding_ratio(
            child_terminal_account, product1, next_val_date
        ) == pytest.approx(
            (valid_claim1.shares + valid_claim2.shares) / product1_price_next_val_date.outstanding_shares,
            rel=Decimal(1e-6),
        )
        assert account_manager.get_terminal_account_holding_ratio(
            child_terminal_account, product2, val_date
        ) == pytest.approx((valid_claim3.shares / product2_price_val_date.outstanding_shares), rel=Decimal(1e-6))
        assert account_manager.get_terminal_account_holding_ratio(
            child_terminal_account, product2, next_val_date
        ) == pytest.approx((valid_claim3.shares / product2_price_next_val_date.outstanding_shares), rel=Decimal(1e-6))

    @pytest.mark.parametrize("val_date", [fake.date_object()])
    def test_get_root_account_total_holding(
        self, account_factory, claim_factory, product_factory, instrument_price_factory, val_date, commission_type
    ):
        product1 = product_factory.create()
        product2 = product_factory.create()
        val_date = (val_date + BDay(0)).date()
        next_val_date = (val_date + BDay(1)).date()
        product1_price_val_date = instrument_price_factory.create(date=val_date, instrument=product1, calculated=False)
        product1_price_next_val_date = instrument_price_factory.create(
            date=next_val_date, instrument=product1, calculated=False
        )
        product2_price_val_date = instrument_price_factory.create(date=val_date, instrument=product2, calculated=False)
        product2_price_next_val_date = instrument_price_factory.create(
            date=next_val_date, instrument=product2, calculated=False
        )

        parent_account = account_factory.create(is_terminal_account=False, is_active=True)
        claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=parent_account,
        )  # ignore this claim because it's attached to a non terminal account

        child_terminal_account = account_factory.create(
            parent=parent_account, is_terminal_account=True, is_active=True
        )
        claim_factory.create(  # ignore this claim because it's not approved
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            account=child_terminal_account,
            trade__underlying_instrument=product1,
            status=random.choice([Claim.Status.DRAFT, Claim.Status.WITHDRAWN, Claim.Status.PENDING]),
        )
        unvalid_child_terminal_account = account_factory.create(parent=parent_account, is_active=False)
        claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=unvalid_child_terminal_account,
        )  # ignore this claim as the attached account is not active

        valid_claim1 = claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=child_terminal_account,
        )
        valid_claim2 = claim_factory.create(
            trade__value_date=next_val_date,
            trade__transaction_date=(next_val_date - BDay(1)).date(),
            trade__underlying_instrument=product1,
            status=Claim.Status.APPROVED,
            account=child_terminal_account,
        )
        valid_claim3 = claim_factory.create(
            trade__value_date=val_date,
            trade__transaction_date=(val_date - BDay(1)).date(),
            trade__underlying_instrument=product2,
            status=Claim.Status.APPROVED,
            account=child_terminal_account,
        )

        account_manager = AccountRebateManager(parent_account, commission_type.key)
        account_manager.initialize()

        valid_claim1_aum = (  # noqa
            valid_claim1.shares
            * product1_price_val_date.net_value
            * product1_price_val_date.currency_fx_rate_to_usd.value
        )
        valid_claim2_aum = (  # noqa
            valid_claim2.shares
            * product1_price_next_val_date.net_value
            * product1_price_next_val_date.currency_fx_rate_to_usd.value
        )
        valid_claim3_aum = (  # noqa
            valid_claim3.shares
            * product2_price_val_date.net_value
            * product2_price_val_date.currency_fx_rate_to_usd.value
        )
        assert account_manager.get_root_account_total_holding(val_date) == (
            pytest.approx(
                (
                    valid_claim1.shares * product1_price_val_date._net_value_usd
                    + valid_claim3.shares * product2_price_val_date._net_value_usd
                ),
                rel=Decimal(1e-6),
            )
        )
        assert account_manager.get_root_account_total_holding(next_val_date) == (
            pytest.approx(
                (valid_claim1.shares + valid_claim2.shares) * product1_price_next_val_date._net_value_usd
                + valid_claim3.shares * product2_price_next_val_date._net_value_usd,
                rel=Decimal(1e-8),
            )
        )
