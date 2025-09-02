import factory

from wbcommission.models import Rebate


class RebateFactory(factory.django.DjangoModelFactory):
    date = factory.Faker("date_object")

    commission = factory.SubFactory("wbcommission.factories.CommissionFactory")
    account = factory.LazyAttribute(lambda o: o.commission.account)
    commission_type = factory.LazyAttribute(lambda o: o.commission.commission_type)
    product = factory.SubFactory("wbportfolio.factories.ProductFactory")
    recipient = factory.SubFactory("wbcore.contrib.directory.factories.entries.PersonFactory")
    value = factory.Faker("pydecimal", positive=True, max_value=1000000, right_digits=4)

    class Meta:
        model = Rebate
