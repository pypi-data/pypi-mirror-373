from wbcore import serializers as wb_serializers

from wbcommission.models import CommissionType


class CommissionTypeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcommission:commissiontype-detail")

    class Meta:
        model = CommissionType
        fields = (
            "id",
            "name",
            "key",
            "_detail",
        )


class CommissionTypeModelSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = CommissionType
        read_only_fields = ("key",)
        fields = (
            "id",
            "name",
            "key",
        )
