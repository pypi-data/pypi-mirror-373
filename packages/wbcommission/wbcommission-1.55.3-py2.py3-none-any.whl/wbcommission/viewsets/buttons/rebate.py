from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.utils.date import current_quarter_date_start
from wbcrm.models.accounts import Account
from wbcrm.serializers.accounts import AccountRepresentationSerializer


class RebateTableButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        class RecomputeRebateSerializer(wb_serializers.Serializer):
            start_date = wb_serializers.DateField(label=_("Start"), default=current_quarter_date_start)
            only_accounts = wb_serializers.PrimaryKeyRelatedField(queryset=Account.objects.filter(level=0))
            _only_accounts = AccountRepresentationSerializer(
                source="only_accounts", filter_params={"level": 0}, many=True
            )
            prune_existing = wb_serializers.BooleanField(
                default=False,
                help_text="If true, existing rebate for the specified accounts and start date will be deleted before regenerated. Usually necessary if commission rule were lowered or claim removed from account",
            )

        if self.request.user.has_perm("wbcommission.administrate_commission"):
            return {
                bt.ActionButton(
                    method=RequestType.PATCH,
                    identifiers=("wbcommission:rebates",),
                    action_label="Trigger Rebate computation",
                    endpoint=reverse("wbcommission:rebate-recompute", args=[], request=self.request),
                    description_fields="<p>Trigger Rebate computation</p>",
                    serializer=RecomputeRebateSerializer,
                    icon=WBIcon.REGENERATE.icon,
                    title="Trigger Rebate computation",
                    label="Trigger Rebate computation",
                    instance_display=create_simple_display(
                        [["start_date", "prune_existing"], ["only_accounts", "only_accounts"]]
                    ),
                ),
            }
        return {}
