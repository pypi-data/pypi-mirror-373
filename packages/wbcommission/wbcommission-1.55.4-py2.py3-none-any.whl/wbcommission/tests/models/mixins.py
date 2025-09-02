import pytest
from wbcrm.factories import AccountFactory

from wbcommission.factories import CommissionTypeFactory
from wbcommission.models.account_service import AccountRebateManager


class AccountManagerFixture:
    @pytest.fixture()
    def performance_account_manager(self):
        commission_type = CommissionTypeFactory.create(name="PERFORMANCE")
        account_manager = AccountRebateManager(AccountFactory.create(), commission_type.key)
        account_manager.initialize()

        return account_manager

    @pytest.fixture()
    def management_account_manager(self):
        commission_type = CommissionTypeFactory.create(name="MANAGEMENT")
        account_manager = AccountRebateManager(AccountFactory.create(), commission_type.key)
        account_manager.initialize()

        return account_manager
