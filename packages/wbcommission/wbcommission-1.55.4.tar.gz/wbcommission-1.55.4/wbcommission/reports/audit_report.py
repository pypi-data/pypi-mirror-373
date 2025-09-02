from datetime import date
from io import BytesIO

import pandas as pd
from celery import shared_task
from wbcore.contrib.authentication.models import User
from wbcore.contrib.directory.models import Entry
from wbcrm.models.accounts import Account
from wbportfolio.models.products import Product

from wbcommission.models import Commission, CommissionType, Rebate

from .utils import create_report_and_send


@shared_task(queue="commission")
def create_audit_report_and_send_as_task(user_id: int, recipient_id: int, start_date: date, end_date: date):
    user = User.objects.get(id=user_id)
    recipient = Entry.objects.get(id=recipient_id)
    create_report_and_send(user, recipient, start_date, end_date, create_report)


def create_report(user, customer, start_date, end_date):
    rebates = Rebate.objects.filter(recipient=customer, date__gte=start_date, date__lte=end_date).filter_for_user(user)
    df = pd.DataFrame(
        rebates.values(
            "date",
            "account",
            "product",
            "recipient",
            "commission_type",
            "commission",
            "value",
            "audit_log",
        )
    )
    buffer = BytesIO()
    if df.empty:
        raise ValueError("There is not rebate for this customer and given time period")
    df = pd.concat([df[df.columns.difference(["audit_log"])], pd.json_normalize(df["audit_log"])], axis=1).sort_values(
        by="date"
    )
    # we deserialize ids into human readable name
    df.commission_type = df.commission_type.map(dict(CommissionType.objects.values_list("id", "name")))
    df["product"] = df["product"].map(dict(Product.objects.values_list("id", "computed_str")))
    df.commission = df.commission.map(
        dict(map(lambda x: (x, str(Commission.objects.get(id=x))), df.commission.unique()))
    )
    df.recipient = df.recipient.map(dict(Entry.objects.values_list("id", "computed_str")))
    df.account = df.account.map(dict(Account.objects.values_list("id", "computed_str")))
    df.to_csv(buffer, index=False, mode="wb", encoding="UTF-8")
    return buffer, "audit_report_{}_{}_{}.csv".format(customer.computed_str, start_date, end_date), "application/csv"
