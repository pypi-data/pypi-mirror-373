from wbcore import serializers as wb_serializers

from wbcommission.models import Rebate


class RebateModelSerializer(wb_serializers.ModelSerializer):
    id = wb_serializers.PrimaryKeyField()
    value_usd = wb_serializers.FloatField(read_only=True)

    class Meta:
        model = Rebate
        fields = ("id", "value_usd")


class RebateProductMarginalitySerializer(wb_serializers.Serializer):
    id = wb_serializers.PrimaryKeyField()
    title = wb_serializers.CharField(read_only=True)
    currency_symbol = wb_serializers.CharField(read_only=True)
    sum_management_fees = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Management Fees")
    sum_performance_fees = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Management Rebates")
    sum_crystalized_performance_fees = wb_serializers.DecimalField(
        max_digits=16, decimal_places=2, label="Crystalized Performance Fees"
    )
    sum_management_rebates = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Performance Fees")
    sum_performance_rebates = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Performance Rebates")
    marginality_management = wb_serializers.DecimalField(
        max_digits=16, decimal_places=2, label="Marginality Management"
    )
    marginality_performance = wb_serializers.DecimalField(
        max_digits=16, decimal_places=2, label="Marginality Performance"
    )

    total_fees = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Total Fees")
    total_rebates = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Total Rebates")
    total_marginality = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Total Marginality")

    total_fees_usd = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Total Fees (USD)")
    total_rebates_usd = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Total Rebates (USD)")
    total_usd = wb_serializers.DecimalField(max_digits=16, decimal_places=2, label="Total Net (USD)")

    class Meta:
        percent_fields = [
            "marginality_management",
            "marginality_performance",
            "total_marginality",
        ]
        decorators = {
            "sum_management_fees": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
            "sum_performance_fees": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
            "sum_management_rebates": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
            "sum_performance_rebates": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
            "total_fees": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
            "total_rebates": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
            "total_fees_usd": wb_serializers.decorator(decorator_type="text", position="left", value="$"),
            "total_rebates_usd": wb_serializers.decorator(decorator_type="text", position="left", value="$"),
        }

        fields = (
            "id",
            "title",
            "currency_symbol",
            "sum_management_fees",
            "sum_performance_fees",
            "sum_crystalized_performance_fees",
            "sum_management_rebates",
            "sum_performance_rebates",
            "marginality_management",
            "marginality_performance",
            "total_fees",
            "total_rebates",
            "total_marginality",
            "total_fees_usd",
            "total_rebates_usd",
            "total_usd",
        )
        read_only_fields = fields
