from datetime import date

import factory
from psycopg.types.range import DateRange
from wbportfolio.models.roles import PortfolioRole

from wbcommission.models.commission import (
    Commission,
    CommissionExclusionRule,
    CommissionRole,
    CommissionType,
)


class CommissionTypeFactory(factory.django.DjangoModelFactory):
    name = "MANAGEMENT"
    key = factory.LazyAttribute(lambda x: x.name.lower())

    class Meta:
        model = CommissionType
        django_get_or_create = ["key"]


class CommissionFactory(factory.django.DjangoModelFactory):
    account = factory.SubFactory("wbcrm.factories.AccountFactory")
    crm_recipient = factory.SubFactory("wbcore.contrib.directory.factories.entries.EntryFactory")

    portfolio_role_recipient = None
    account_role_type_recipient = None
    order = 0
    commission_type = factory.SubFactory(CommissionTypeFactory)
    net_commission = True
    is_hidden = False

    class Meta:
        model = Commission

    @factory.post_generation
    def rule_timespan(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            v = self.rules.first()
            v.timespan = extracted
            v.save()

    @factory.post_generation
    def rule_aum(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            v = self.rules.first()
            v.assets_under_management_range = extracted
            v.save()

    @factory.post_generation
    def rule_percent(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            v = self.rules.first()
            v.percent = extracted
            v.save()


class PortfolioRoleCommissionFactory(CommissionFactory):
    crm_recipient = None
    account_role_type_recipient = None
    portfolio_role_recipient = factory.Iterator([role_choice[0] for role_choice in PortfolioRole.RoleType.choices])

    class Meta:
        model = Commission


class AccountTypeRoleCommissionFactory(CommissionFactory):
    crm_recipient = None
    portfolio_role_recipient = None
    account_role_type_recipient = factory.SubFactory("wbcrm.factories.AccountRoleTypeFactory")

    class Meta:
        model = Commission


class CommissionRoleFactory(factory.django.DjangoModelFactory):
    commission = factory.SubFactory(CommissionFactory)
    person = factory.SubFactory("wbcore.contrib.directory.factories.entries.PersonFactory")

    class Meta:
        model = CommissionRole


class CommissionExclusionRuleFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory("wbportfolio.factories.products.ProductFactory")
    commission_type = factory.SubFactory(CommissionTypeFactory)
    overriding_percent = factory.Faker("pydecimal", min_value=0, max_value=1, right_digits=2)
    overriding_net_or_gross_commission = "DEFAULT"
    account_role_type = None
    timespan = DateRange(date.min, date.max)

    class Meta:
        model = CommissionExclusionRule
