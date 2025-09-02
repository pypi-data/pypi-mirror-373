from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from faker import Faker
from pandas.tseries.offsets import BDay
from psycopg.types.range import DateRange, NumericRange
from wbportfolio.models import Claim, Trade
from wbportfolio.models.roles import PortfolioRole

from wbcommission.models import Commission, CommissionRule, CommissionType

fake = Faker()


@pytest.mark.django_db
class TestCommissionModel:
    def test_init(self, commission):
        assert commission.id is not None

    def test_init_account_role_type_commission(self, account_role_type_commission):
        assert account_role_type_commission.id is not None

    def test_init_portfolio_role_commission(self, portfolio_role_commission):
        assert portfolio_role_commission.id is not None

    @pytest.mark.parametrize(
        "validity_date, is_superuser",
        [
            (fake.date_object(), True),
            (fake.date_object(), False),
        ],
    )
    def test_filter_for_user(
        self,
        user,
        commission_factory,
        commission_role_factory,
        account_factory,
        account_role_factory,
        validity_date,
        is_superuser,
    ):
        # Create a public account without any account role. The linked commission rule cannot be seen by the user
        public_account_without_role = account_factory.create(is_public=True)
        public_account_without_role_commission = commission_factory.create(  # noqa
            is_hidden=fake.pybool(), account=public_account_without_role
        )  # noqa

        recipient_commission = commission_factory.create(is_hidden=fake.pybool(), crm_recipient=user.profile.entry_ptr)

        # Create a public account with a account role for the user, the underlying commision line can be seen by the user
        public_account_with_role = account_factory.create(is_public=True)
        account_role_factory.create(account=public_account_with_role, entry=user.profile.entry_ptr)
        public_account_with_role_commission = commission_factory.create(
            is_hidden=False, account=public_account_with_role
        )  # noqa
        # any public sub accounts can be seen by the user, as any commission lines attached to these sub account but as it is hidden, it will not show
        sub_public_account_with_parent_role = account_factory.create(parent=public_account_with_role)
        sub_public_account_with_parent_role_commission = commission_factory.create(  # noqa
            is_hidden=True, account=sub_public_account_with_parent_role
        )
        # Private account without role, so cannot be seen by the user, as any commission line
        private_account_without_role = account_factory.create(is_public=False)
        private_account_without_role_commission = commission_factory.create(  # noqa
            is_hidden=False, account=private_account_without_role
        )

        # Private account with a role, so the underlying commission line can be seen by the user
        private_account_with_role = account_factory.create(is_public=False)
        account_role_factory.create(account=private_account_with_role, entry=user.profile.entry_ptr)
        unhidden_commission_with_role_on_private_account = commission_factory.create(
            is_hidden=False, account=private_account_with_role
        )  # noqa

        # Private account with a role, but expired, so the commission line cannot be seen by the user
        private_account_with_unvalid_role = account_factory.create(  # noqa
            is_public=False,
        )
        account_role_factory.create(
            account=private_account_with_unvalid_role,
            entry=user.profile.entry_ptr,
            visibility_daterange=DateRange(date.min, fake.past_date()),  # type: ignore
        )
        private_account_with_unvalid_role_commission = commission_factory.create(  # noqa
            is_hidden=False, account=private_account_with_unvalid_role
        )

        # Valid role an private account but the commission line is hidden so the user cannot see this commission line
        private_account_with_valid_role_hidden_commission = commission_factory.create(  # noqa
            is_hidden=True, account=private_account_with_role
        )  # noqa Valid account role but commission line hidden, so won't show up

        # Commission line on account without any role, but the user as direct commission role so they can see it
        commission_with_direct_role = commission_role_factory.create(person=user.profile).commission
        if is_superuser:
            user.user_permissions.add(
                Permission.objects.get(content_type__app_label="wbcommission", codename="administrate_commission")
            )
        user = get_user_model().objects.get(id=user.id)
        if is_superuser:
            assert set(Commission.objects.filter_for_user(user, validity_date)) == set(Commission.objects.all())
        else:
            assert set(Commission.objects.filter_for_user(user)) == {
                public_account_with_role_commission,
                recipient_commission,
                unhidden_commission_with_role_on_private_account,
                commission_with_direct_role,
            }

    @pytest.mark.parametrize("val_date", [fake.date_object()])
    def test_get_recipients(self, commission, product, val_date):
        assert set(commission.get_recipients(commission.account, product, val_date)) == {
            (commission.crm_recipient, Decimal(1.0))
        }

    @pytest.mark.parametrize("val_date", [fake.date_object()])
    def test_get_recipients_portfolio_role(
        self,
        portfolio_role_commission_factory,
        product,
        val_date,
        product_portfolio_role_factory,
    ):
        # Create valid portfolio roles
        valid_role1 = product_portfolio_role_factory.create(instrument=product, start=val_date)
        valid_role2 = product_portfolio_role_factory.create(
            instrument=None, start=val_date, role_type=valid_role1.role_type
        )
        valid_role3 = product_portfolio_role_factory.create(
            instrument=product, start=val_date - timedelta(days=1), end=val_date, role_type=valid_role1.role_type
        )
        # create invalid portfolio roles
        unvalid_role1 = product_portfolio_role_factory.create(  # noqa
            instrument=product, end=val_date + timedelta(days=1)
        )  # noqa
        unvalid_role2 = product_portfolio_role_factory.create(  # noqa
            instrument=product,
            start=val_date,
            role_type=PortfolioRole.RoleType.ANALYST
            if valid_role1.role_type == PortfolioRole.RoleType.PORTFOLIO_MANAGER
            else PortfolioRole.RoleType.PORTFOLIO_MANAGER,
        )  # noqa

        # create commission of type portfolio role whose type correspond to valid_role1's type
        commission = portfolio_role_commission_factory.create(portfolio_role_recipient=valid_role1.role_type)
        total_weighting = valid_role1.weighting + valid_role2.weighting + valid_role3.weighting
        # We expect all recipients who have a portfolio role of type role1 to get a share of that commission line
        res = {k: v for k, v in commission.get_recipients(commission.account, product, val_date)}
        assert res[valid_role1.person.entry_ptr] == pytest.approx(
            Decimal(valid_role1.weighting / total_weighting), rel=Decimal(1e-6)
        )
        assert res[valid_role2.person.entry_ptr] == pytest.approx(
            Decimal(valid_role2.weighting / total_weighting), rel=Decimal(1e-6)
        )
        assert res[valid_role3.person.entry_ptr] == pytest.approx(
            Decimal(valid_role3.weighting / total_weighting), rel=Decimal(1e-6)
        )

    @pytest.mark.parametrize("val_date", [fake.date_object()])
    def test_get_recipients_account_role(
        self, account_type_role_commission_factory, account_factory, account_role_factory, product, val_date
    ):
        parent_account = account_factory.create()
        valid_parent_role1 = account_role_factory.create(
            account=parent_account, weighting=0.5
        )  # parent account role but not direct account role, thus invalid
        unvalid_role1 = account_role_factory.create(  # noqa
            account=parent_account,
            visibility_daterange=DateRange(date.min, val_date),  # type: ignore
        )  # parent account role but not direct account role, thus invalid
        child_account = account_factory.create(parent=parent_account)

        # create valid account role for that child account
        valid_role1 = account_role_factory.create(
            account=child_account, role_type=valid_parent_role1.role_type, weighting=0.4
        )
        valid_role2 = account_role_factory.create(
            account=child_account, role_type=valid_parent_role1.role_type, weighting=0.1
        )
        account_role_factory.create(account=child_account)  # noqa Other role type, therefore unvalid

        # Create commission of type account type role for that accout role type of unvalid_role1
        account_role_type_commission = account_type_role_commission_factory.create(
            account=parent_account, account_role_type_recipient=valid_parent_role1.role_type
        )
        res = {k: v for k, v in account_role_type_commission.get_recipients(child_account, product, val_date)}
        # we expect every profile who have an account role fo type unvalid_role1.role_type to gain from this commission line
        assert res[valid_role1.entry] == pytest.approx(Decimal(0.4), rel=Decimal(1e-6))
        assert res[valid_role2.entry] == pytest.approx(Decimal(0.1), rel=Decimal(1e-6))
        assert res[valid_parent_role1.entry] == pytest.approx(Decimal(0.5), rel=Decimal(1e-6))

        assert (
            next(account_role_type_commission.get_recipients(parent_account, product, val_date))[0]
            == valid_parent_role1.entry
        )
        assert next(account_role_type_commission.get_recipients(parent_account, product, val_date))[
            1
        ] == pytest.approx(Decimal(0.5 / 0.5), rel=Decimal(1e-6))

    @pytest.mark.parametrize("validity_date, min_aum", [(fake.date_object(), fake.pydecimal(min_value=0))])
    def test_is_valid(self, commission, product, validity_date, min_aum):
        # basic test for is_valid. We expect the "validated_percent" and "validated_net_commission" to be set properly upon validation
        rule = commission.rules.first()
        rule.percent = Decimal(0.2)
        rule.save()
        rule.refresh_from_db()
        assert commission.is_valid(validity_date, product, min_aum)
        assert commission.validated_percent == rule.percent
        assert commission.validated_net_commission == commission.net_commission

    @pytest.mark.parametrize("validity_date, min_aum", [(fake.date_object(), fake.pydecimal(min_value=0))])
    def test_is_valid_with_exclusion_rule(
        self, commission, commission_exclusion_rule_factory, product, validity_date, min_aum, account_role_type
    ):
        # test overriding of commission rule by exclusion rule on a specific product
        rule = commission.rules.first()
        rule.percent = Decimal(0.2)
        rule.save()
        rule.refresh_from_db()
        exclusion_rule = commission_exclusion_rule_factory.create(
            product=product,
            commission_type=commission.commission_type,
        )
        exclusion_rule.refresh_from_db()
        assert commission.is_valid(validity_date, product, min_aum)
        assert commission.validated_percent == exclusion_rule.overriding_percent
        assert commission.validated_net_commission == exclusion_rule.get_net_or_gross(commission.net_commission)

        # we assign a explicit account type  for the commission
        commission.exclusion_rule_account_role_type = account_role_type
        commission.save()
        exclusion_rule_for_specific_account_type = commission_exclusion_rule_factory.create(
            product=product, commission_type=commission.commission_type, account_role_type=account_role_type
        )
        exclusion_rule_for_specific_account_type.refresh_from_db()
        assert commission.is_valid(validity_date, product, min_aum)
        assert commission.validated_percent == exclusion_rule_for_specific_account_type.overriding_percent
        assert commission.validated_net_commission == exclusion_rule_for_specific_account_type.get_net_or_gross(
            commission.net_commission
        )

    @pytest.mark.parametrize(
        "validity_date, min_aum", [(fake.date_object(), fake.pydecimal(min_value=10, max_value=100))]
    )
    def test_is_invalid_aum(self, commission, product, validity_date, min_aum):
        rule = commission.rules.first()
        rule.assets_under_management_range = NumericRange(min_aum, None)  # type: ignore
        rule.save()
        assert not commission.is_valid(validity_date, product, min_aum - Decimal(1))

    @pytest.mark.parametrize("validity_date, min_aum", [(fake.date_object(), fake.pydecimal(min_value=1000000))])
    def test_is_invalid_date(self, commission, product, validity_date, min_aum):
        rule = commission.rules.first()
        rule.timespan = DateRange(validity_date + timedelta(days=1), date.max)  # type: ignore
        rule.save()
        assert not commission.is_valid(validity_date, product, min_aum)


@pytest.mark.django_db
class TestCommissionType:
    @pytest.mark.parametrize(
        "commission_type__name,net_commission,compute_date,percent1,percent2",
        [
            (
                "MANAGEMENT",
                True,
                fake.date_object(),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
            ),
            (
                "MANAGEMENT",
                False,
                fake.date_object(),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
            ),
            (
                "PERFORMANCE",
                True,
                fake.date_object(),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
            ),
            (
                "PERFORMANCE",
                False,
                fake.date_object(),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
                fake.pydecimal(min_value=0, max_value=1, right_digits=2) / Decimal(2),
            ),
        ],
    )
    def test_get_valid_commissions(
        self, account, product, commission_factory, commission_type, net_commission, compute_date, percent1, percent2
    ):
        # Here we test the following:
        # - computation of net/gross fees
        # - invalid commission rules are not considered
        invalid_aum_commission = commission_factory.create(  # noqa
            account=account,
            commission_type=commission_type,
            net_commission=net_commission,
            order=0,
            rule_aum=NumericRange(1e6 + 1, None),  # type: ignore
        )  # invalid commission rule because the aum range is below the total aum
        invalid_date_commission = commission_factory.create(  # noqa
            account=account,
            commission_type=commission_type,
            net_commission=net_commission,
            order=1,
            rule_timespan=DateRange(date.min, compute_date),  # type: ignore
        )  # invalid commission rule because the rule is not valid for the given date

        commission1 = commission_factory.create(
            account=account,
            commission_type=commission_type,
            net_commission=net_commission,
            order=2,
            rule_percent=percent1,
        )
        commission2 = commission_factory.create(
            account=account,
            commission_type=commission_type,
            net_commission=net_commission,
            order=3,
            rule_percent=percent2,
        )
        commission3 = commission_factory.create(
            account=account,
            commission_type=commission_type,
            net_commission=False,
            order=4,
            rule_percent=Decimal(1) - percent1 - percent2 + Decimal(0.5),
        )  # We add to much percent so that the sum of gross percent is greater than 1
        commission4 = commission_factory.create(  # noqa
            account=account, commission_type=commission_type, net_commission=False, order=5, rule_percent=percent1
        )  # there isn't any gross percent left, so the result is always zero

        res = list(commission_type.get_valid_commissions(account, compute_date, product, Decimal(1e6)))
        if net_commission:
            assert res == [
                (commission1, percent1),
                (commission2, (Decimal(1.0) - percent1) * percent2),
                (commission3, Decimal(1) - percent1 - (Decimal(1) - percent1) * percent2),
            ]
        else:
            if (
                Decimal(1) - percent1 - percent2 == 0
            ):  # in that case we don't exepct commission 3 to show up as a valid commission as the resulting percent will be zero (i.e. no percent left to assign)
                assert res == [(commission1, percent1), (commission2, percent2)]
            else:
                assert res == [
                    (commission1, percent1),
                    (commission2, percent2),
                    (commission3, Decimal(1) - percent1 - percent2),
                ]

    def test_get_valid_commissions_with_inheritance(
        self, account_factory, commission_factory, commission_type, product
    ):
        compute_date = fake.date_object()
        parent_account = account_factory.create()
        account = account_factory.create(parent=parent_account)

        parent_commission_0 = commission_factory.create(
            account=parent_account,
            commission_type=commission_type,
            net_commission=False,
            order=0,
            rule_percent=Decimal(0.1),
        )
        parent_commission_1 = commission_factory.create(  # noqa
            account=parent_account,
            commission_type=commission_type,
            net_commission=False,
            order=1,
            rule_percent=Decimal(0.2),
        )
        child_account_1 = commission_factory.create(
            account=account, commission_type=commission_type, net_commission=False, order=1, rule_percent=Decimal(0.3)
        )
        child_account_2 = commission_factory.create(
            account=account, commission_type=commission_type, net_commission=False, order=2, rule_percent=Decimal(0.4)
        )
        res = list(commission_type.get_valid_commissions(account, compute_date, product, Decimal(1e6)))
        assert res == [
            (parent_commission_0, parent_commission_0.rules.first().percent),
            (child_account_1, child_account_1.rules.first().percent),
            (child_account_2, child_account_2.rules.first().percent),
        ]

    @pytest.mark.parametrize(
        "val_date, percent1,percent2",
        [
            (
                fake.date_object(),
                fake.pydecimal(positive=True, max_value=1, right_digits=2) / Decimal(2),
                fake.pydecimal(positive=True, max_value=1, right_digits=2) / Decimal(2),
            )
        ],
    )
    def test_compute_rebates(
        self,
        val_date,
        product,
        account,
        fees_factory,
        customer_trade_factory,
        commission_factory,
        account_type_role_commission_factory,
        account_role_factory,
        instrument_price_factory,
        claim_factory,
        percent1,
        percent2,
    ):
        val_date = (val_date + BDay(0)).date()
        val_date_1 = (val_date - BDay(1)).date()
        fees_factory.create(product=product, fee_date=val_date_1, transaction_subtype="PERFORMANCE")
        fees_factory.create(product=product, fee_date=val_date_1, transaction_subtype="MANAGEMENT")
        perf_fees = fees_factory.create(product=product, fee_date=val_date, transaction_subtype="PERFORMANCE")
        mngt_fees = fees_factory.create(product=product, fee_date=val_date, transaction_subtype="MANAGEMENT")
        sub2 = customer_trade_factory.create(
            underlying_instrument=product,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
            value_date=val_date,
            transaction_date=val_date_1,  # we consider only trade in t-1
        )
        sub1 = customer_trade_factory.create(
            underlying_instrument=product,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
            value_date=val_date,
            transaction_date=val_date_1,
        )

        claim = claim_factory(
            trade__value_date=val_date,
            trade__transaction_date=val_date_1,
            account=account,
            trade=sub1,
            product=sub1.underlying_instrument,
            status=Claim.Status.APPROVED,
        )

        product_shares = sub1.shares + sub2.shares
        instrument_price_factory.create(
            instrument=product, outstanding_shares=product_shares, date=val_date, calculated=True
        )
        instrument_price_factory.create(
            instrument=product, outstanding_shares=product_shares, date=val_date, calculated=False
        )
        instrument_price_factory.create(
            instrument=product, outstanding_shares=product_shares, date=val_date_1, calculated=True
        )
        instrument_price_factory.create(
            instrument=product, outstanding_shares=product_shares, date=val_date_1, calculated=False
        )
        account_role1 = account_role_factory.create(account=account)
        account_role2 = account_role_factory.create(account=account, role_type=account_role1.role_type)

        commission_perf = commission_factory.create(
            account=account, commission_type__name="PERFORMANCE", order=0, rule_percent=percent1
        )
        commission_perf_account_role = account_type_role_commission_factory.create(  # noqa
            account=account,
            commission_type__name="PERFORMANCE",
            order=1,
            rule_percent=percent2,
            account_role_type_recipient=account_role1.role_type,
        )
        commission_mngt = commission_factory.create(
            account=account, commission_type__name="MANAGEMENT", order=0, rule_percent=percent1
        )
        res = dict()
        for commission_type in CommissionType.objects.all():
            for (
                terminal_account,
                compute_date,
                commission,
                product,
                recipient,
                recipient_fees,
                _,
            ) in commission_type.compute_rebates(account):
                res[recipient] = recipient_fees
        assert res[commission_perf.crm_recipient] == pytest.approx(
            perf_fees.total_value * (claim.shares / product_shares) * percent1, rel=Decimal(1e-4)
        )
        assert res[account_role1.entry] == pytest.approx(
            perf_fees.total_value
            * (claim.shares / product_shares)
            * (Decimal(1.0) - percent1)
            * percent2
            / Decimal(2),
            rel=Decimal(1e-4),
        )
        assert res[account_role2.entry] == pytest.approx(
            perf_fees.total_value
            * (claim.shares / product_shares)
            * (Decimal(1.0) - percent1)
            * percent2
            / Decimal(2),
            rel=Decimal(1e-4),
        )
        assert res[commission_mngt.crm_recipient] == pytest.approx(
            mngt_fees.total_value * (claim.shares / product_shares) * percent1, rel=Decimal(1e-4)
        )

    def test_account_merging(self, account_factory, commission_factory, commission_role_factory, rebate_factory):
        # TODO implemetns for commission
        pivot_date = date(2023, 1, 1)
        # for each type a
        base_account = account_factory.create()
        merged_account = account_factory.create()

        base_mngt_commission = commission_factory.create(
            account=base_account, rule_percent=0.2, rule_timespan=DateRange(date.min, pivot_date)
        )
        base_rule = base_mngt_commission.rules.first()
        base_mngt_commission_role = commission_role_factory.create(commission=base_mngt_commission)
        base_mngt_rebate = rebate_factory.create(commission=base_mngt_commission, account=base_account)

        merged_mngt_commission = commission_factory.create(
            crm_recipient=base_mngt_commission.crm_recipient,
            account=merged_account,
            rule_percent=0.5,
            rule_timespan=DateRange(pivot_date + timedelta(days=1), date.max),
        )
        CommissionRule.objects.create(  # we create a rule that overlaps the base rule but to be sure it does not change the base commission rule
            commission=merged_mngt_commission,
            timespan=DateRange(date.min, pivot_date),  # type: ignore
            assets_under_management_range=NumericRange(0, 1000000000000),  # type: ignore
        )
        merged_mngt_commission_role = commission_role_factory.create(commission=merged_mngt_commission)
        merged_mngt_rebate = rebate_factory.create(commission=merged_mngt_commission, account=merged_account)
        merged_mngt_commission_rule = merged_mngt_commission.rules.first()

        merged_perf_commission = commission_factory.create(
            crm_recipient=base_mngt_commission.crm_recipient,
            account=merged_account,
            commission_type__name="Performance",
        )
        merged_perf_commission_rule = merged_perf_commission.rules.first()
        merged_perf_commission_role = commission_role_factory.create(commission=merged_perf_commission)
        merged_perf_rebate = rebate_factory.create(commission=merged_perf_commission, account=merged_account)

        base_account.merge(merged_account)

        base_mngt_commission.refresh_from_db()

        # test that the non overlapping rule are forwarded to the existing commission
        assert set(base_mngt_commission.rules.all()) == {base_rule, merged_mngt_commission_rule}
        assert set(base_mngt_commission.roles.all()) == {base_mngt_commission_role, merged_mngt_commission_role}

        # test that the base rebate didn't change
        base_mngt_rebate.refresh_from_db()
        assert base_mngt_rebate.commission == base_mngt_commission
        assert base_mngt_rebate.account == base_account

        # test that the overlapping commission are simply deleted
        with pytest.raises(Commission.DoesNotExist):
            merged_mngt_commission.refresh_from_db()

        # checked that the rebate from the merged commission is reassigned to the base commission and account
        merged_mngt_rebate.refresh_from_db()
        assert merged_mngt_rebate.commission == base_mngt_commission
        assert merged_mngt_rebate.account == base_account

        base_perf_commission = Commission.objects.get(
            commission_type__key="performance",
            account=base_account,
            crm_recipient=merged_perf_commission.crm_recipient,
        )
        assert set(base_perf_commission.rules.all()) == {merged_perf_commission_rule}
        assert set(base_perf_commission.roles.all()) == {merged_perf_commission_role}
        with pytest.raises(Commission.DoesNotExist):
            merged_perf_commission.refresh_from_db()
        merged_perf_rebate.refresh_from_db()
        assert merged_perf_rebate.commission == base_perf_commission
        assert merged_perf_rebate.account == base_account
