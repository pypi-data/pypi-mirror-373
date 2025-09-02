from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from faker import Faker

from wbcommission.models import CommissionType, Rebate

from .mixins import AccountManagerFixture

fake = Faker()


@pytest.mark.django_db
class TestRebateModel(AccountManagerFixture):
    def test_init(self, rebate):
        assert rebate.id is not None

    def test_rebate_view_permission(self, rebate_factory, user, commission_factory, commission_role_factory):
        # Here we simply test that if the user can see the underlying commission line, they can see the rebate (i.e. we check that the permission is applied for the queryset)
        # We do extensive unit testing on what commisison line a user can see on the corresponding test "test_filter_for_user"
        hidden_commission = commission_factory.create()
        hidden_rebate = rebate_factory.create(commission=hidden_commission)  # noqa

        commission_with_role = commission_factory.create()
        commission_role_factory.create(commission=commission_with_role, person=user.profile)
        visible_rebate = rebate_factory.create(commission=commission_with_role)
        assert set(Rebate.objects.filter_for_user(user)) == {visible_rebate}

        user.user_permissions.add(
            Permission.objects.get(content_type__app_label="wbcommission", codename="administrate_commission")
        )
        user = get_user_model().objects.get(id=user.id)
        assert set(Rebate.objects.filter_for_user(user)) == {visible_rebate, hidden_rebate}

    @patch.object(CommissionType, "compute_rebates")
    @pytest.mark.parametrize("rebate_value", [fake.pydecimal(right_digits=4, min_value=0, max_value=1000000)])
    def test_manage_rebate(self, mock_fct, commission_factory, fees_factory, rebate_value):
        fees = fees_factory.create()
        commission = commission_factory.create()
        # We check that the method create a rebate if none exists
        mock_fct.return_value = [
            (
                commission.account,
                fees.fee_date,
                commission,
                fees.product,
                commission.crm_recipient,
                rebate_value,
                dict(),
            )
        ]
        Rebate.manage_rebate(commission.account)
        new_rebate = Rebate.objects.get(
            commission=commission,
            product=fees.product,
            date=fees.fee_date,
            recipient=commission.crm_recipient,
        )
        assert new_rebate.value == rebate_value

        # we check that the method update the existing rebate
        mock_fct.return_value = [
            (
                commission.account,
                fees.fee_date,
                commission,
                fees.product,
                commission.crm_recipient,
                rebate_value * 2,
                dict(),
            )
        ]
        Rebate.manage_rebate(commission.account)
        new_rebate.refresh_from_db()
        assert new_rebate.value == rebate_value * 2

        # test that if rebate not valid anymore, a recomputation will automatically remove it
        new_commission = commission_factory.create(account=commission.account)
        mock_fct.return_value = [
            (
                commission.account,
                fees.fee_date,
                new_commission,
                fees.product,
                new_commission.crm_recipient,
                rebate_value,
                dict(),
            )
        ]
        Rebate.manage_rebate(commission.account, prune_existing=True)
        with pytest.raises((Rebate.DoesNotExist,)):
            new_rebate.refresh_from_db()
        assert (
            Rebate.objects.get(
                commission=new_commission,
                product=fees.product,
                date=fees.fee_date,
                recipient=new_commission.crm_recipient,
            ).value
            == rebate_value
        )

    def test_account_merging(self, account_factory, rebate_factory):
        """
        We want to test that:
        - Existing rebate for the same unique lookup arg are summed
        - If not existing rebate, then account are shifted
        """
        base_account = account_factory.create()
        merged_account = account_factory.create()
        base_rebate = rebate_factory.create(account=base_account)
        base_rebate.refresh_from_db()
        base_value = base_rebate.value  # for safekeeping

        # a rebate from the account that is going to be merged but with same date, recipient, product, and type. We expect this rebate to be deleted and its value summed to the base rebate
        merged_rebate_but_similar = rebate_factory.create(
            account=merged_account,
            date=base_rebate.date,
            recipient=base_rebate.recipient,
            product=base_rebate.product,
            commission_type=base_rebate.commission_type,
        )
        merged_rebate_but_similar.refresh_from_db()
        # rebate from the merged account but completly different: there won't be any existing rebate, hence the account will just be shifted.
        merged_rebate = rebate_factory.create(account=merged_account)

        base_account.merge(merged_account)
        base_rebate.refresh_from_db()
        assert base_rebate.value == base_value + merged_rebate_but_similar.value

        # check that the redundant rebate was deleted
        with pytest.raises(Rebate.DoesNotExist):
            merged_rebate_but_similar.refresh_from_db()
        merged_rebate.refresh_from_db()
        assert merged_rebate.account == base_account
