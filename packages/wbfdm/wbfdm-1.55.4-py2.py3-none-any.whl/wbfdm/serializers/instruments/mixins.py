from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers


class InstrumentAdditionalResourcesMixin:
    @wb_serializers.register_only_instance_resource()
    def instrument_resources(self, instance, request, user, **kwargs):
        additional_resources = dict()

        if instance.prices.exists():
            additional_resources["instrumentpricestatisticchart"] = reverse(
                "wbfdm:instrument-pricestatisticchart-list",
                args=[instance.id],
                request=request,
            )
            additional_resources["instrumentprices"] = reverse(
                "wbfdm:instrument-price-list",
                args=[instance.id],
                request=request,
            )

        additional_resources["distributionreturnschart"] = reverse(
            "wbfdm:instrument-distributionreturnschart-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["bestandworstreturns"] = reverse(
            "wbfdm:instrument-bestandworstreturns-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["price_and_volume"] = (
            f'{reverse("wbfdm:market_data-list", args=[instance.id], request=request)}?chart_type=close&indicators=sma_50,sma_100&volume=true'
        )

        additional_resources["classifications_list"] = reverse(
            "wbfdm:instrument-classification-list",
            args=[instance.get_root().id],
            request=request,
        )
        additional_resources["instrument_lists"] = reverse(
            "wbfdm:instrument-instrumentlistthrough-list", args=[instance.id], request=request
        )

        return additional_resources

    @wb_serializers.register_only_instance_resource()
    def related_instruments(self, instance, request, user, **kwargs):
        return {
            "related_instruments": reverse(
                "wbfdm:instrument-relatedinstrument-list", args=[instance.id], request=request
            )
        }

    # @wb_serializers.register_only_instance_resource()
    # def deprecated_financial_resources(self, instance, request, user, **kwargs):
    #     additional_resources = dict()
    #     additional_resources["summary_table"] = reverse(
    #         "wbfdm:instrument-summarytablechart-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     additional_resources["financials_graph"] = reverse(
    #         "wbfdm:instrument-financialsgraphchart-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     additional_resources["profitability_ratios"] = reverse(
    #         "wbfdm:instrument-profitabilityratioschart-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     additional_resources["cash_flow_analysis_table"] = reverse(
    #         "wbfdm:instrument-cashflowanalysistablechart-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     additional_resources["cash_flow_analysis_chart"] = reverse(
    #         "wbfdm:instrument-cashflowanalysisbarchart-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     additional_resources["net_debt_and_ebitda_chart"] = reverse(
    #         "wbfdm:instrument-netdebtandebitdachart-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     earnings_base_url = reverse(
    #         "wbfdm:instrument-earningschart-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     additional_resources["earnings_chart"] = earnings_base_url
    #     additional_resources["earnings_chart_ttm"] = f"{earnings_base_url}?period=TTM"
    #     additional_resources["earnings_chart_ntm"] = f"{earnings_base_url}?period=FTM"
    #     valuation_ratios_base_url = reverse(
    #         "wbfdm:instrument-valuationratios-list",
    #         args=[instance.id],
    #         request=request,
    #     )
    #     additional_resources["valuation_ratios-old"] = valuation_ratios_base_url
    #     additional_resources["valuation_ratios_ranges"] = f"{valuation_ratios_base_url}?ranges=true"
    #     additional_resources["valuation_ratios_related"] = f"{valuation_ratios_base_url}?vs_related=true"
    #     return additional_resources
