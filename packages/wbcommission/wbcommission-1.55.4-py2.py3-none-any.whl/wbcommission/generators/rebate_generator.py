from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from functools import reduce
from typing import Iterable

from django.db.models import QuerySet, Sum
from wbaccounting.generators.base import AbstractBookingEntryGenerator
from wbaccounting.models import BookingEntry
from wbcore.contrib.directory.models import Entry
from wbportfolio.models import Product

from wbcommission.models import Rebate


class RebateGenerator(AbstractBookingEntryGenerator):
    TITLE = "Rebate Generation"

    @staticmethod
    def generate_booking_entries(from_date: date, to_date: date, counterparty: Entry) -> Iterable[BookingEntry]:
        rebates = Rebate.objects.filter(recipient=counterparty, date__gte=from_date, date__lte=to_date)

        for product_id in rebates.distinct("product_id").values_list("product_id", flat=True):
            product = Product.objects.get(id=product_id)

            for rebate_key, rebate_title in (("management", "Management"), ("performance", "Performance")):
                rebate_sum = (
                    rebates.filter(product_id=product_id, commission_type__key=rebate_key)
                    .aggregate(sum=Sum("value"))
                    .get("sum")
                    or 0.0
                )
                if rebate_sum > 0:
                    yield BookingEntry(
                        title=f"{product.name} {product.isin} {rebate_title} Fees",
                        booking_date=date.today(),
                        reference_date=to_date,
                        gross_value=Decimal(-1 * rebate_sum),
                        vat=Decimal(counterparty.entry_accounting_information.vat) or Decimal(0.0),
                        currency=product.currency,
                        counterparty=counterparty,
                        parameters={
                            "from_date": from_date.strftime("%d.%m.%Y"),
                            "to_date": to_date.strftime("%d.%m.%Y"),
                        },
                        backlinks={
                            "comm-rebates": {
                                "title": "Rebates",
                                "reverse": "wbcommission:rebatetable-list",
                                "parameters": {
                                    "date": f'{from_date.strftime("%Y-%m-%d")},{to_date.strftime("%Y-%m-%d")}',
                                    "product": product_id,
                                    "recipient": counterparty.id,
                                    "group_by": "ACCOUNT",
                                },
                            },
                        },
                    )

    @staticmethod
    def _compare(d1: str, d2: str) -> str:
        d1_lb, d1_ub = d1.split(",")
        d2_lb, d2_ub = d2.split(",")

        lb = min(datetime.strptime(d1_lb, "%Y-%m-%d"), datetime.strptime(d2_lb, "%Y-%m-%d"))
        ub = max(datetime.strptime(d1_ub, "%Y-%m-%d"), datetime.strptime(d2_ub, "%Y-%m-%d"))

        return f"{lb.strftime('%Y-%m-%d')},{ub.strftime('%Y-%m-%d')}"

    @staticmethod
    def _merge_key_into_dict(d: dict, key: str, value: dict) -> dict:
        d[key]["title"] = value["title"]
        d[key]["reverse"] = value["reverse"]
        if "recipient" in value["parameters"]:
            d[key]["parameters"]["recipient"] = value["parameters"]["recipient"]
            d[key]["parameters"]["date"] = RebateGenerator._compare(
                d[key]["parameters"].get("date", "9999-12-31,1111-01-01"), value["parameters"]["date"]
            )
        return d

    @staticmethod
    def _iter_backlinks(booking_entries: QuerySet) -> Iterable:
        for backlink in booking_entries:
            yield from backlink.items()

    @staticmethod
    def merge_backlinks(booking_entries: QuerySet[BookingEntry]) -> dict:
        return reduce(
            lambda d, v: RebateGenerator._merge_key_into_dict(d, *v),
            RebateGenerator._iter_backlinks(
                booking_entries.filter(backlinks__isnull=False).values_list("backlinks", flat=True)
            ),
            defaultdict(lambda: dict(parameters=dict())),
        )
