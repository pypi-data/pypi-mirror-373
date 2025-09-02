import pytest
from faker import Faker
from pandas.tseries.offsets import BDay
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory
from wbfdm.factories import InstrumentPriceFactory
from wbportfolio.factories import FeesFactory, ProductFactory
from wbportfolio.models import Product

from wbcommission.analytics.marginality import MarginalityCalculator
from wbcommission.factories import CommissionTypeFactory, RebateFactory
from wbcommission.viewsets.rebate import RebateProductMarginalityViewSet

fake = Faker()


def _create_fixture(product, val_date, net_value=100, outstanding_shares=100):
    management = CommissionTypeFactory.create(key="management")
    perforance = CommissionTypeFactory.create(key="performance")
    i1 = InstrumentPriceFactory.create(
        instrument=product, net_value=net_value, outstanding_shares=outstanding_shares, calculated=False, date=val_date
    ).net_value  # create a price of AUM 100*100
    management_fees_1 = FeesFactory.create(
        product=product, fee_date=val_date, transaction_subtype="MANAGEMENT", calculated=False
    ).total_value
    performance_fees_1 = FeesFactory.create(
        product=product, fee_date=val_date, transaction_subtype="PERFORMANCE", calculated=False
    ).total_value
    performance_crys_fees_1 = FeesFactory.create(
        product=product,
        fee_date=val_date,
        transaction_subtype="PERFORMANCE_CRYSTALIZED",
        calculated=False,
    ).total_value
    management_rebate_1 = RebateFactory.create(product=product, date=val_date, commission_type=management).value
    performance_rebate_1 = RebateFactory.create(product=product, date=val_date, commission_type=perforance).value
    if val_date.weekday() == 0:
        return (
            i1,
            management_fees_1 / 3.0,
            performance_fees_1 / 3.0,
            performance_crys_fees_1 / 3.0,
            float(management_rebate_1) / 3.0,
            float(performance_rebate_1) / 3.0,
        )
    else:
        return (
            i1,
            management_fees_1,
            performance_fees_1,
            performance_crys_fees_1,
            float(management_rebate_1),
            float(performance_rebate_1),
        )


@pytest.mark.django_db
class TestMarginalityCalculator:
    @pytest.fixture
    def marginality_calculator(self):
        product = ProductFactory.create()
        start = (fake.date_object() + BDay(0)).date()
        end = (start + BDay(1)).date()

        (
            self.i1,
            self.management_fees_1,
            self.performance_fees_1,
            self.performance_crys_fees_1,
            self.management_rebate_1,
            self.performance_rebate_1,
        ) = _create_fixture(product, start)
        self.product_id = product.id
        self.start = start
        self.end = end
        return MarginalityCalculator(Product.objects.filter(id=product.id), start, end)

    def test_fees(self, marginality_calculator):
        assert marginality_calculator.management_fees.loc[self.product_id] == pytest.approx(
            self.management_fees_1, rel=1e-4
        )
        assert marginality_calculator.performance_fees.loc[self.product_id] == pytest.approx(
            self.performance_fees_1 + self.performance_crys_fees_1, rel=1e-4
        )
        assert marginality_calculator.total_fees.loc[self.product_id] == pytest.approx(
            self.performance_fees_1 + self.performance_crys_fees_1 + self.management_fees_1, rel=1e-4
        )

    def test_rebates(self, marginality_calculator):
        assert marginality_calculator.management_rebates.loc[self.product_id] == pytest.approx(
            self.management_rebate_1, rel=1e-4
        )
        assert marginality_calculator.performance_rebates.loc[self.product_id] == pytest.approx(
            self.performance_rebate_1, rel=1e-4
        )
        assert marginality_calculator.total_rebates.loc[self.product_id] == pytest.approx(
            self.performance_rebate_1 + self.management_rebate_1, rel=1e-4
        )

    def test_fees_usd(self, marginality_calculator):
        assert marginality_calculator.management_fees_usd.loc[self.product_id] == pytest.approx(
            self.management_fees_1, rel=1e-4
        )
        assert marginality_calculator.performance_fees_usd.loc[self.product_id] == pytest.approx(
            self.performance_fees_1 + self.performance_crys_fees_1, rel=1e-4
        )
        assert marginality_calculator.total_fees_usd.loc[self.product_id] == pytest.approx(
            self.performance_fees_1 + self.performance_crys_fees_1 + self.management_fees_1, rel=1e-4
        )

    def test_rebates_usd(self, marginality_calculator):
        assert marginality_calculator.management_rebates_usd.loc[self.product_id] == pytest.approx(
            self.management_rebate_1, rel=1e-4
        )
        assert marginality_calculator.performance_rebates_usd.loc[self.product_id] == pytest.approx(
            self.performance_rebate_1, rel=1e-4
        )
        assert marginality_calculator.total_rebates_usd.loc[self.product_id] == pytest.approx(
            self.performance_rebate_1 + self.management_rebate_1, rel=1e-4
        )

    def test_marginality(self, marginality_calculator):
        assert marginality_calculator.management_marginality.loc[self.product_id] == pytest.approx(
            self.management_fees_1 - self.management_rebate_1, rel=1e-4
        )
        assert marginality_calculator.performance_marginality.loc[self.product_id] == pytest.approx(
            self.performance_fees_1 + self.performance_crys_fees_1 - self.performance_rebate_1, rel=1e-4
        )
        assert marginality_calculator.total_marginality.loc[self.product_id] == pytest.approx(
            (self.performance_fees_1 + self.performance_crys_fees_1 + self.management_fees_1)
            - (self.performance_rebate_1 + self.management_rebate_1),
            rel=1e-4,
        )

    def test_marginality_usd(self, marginality_calculator):
        assert marginality_calculator.management_marginality_usd.loc[self.product_id] == pytest.approx(
            marginality_calculator.management_marginality.loc[self.product_id], rel=1e-4
        )
        assert marginality_calculator.performance_marginality_usd.loc[self.product_id] == pytest.approx(
            marginality_calculator.performance_marginality.loc[self.product_id], rel=1e-4
        )
        assert marginality_calculator.total_marginality_usd.loc[self.product_id] == pytest.approx(
            marginality_calculator.total_marginality.loc[self.product_id], rel=1e-4
        )

    def test_marginality_percent(self, marginality_calculator):
        assert marginality_calculator.management_marginality_percent.loc[self.product_id] == pytest.approx(
            (self.management_fees_1 - float(self.management_rebate_1)) / self.management_fees_1, rel=1e-4
        )
        assert marginality_calculator.performance_marginality_percent.loc[self.product_id] == pytest.approx(
            (self.performance_fees_1 + self.performance_crys_fees_1 - float(self.performance_rebate_1))
            / (self.performance_fees_1 + self.performance_crys_fees_1),
            rel=1e-4,
        )
        assert marginality_calculator.total_marginality_percent.loc[self.product_id] == pytest.approx(
            (
                (self.performance_fees_1 + self.performance_crys_fees_1 + self.management_fees_1)
                - (float(self.performance_rebate_1) + float(self.management_rebate_1))
            )
            / (self.performance_fees_1 + self.performance_crys_fees_1 + self.management_fees_1),
            rel=1e-4,
        )

    def test_marginality_percent_usd(self, marginality_calculator):
        assert marginality_calculator.management_marginality_percent_usd.loc[self.product_id] == pytest.approx(
            marginality_calculator.management_marginality_percent.loc[self.product_id], rel=1e-4
        )
        assert marginality_calculator.performance_marginality_percent_usd.loc[self.product_id] == pytest.approx(
            marginality_calculator.performance_marginality_percent.loc[self.product_id], rel=1e-4
        )
        assert marginality_calculator.total_marginality_percent_usd.loc[self.product_id] == pytest.approx(
            marginality_calculator.total_marginality_percent.loc[self.product_id], rel=1e-4
        )

    def test_get_net_marginality(self, marginality_calculator):
        assert marginality_calculator.get_net_marginality("management").loc[self.product_id] == pytest.approx(
            (self.management_fees_1 - float(self.management_rebate_1)) / (100 * 100) * 360, rel=1e-4
        )

    def test_get_aggregated_net_marginality(self, marginality_calculator):
        product_1 = ProductFactory.create()
        product_2 = ProductFactory.create()
        start = (fake.date_object() + BDay(0)).date()
        end = (start + BDay(1)).date()

        (
            i1,
            management_fees_1,
            performance_fees_1,
            performance_crys_fees_1,
            management_rebate_1,
            performance_rebate_1,
        ) = _create_fixture(product_1, start)
        (
            i2,
            management_fees_2,
            performance_fees_2,
            performance_crys_fees_2,
            management_rebate_2,
            performance_rebate_2,
        ) = _create_fixture(product_2, start, outstanding_shares=1000)
        total_aum = 100 * 100 + 100 * 1000
        calculator = MarginalityCalculator(Product.objects.filter(id__in=[product_1.id, product_2.id]), start, end)
        assert calculator.get_aggregated_net_marginality("management") == pytest.approx(
            ((management_fees_1 + management_fees_2) - (management_rebate_1 + management_rebate_2)) / total_aum * 360,
            rel=1e-4,
        )

    def test_rebate_marginality_view(self, marginality_calculator, super_user):
        request = APIRequestFactory().get("")
        request.query_params = {}
        request.GET = {"date_gte": self.start.strftime("%Y-%m-%d"), "date_lte": self.end.strftime("%Y-%m-%d")}
        request.user = super_user
        viewset = RebateProductMarginalityViewSet(request=request)
        assert set(viewset._get_dataframe().columns) == {
            "id",
            "title",
            "currency_symbol",
            "base_management_fees_percent",
            "management_fees",
            "management_rebates",
            "management_marginality",
            "management_marginality_percent",
            "base_performance_fees_percent",
            "performance_fees",
            "performance_rebates",
            "performance_marginality",
            "total_fees",
            "total_rebates",
            "total_marginality_percent",
            "total_fees_usd",
            "total_rebates_usd",
            "total_marginality_usd",
            "net_management_marginality",
            "net_performance_marginality",
        }

        # regression tests to check that without date range the view doesn't break
        url = reverse("wbcommission:rebatemarginalitytable-list", args=[])
        api_client = APIClient()
        api_client.force_authenticate(super_user)

        response = api_client.options(url)
        assert response.status_code == 200

        response = api_client.get(url)
        assert response.status_code == 200

        # check that with proper date range the viewset return some content
        response = api_client.options(url, data=request.GET)
        assert response.status_code == 200

        response = api_client.get(url, data=request.GET)
        assert response.status_code == 200
        assert response.json()["results"]
