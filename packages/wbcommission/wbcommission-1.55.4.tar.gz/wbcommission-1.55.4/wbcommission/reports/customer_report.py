from datetime import date
from decimal import Decimal
from io import BytesIO

import xlsxwriter
from celery import shared_task
from django.db.models import Case, F, Sum, When
from wbcore.contrib.authentication.models import User
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import Entry
from wbcrm.models.accounts import (
    Account,
    AccountRole,
    AccountRoleType,
    AccountRoleValidity,
)
from wbfdm.models import InstrumentPrice
from wbportfolio.models.transactions.claim import Claim
from xlsxwriter.utility import xl_rowcol_to_cell

from wbcommission.models import CommissionType, Rebate

from .utils import create_report_and_send

AccountCustomer = None


@shared_task(queue="commission")
def create_customer_report_and_send_as_task(user_id: int, recipient_id: int, start_date: date, end_date: date):
    user = User.objects.get(id=user_id)
    recipient = Entry.objects.get(id=recipient_id)
    create_report_and_send(user, recipient, start_date, end_date, create_report)


def create_report(user, customer, start_date, end_date):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    base_format = workbook.add_format({"font_name": "Liberation Sans", "font_size": 10})
    bold_format = workbook.add_format({"font_name": "Liberation Sans", "font_size": 10, "bold": True})
    decimal_format = workbook.add_format({"font_name": "Liberation Sans", "font_size": 10, "num_format": "#,##.00"})
    bold_decimal_format = workbook.add_format(
        {"font_name": "Liberation Sans", "font_size": 10, "num_format": "#,##.00", "bold": True}
    )
    percent_format = workbook.add_format({"font_name": "Liberation Sans", "font_size": 10, "num_format": "#,##.00 %"})
    bold_percent_format = workbook.add_format(
        {"font_name": "Liberation Sans", "font_size": 10, "num_format": "#,##.00 %", "bold": True}
    )

    # HERE STARTS THE FIRST WORKSHEET
    worksheet_products = workbook.add_worksheet(f"Products ({end_date:%d.%m.%Y})")

    worksheet_products.write_string(0, 0, "Product", bold_format)
    worksheet_products.write_string(0, 1, "Currency", bold_format)
    worksheet_products.write_string(0, 2, "Price", bold_format)
    worksheet_products.write_string(0, 3, "Price USD", bold_format)
    worksheet_products.write_string(0, 4, "Direct Assets", bold_format)
    worksheet_products.write_string(0, 5, "Direct Assets USD", bold_format)
    worksheet_products.write_string(0, 6, "Indirect Assets", bold_format)
    worksheet_products.write_string(0, 7, "Indirect Assets USD", bold_format)
    worksheet_products.write_string(0, 8, "Total Assets USD", bold_format)

    worksheet_products.write_formula(1, 5, "=SUM(F4:F99999)", bold_decimal_format)
    worksheet_products.write_formula(1, 7, "=SUM(H4:H99999)", bold_decimal_format)
    worksheet_products.write_formula(1, 8, "=SUM(I4:I99999)", bold_decimal_format)

    fx_rates = CurrencyFXRates.get_fx_rates_subquery(end_date)
    customer_accounts = Account.get_accounts_for_customer(customer)
    valid_customer_roles = (
        AccountRole.objects.filter(entry=customer)
        .annotate(is_currently_valid=AccountRoleValidity.get_role_validity_subquery(date.today()))
        .filter(is_currently_valid=True)
    )
    account_types = AccountRoleType.objects.filter(id__in=valid_customer_roles.values("role_type"))

    user_claims = Claim.objects.filter_for_customer(customer, include_related_roles=True).filter_for_user(
        user, validity_date=date.today()
    )
    products = (
        user_claims.filter(
            date__lte=end_date,
            status=Claim.Status.APPROVED,
        )
        .annotate(
            owner_asset_shares=Case(When(account__in=customer_accounts, then=F("shares")), default=Decimal(0)),
            **{
                f"{account_type.key}_assets_shares": Case(
                    When(
                        account__in=valid_customer_roles.filter(role_type=account_type).values("account"),
                        then=F("shares"),
                    ),
                    default=Decimal(0),
                )
                for account_type in account_types
            },
        )
        .values("product")
        .annotate(
            price=InstrumentPrice.subquery_closest_value(
                "net_value", val_date=end_date, instrument_pk_name="product__pk"
            ),
            product_id=F("product_id"),
            title=F("product__name"),
            currency=F("product__currency__symbol"),
            sum_shares=Sum("shares"),
            fx_rate=fx_rates,
            sum_owner_assets_shares=Sum("owner_asset_shares"),
            **{
                f"sum_{account_type.key}_assets_shares": Sum(f"{account_type.key}_assets_shares")
                for account_type in account_types
            },
        )
        .order_by("title")
    )
    for row, product in enumerate(products, start=3):
        product_cell = xl_rowcol_to_cell(row, 0)
        currency_cell = xl_rowcol_to_cell(row, 1)
        price_cell = xl_rowcol_to_cell(row, 2)
        price_usd_cell = xl_rowcol_to_cell(row, 3)
        owner_assets_cell = xl_rowcol_to_cell(row, 4)
        owner_assets_usd_cell = xl_rowcol_to_cell(row, 5)
        account_role_cells = dict()
        account_role_cells_usd = dict()
        index = 6
        for account_type in account_types:
            account_role_cells[account_type.key] = xl_rowcol_to_cell(row, index)
            account_role_cells_usd[account_type.key] = xl_rowcol_to_cell(row, index + 1)
            index += 2
        total_assets_usd_cell = xl_rowcol_to_cell(row, index)

        worksheet_products.write_string(product_cell, product["title"], base_format)
        worksheet_products.write_string(currency_cell, product["currency"], base_format)
        worksheet_products.write_number(price_cell, product["price"], decimal_format)
        worksheet_products.write_formula(price_usd_cell, f"{price_cell} * {product['fx_rate']}", decimal_format)

        worksheet_products.write_formula(
            owner_assets_cell, f"{product['sum_owner_assets_shares']} * {price_cell}", decimal_format
        )
        worksheet_products.write_formula(
            owner_assets_usd_cell, f"{owner_assets_cell} * {product['fx_rate']}", decimal_format
        )

        for account_type in account_types:
            worksheet_products.write_formula(
                account_role_cells[account_type.key],
                f"{product[f'sum_{account_type.key}_assets_shares']} * {price_cell}",
                decimal_format,
            )
            worksheet_products.write_formula(
                account_role_cells_usd[account_type.key],
                f"{account_role_cells[account_type.key]} * {product['fx_rate']}",
                decimal_format,
            )
        worksheet_products.write_formula(
            total_assets_usd_cell,
            " + ".join([owner_assets_usd_cell] + list(account_role_cells_usd.values())),
            decimal_format,
        )

    # HERE STARTS THE SECOND WORKSHEET
    worksheet_trade_performance = workbook.add_worksheet(f"Trades ({end_date:%d.%m.%Y})")

    worksheet_trade_performance.write_string(0, 0, "Trade Date", bold_format)
    worksheet_trade_performance.write_string(0, 1, "Shares", bold_format)
    worksheet_trade_performance.write_string(0, 2, "Bank", bold_format)
    worksheet_trade_performance.write_string(0, 3, "Root Account", bold_format)
    worksheet_trade_performance.write_string(0, 4, "Account", bold_format)
    worksheet_trade_performance.write_string(0, 5, "Product", bold_format)
    worksheet_trade_performance.write_string(0, 6, "Price (Trade Date)", bold_format)
    worksheet_trade_performance.write_string(0, 7, "Net Value (Trade Date)", bold_format)
    worksheet_trade_performance.write_string(0, 8, "Net Value (Trade Date) USD", bold_format)
    worksheet_trade_performance.write_string(0, 9, f"Price ({end_date:%d.%m.%Y})", bold_format)
    worksheet_trade_performance.write_string(0, 10, f"Net Value ({end_date:%d.%m.%Y})", bold_format)
    worksheet_trade_performance.write_string(0, 11, f"Net Value ({end_date:%d.%m.%Y}) USD", bold_format)
    worksheet_trade_performance.write_string(0, 12, "Performance", bold_format)

    worksheet_trade_performance.write_formula(1, 8, "=SUM(I4:I99999)", bold_decimal_format)
    worksheet_trade_performance.write_formula(1, 11, "=SUM(L4:L99999)", bold_decimal_format)
    worksheet_trade_performance.write_formula(1, 12, "=(L2/I2)-1", bold_percent_format)

    fx_rates_date = CurrencyFXRates.get_fx_rates_subquery("date")

    fx_rates_end = CurrencyFXRates.get_fx_rates_subquery(end_date)

    claims = (
        user_claims.filter(
            date__lte=end_date,
            status=Claim.Status.APPROVED,
        )
        .annotate(
            price_date=InstrumentPrice.subquery_closest_value("net_value", instrument_pk_name="product__pk"),
            price_end=InstrumentPrice.subquery_closest_value(
                "net_value", val_date=end_date, instrument_pk_name="product__pk"
            ),
            fx_rates_date=fx_rates_date,
            fx_rates_end=fx_rates_end,
        )
        .order_by("date")
    ).select_related("product", "account")

    for row, claim in enumerate(claims, start=3):
        trade_date_cell = xl_rowcol_to_cell(row, 0)
        shares_cell = xl_rowcol_to_cell(row, 1)
        bank_cell = xl_rowcol_to_cell(row, 2)
        root_account_cell = xl_rowcol_to_cell(row, 3)
        account_cell = xl_rowcol_to_cell(row, 4)
        product_cell = xl_rowcol_to_cell(row, 5)
        price_trade_cell = xl_rowcol_to_cell(row, 6)
        net_value_trade_cell = xl_rowcol_to_cell(row, 7)
        net_value_usd_trade_cell = xl_rowcol_to_cell(row, 8)
        price_end_cell = xl_rowcol_to_cell(row, 9)
        net_value_end_cell = xl_rowcol_to_cell(row, 10)
        net_value_usd_end_cell = xl_rowcol_to_cell(row, 11)
        performance_cell = xl_rowcol_to_cell(row, 12)

        worksheet_trade_performance.write_string(trade_date_cell, f"{claim.date:%d.%m.%Y}", base_format)
        worksheet_trade_performance.write_number(shares_cell, claim.shares, decimal_format)
        worksheet_trade_performance.write_string(bank_cell, claim.bank, base_format)
        worksheet_trade_performance.write_string(root_account_cell, claim.account.get_root().title, base_format)
        worksheet_trade_performance.write_string(account_cell, str(claim.account), base_format)
        worksheet_trade_performance.write_string(product_cell, claim.product.title, base_format)

        worksheet_trade_performance.write_number(
            price_trade_cell, claim.price_date or claim.product.share_price, decimal_format
        )
        worksheet_trade_performance.write_formula(
            net_value_trade_cell, f"={shares_cell}*{price_trade_cell}", decimal_format
        )
        worksheet_trade_performance.write_formula(
            net_value_usd_trade_cell, f"={net_value_trade_cell}*{claim.fx_rates_date}", decimal_format
        )

        worksheet_trade_performance.write_number(price_end_cell, claim.price_end, decimal_format)
        worksheet_trade_performance.write_formula(
            net_value_end_cell, f"={shares_cell}*{price_end_cell}", decimal_format
        )
        worksheet_trade_performance.write_formula(
            net_value_usd_end_cell, f"={net_value_end_cell}*{claim.fx_rates_end}", decimal_format
        )

        worksheet_trade_performance.write_formula(
            performance_cell, f"=({net_value_usd_end_cell}/{net_value_usd_trade_cell})-1", percent_format
        )

    # HERE STARTS THE THIRD WORKSHEET
    worksheet_rebates = workbook.add_worksheet(f"Rebates ({start_date:%d.%m.%Y}-{end_date:%d.%m.%Y})")

    worksheet_rebates.write_string(0, 0, "Date", bold_format)
    worksheet_rebates.write_string(0, 1, "Product", bold_format)
    worksheet_rebates.write_string(0, 2, "Account", bold_format)
    for index, commission_type in enumerate(CommissionType.objects.all()):
        worksheet_rebates.write_string(0, index + 3, f"{commission_type.name.title()} Fees", bold_format)
        worksheet_rebates.write_formula(
            1, index + 3, f"=SUM({chr(ord('@') + (index + 3))}3]:E99999)", bold_decimal_format
        )

    rebates_for_user = Rebate.objects.filter_for_user(user, validity_date=date.today())
    rebates = (
        rebates_for_user.filter(recipient=customer, date__gte=start_date, date__lte=end_date)
        .select_related("account", "product")
        .annotate(
            **{
                f"{commission_type.key}__value": Case(
                    When(commission_type=commission_type, then=F("value")), default=Decimal(0)
                )
                for commission_type in CommissionType.objects.all()
            }
        )
        .values("date", "account", "product")
        .annotate(
            product_title=F("product__name"),
            account_id=F("account__id"),
            account_title=F("account__computed_str"),
            **{
                f"sum_{commission_type.key}_value": Sum(f"{commission_type.key}__value")
                for commission_type in CommissionType.objects.all()
            },
        )
        .order_by("date", "product", "account_id")
    )

    for row, rebate in enumerate(rebates, start=4):
        date_cell = xl_rowcol_to_cell(row, 0)
        product_cell = xl_rowcol_to_cell(row, 1)
        account_cell = xl_rowcol_to_cell(row, 2)

        worksheet_rebates.write_string(date_cell, f"{rebate['date']:%d.%m.%Y}", base_format)
        worksheet_rebates.write_string(product_cell, rebate["product_title"], base_format)
        worksheet_rebates.write_string(account_cell, rebate["account_title"], base_format)
        for index, commission_type in enumerate(CommissionType.objects.all()):
            cell = xl_rowcol_to_cell(row, 3 + index)
            worksheet_rebates.write_number(cell, rebate[f"sum_{commission_type.key}_value"], decimal_format)

    workbook.close()
    output.seek(0)
    return (
        output,
        "customer_report_{}_{}_{}.xlsx".format(customer.computed_str, start_date, end_date),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
