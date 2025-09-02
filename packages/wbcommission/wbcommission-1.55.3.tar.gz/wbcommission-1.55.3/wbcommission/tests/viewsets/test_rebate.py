import pytest
from django.db.models import Sum
from faker import Faker
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories.users import UserFactory
from wbcore.contrib.directory.models import Entry
from wbcore.utils.strings import format_number
from wbcrm.factories.accounts import AccountFactory, AccountRoleFactory

from wbcommission.factories import (
    AccountTypeRoleCommissionFactory,
    CommissionFactory,
    RebateFactory,
)
from wbcommission.models.rebate import Rebate
from wbcommission.viewsets.rebate import RebateModelViewSet, RebatePandasView

fake = Faker()


@pytest.mark.django_db
class TestRebateModelViewSet:
    @pytest.fixture
    def account_user(self):
        # True, we create a superuser

        # if fake.pybool():
        #     user = UserFactory.create(is_superuser=True)
        # else:
        user = UserFactory.create(is_superuser=False)
        entry = Entry.objects.get(id=user.profile.id)

        # Create a bunch of account and roles
        public_account = AccountFactory.create(is_public=True)
        role = AccountRoleFactory.create(account=public_account, entry=entry)
        RebateFactory.create(
            account=public_account,
            commission=AccountTypeRoleCommissionFactory.create(account_role_type_recipient=role.role_type),
        )  # shown rebate

        RebateFactory.create(commission=CommissionFactory.create(crm_recipient=entry))  # shown rebate
        RebateFactory.create()  # hidden rebate
        return user

    def test_ensure_permission_on_rebatetable(self, account_user):
        """
        We ensure that all claims viewset doesn't show more that what the user is allowed to see.
        For claim, the allowed claim are all the claims where the account is among the account they is allowed to see
        """
        allowed_rebates = Rebate.objects.filter_for_user(account_user)

        request = APIRequestFactory().get("")
        request.query_params = {}
        request.user = account_user
        viewset = RebatePandasView(request=request)
        assert allowed_rebates.exists()
        assert allowed_rebates.count() < Rebate.objects.count()  # Ensure that the filtering works
        assert set(allowed_rebates) == set(viewset.get_queryset())
        assert not viewset._get_dataframe().empty

    def test_ensure_permission_on_rebatemodelview(self, account_user):
        """
        We ensure that all claims viewset doesn't show more that what the user is allowed to see.
        For claim, the allowed claim are all the claims where the account is among the account they is allowed to see
        """
        allowed_rebates = Rebate.objects.filter_for_user(account_user)

        request = APIRequestFactory().get("")
        request.user = account_user
        viewset = RebateModelViewSet(request=request)
        queryset = viewset.get_queryset()
        assert allowed_rebates.exists()
        assert allowed_rebates.count() < Rebate.objects.count()  # Ensure that the filtering works
        assert set(allowed_rebates) == set(queryset)
        assert viewset.get_aggregates(queryset, queryset)["value_usd"]["Σ"] == float(
            format_number(allowed_rebates.aggregate(s=Sum("value"))["s"])
        )
