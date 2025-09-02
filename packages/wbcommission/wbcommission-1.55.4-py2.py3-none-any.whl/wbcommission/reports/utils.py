from contextlib import suppress
from datetime import date

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from wbcore.contrib.authentication.models import User
from wbcore.contrib.directory.models import Entry
from wbcore.utils.html import convert_html2text

AccountCustomer = None


def create_report_and_send(user: User, customer: Entry, start_date: date, end_date: date, report_callback):
    with suppress(ValueError):
        report_stream, file_name, file_extension = report_callback(user, customer, start_date, end_date)

        html = get_template("portfolio/email/customer_report.html")

        context = {"profile": user, "customer": customer}
        html_content = html.render(context)

        msg = EmailMultiAlternatives("Report", body=convert_html2text(html_content), to=[user.email])
        msg.attach_alternative(html_content, "text/html")
        report_stream.seek(0)
        msg.attach(
            file_name,
            report_stream.read(),
            file_extension,
        )
        msg.send()
