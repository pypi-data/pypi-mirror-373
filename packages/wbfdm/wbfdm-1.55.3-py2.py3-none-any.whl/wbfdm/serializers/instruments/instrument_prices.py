from wbcore import serializers as wb_serializers

from wbfdm.models import InstrumentPrice
from wbfdm.serializers.instruments.instruments import (
    InvestableInstrumentRepresentationSerializer,
)


class InstrumentPriceModelSerializer(wb_serializers.ModelSerializer):
    _instrument = InvestableInstrumentRepresentationSerializer(source="instrument")
    currency_symbol = wb_serializers.CharField(read_only=True)
    net_value = wb_serializers.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_value_usd = wb_serializers.DecimalField(max_digits=16, decimal_places=2, default=0)
    gross_value = wb_serializers.DecimalField(max_digits=16, decimal_places=2, default=0)
    daily_diff_net_value = wb_serializers.FloatField(required=False, read_only=True, default=0, precision=4)
    daily_diff_gross_value = wb_serializers.FloatField(required=False, read_only=True, default=0, precision=4)
    real_price_exists = wb_serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = InstrumentPrice
        percent_fields = [
            "daily_diff_net_value",
            "daily_diff_gross_value",
        ]
        decorators = {
            "market_capitalization": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
        }
        fields = (
            "id",
            "date",
            "net_value",
            "net_value_usd",
            "gross_value",
            "calculated",
            "real_price_exists",
            "sharpe_ratio",
            "correlation",
            "beta",
            "daily_diff_net_value",
            "daily_diff_gross_value",
            "instrument",
            "_instrument",
            "volume",
            "volume_50d",
            "volume_200d",
            "currency_symbol",
            "outstanding_shares_consolidated",
            "market_capitalization",
        )


class InstrumentPriceInstrumentModelSerializer(InstrumentPriceModelSerializer):
    class Meta(InstrumentPriceModelSerializer.Meta):
        fields = (
            "id",
            "date",
            "net_value",
            "net_value_usd",
            "gross_value",
            "sharpe_ratio",
            "calculated",
            "correlation",
            "beta",
            "daily_diff_net_value",
            "daily_diff_gross_value",
            "volume",
            "volume_50d",
            "volume_200d",
            "currency_symbol",
            "outstanding_shares_consolidated",
            "market_capitalization",
        )
