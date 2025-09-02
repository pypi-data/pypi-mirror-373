from django.dispatch import receiver
from wbcore.contrib.directory.viewsets import (
    CompanyModelViewSet,
    EntryModelViewSet,
    PersonModelViewSet,
)
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.signals.instance_buttons import add_instance_button
from wbcore.utils.serializers import StartEndDateSerializer


@receiver(add_instance_button, sender=PersonModelViewSet)
@receiver(add_instance_button, sender=EntryModelViewSet)
@receiver(add_instance_button, sender=CompanyModelViewSet)
def crm_adding_instance_buttons(sender, many, *args, **kwargs):
    if many:
        return
    return bt.DropDownButton(
        label="Commission",
        icon=WBIcon.UNFOLD.icon,
        buttons=(
            bt.WidgetButton(key="rebates", label="Rebates", icon=WBIcon.DEAL_MONEY.icon),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcommission:rebates",),
                action_label="Send Customer Report",
                key="generate_customer_commission_report",
                description_fields="<p>Generate Commission Report</p>",
                serializer=StartEndDateSerializer,
                icon=WBIcon.CHART_SWITCHES.icon,
                title="Generate Commission reports",
                label="Generate Commission reports",
                instance_display=create_simple_display([["start"], ["end"]]),
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcommission:rebates",),
                action_label="Send Audit Report",
                key="generate_audit_commission_report",
                description_fields="<p>Generate Audit Commission Report</p>",
                serializer=StartEndDateSerializer,
                icon=WBIcon.NOTEBOOK.icon,
                title="Generate Audit Commission reports",
                label="Generate Audit Commission reports",
                instance_display=create_simple_display([["start"], ["end"]]),
            ),
        ),
    )
