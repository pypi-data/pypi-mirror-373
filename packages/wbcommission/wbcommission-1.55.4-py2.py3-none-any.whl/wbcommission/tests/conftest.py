from wbcore.tests.conftest import *  # isort: skip # type: ignore
from django.apps import apps
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import (
    AuthenticatedPersonFactory,
    SuperUserFactory,
    UserFactory,
)
from wbcore.contrib.currency.factories import CurrencyFactory, CurrencyFXRatesFactory
from wbcore.contrib.directory.factories.entries import (
    CompanyFactory,
    CompanyTypeFactory,
    CustomerStatusFactory,
    EntryFactory,
    PersonFactory,
)
from wbcore.contrib.geography.factories import (
    CityFactory,
    ContinentFactory,
    CountryFactory,
    StateFactory,
)
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbcrm.factories import AccountFactory, AccountRoleFactory, AccountRoleTypeFactory
from wbfdm.factories import ExchangeFactory, InstrumentFactory, InstrumentTypeFactory, InstrumentPriceFactory
from wbportfolio.factories import (
    ClaimFactory,
    CustomerTradeFactory,
    FeesFactory,
    PortfolioFactory,
    ProductFactory,
    ProductPortfolioRoleFactory,
)

from ..factories import (
    AccountTypeRoleCommissionFactory,
    CommissionExclusionRuleFactory,
    CommissionFactory,
    CommissionRoleFactory,
    CommissionTypeFactory,
    PortfolioRoleCommissionFactory,
    RebateFactory,
)

register(AccountFactory)
register(AccountRoleFactory)
register(AccountRoleTypeFactory)

register(InstrumentFactory)
register(InstrumentTypeFactory)
register(ExchangeFactory)
register(ProductFactory)
register(ProductPortfolioRoleFactory)
register(FeesFactory)
register(PortfolioFactory)
register(InstrumentPriceFactory)
register(ClaimFactory)
register(CustomerTradeFactory)
register(CurrencyFXRatesFactory)

register(CurrencyFactory)
register(CityFactory)
register(StateFactory)
register(CountryFactory)
register(ContinentFactory)

register(CompanyFactory)
register(EntryFactory)
register(PersonFactory)
register(CustomerStatusFactory)
register(CompanyTypeFactory)

register(AuthenticatedPersonFactory, "authenticated_person")
register(UserFactory)
register(SuperUserFactory, "superuser")

register(RebateFactory)
register(CommissionTypeFactory)
register(CommissionFactory)
register(CommissionExclusionRuleFactory)
register(AccountTypeRoleCommissionFactory, "account_role_type_commission")
register(CommissionRoleFactory)
register(PortfolioRoleCommissionFactory, "portfolio_role_commission")
from .signals import *

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbportfolio"))
from .signals import *  # noqa: F401
