from django.dispatch import receiver
from rest_framework.reverse import reverse
from wbcore.contrib.directory.serializers import (
    CompanyModelSerializer,
    EntryModelSerializer,
    PersonModelSerializer,
)
from wbcore.filters.defaults import current_quarter_date_end, current_quarter_date_start
from wbcore.signals import add_instance_additional_resource


# register the rebate and generate report addition resources to the entry model serializers
@receiver(add_instance_additional_resource, sender=CompanyModelSerializer)
@receiver(add_instance_additional_resource, sender=PersonModelSerializer)
@receiver(add_instance_additional_resource, sender=EntryModelSerializer)
def commission_adding_additional_resource(sender, serializer, instance, request, user, **kwargs):
    start = current_quarter_date_start()
    end = current_quarter_date_end()
    res = {
        "rebates": f'{reverse("wbcommission:rebatetable-list", args=[], request=request)}?group_by=PRODUCT&recipient={instance.id}&date={start:%Y-%m-%d},{end:%Y-%m-%d}',
        "generate_customer_commission_report": f'{reverse("wbcommission:rebate-customerreport", request=request)}?recipient_id={instance.id}',
    }
    if user.has_perm("wbcommission.administrate_commission"):
        res["generate_audit_commission_report"] = (
            f'{reverse("wbcommission:rebate-auditreport", request=request)}?recipient_id={instance.id}'
        )
    return res
