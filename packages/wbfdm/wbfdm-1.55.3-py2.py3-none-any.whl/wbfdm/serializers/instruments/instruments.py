from typing import TYPE_CHECKING, Type

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.geography.models import Geography
from wbcore.contrib.geography.serializers import CountryRepresentationSerializer
from wbcore.contrib.tags.serializers import TagRepresentationSerializer

from wbfdm.models import Instrument, InstrumentType

from ..exchanges import ExchangeRepresentationSerializer
from .classifications import ClassificationRepresentationSerializer
from .mixins import InstrumentAdditionalResourcesMixin

if TYPE_CHECKING:
    User = Type[get_user_model()]


class InstrumentTypeRepresentationSerializer(serializers.RepresentationSerializer):
    class Meta:
        model = InstrumentType
        fields = ("id", "name", "key")


class InstrumentRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbfdm:instrument-detail")

    def get_filter_params(self, request):
        filter_params = {}
        if (view := request.parser_context.get("view", None)) and (
            classification_id := view.kwargs.get("classification_id", None)
        ):
            filter_params["classifications_neq"] = classification_id

        return filter_params

    class Meta:
        model = Instrument
        fields = ("id", "name", "ticker", "isin", "computed_str", "_detail")


class ClassifiableInstrumentRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["instrument_type__is_classifiable"] = True
        filter_params["level"] = 0
        return filter_params


class CompanyRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["level"] = 0
        return filter_params


class SecurityRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["is_security"] = True
        return filter_params


class InvestableUniverseRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["is_investable_universe"] = True
        return filter_params


class InvestableInstrumentRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["is_investable"] = True
        return filter_params


class PrimaryInvestableInstrumentRepresentationSerializer(InvestableInstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["is_primary"] = True
        return filter_params


class ManagedInstrumentRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["is_managed"] = True
        return filter_params


class EquityRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["instrument_type__key"] = "equity"
        return filter_params


class ProductRepresentationSerializer(InstrumentRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = super().get_filter_params(request)
        filter_params["instrument_type__key"] = "product"
        return filter_params


class InstrumentModelListSerializer(
    serializers.ModelSerializer,
):
    _currency = CurrencyRepresentationSerializer(source="currency")
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())
    currency_symbol = serializers.CharField(read_only=True)
    _exchange = ExchangeRepresentationSerializer(source="exchange")
    country = serializers.PrimaryKeyRelatedField(queryset=Geography.countries.all())
    _country = CountryRepresentationSerializer(source="country")
    instrument_type = serializers.PrimaryKeyRelatedField(queryset=InstrumentType.objects.all())
    _instrument_type = InstrumentTypeRepresentationSerializer(source="instrument_type")
    _tags = TagRepresentationSerializer(many=True, source="tags")

    _classifications = ClassificationRepresentationSerializer(
        source="classifications", many=True, label_key="{{ name }}"
    )
    _parent = InstrumentRepresentationSerializer(source="parent")
    is_active = serializers.BooleanField(default=True, read_only=True)
    is_cash = serializers.BooleanField(default=False, read_only=True)
    _group_key = serializers.CharField(read_only=True)

    class Meta:
        model = Instrument
        read_only_fields = (
            "name",
            "exchange",
            "computed_str",
            "instrument_type",
            "old_isins",
            "inception_date",
            "country",
            "is_active",
            "parent",
            "is_primary",
            "is_investable_universe",
            "is_security",
            "is_managed",
        )

        fields = (
            "id",
            "name",
            "name_repr",
            "description",
            "instrument_type",
            "_instrument_type",
            "inception_date",
            "delisted_date",
            "country",
            "_country",
            "currency",
            "_currency",
            "currency_symbol",
            "isin",
            "refinitiv_identifier_code",
            "refinitiv_mnemonic_code",
            "ticker",
            "_classifications",
            "classifications",
            "_tags",
            "tags",
            "is_active",
            "is_cash",
            "_parent",
            "parent",
            "_additional_resources",
            "_buttons",
            "_group_key",
            "exchange",
            "_exchange",
            "is_primary",
            "is_investable_universe",
            "is_security",
            "is_managed",
        )


class InstrumentModelSerializer(InstrumentAdditionalResourcesMixin, InstrumentModelListSerializer):
    _related_instruments = SecurityRepresentationSerializer(source="related_instruments", many=True)

    @serializers.register_resource()
    def load_resources(self, instance, request, user, **kwargs):
        res = {
            "prices": reverse("wbfdm:prices-list", args=[instance.id], request=request),
            "financial-statistics": reverse(
                "wbfdm:instrument-financialstatistics-list", args=[instance.id], request=request
            ),
        }
        if not instance.is_managed:
            res.update(
                {
                    "fin-summary": reverse("wbfdm:financial-summary-list", args=[instance.id], request=request),
                    "swe-income-statement": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "income"], request=request
                    ),
                    "swe-balance-sheet": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "balancesheet"], request=request
                    ),
                    "swe-cashflow-statement": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "cashflow"], request=request
                    ),
                    "swe-ratios": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "ratios"], request=request
                    ),
                    "swe-margins": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "margins"], request=request
                    ),
                    "swe-summary": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "summary"], request=request
                    ),
                    "swe-cashflow-ratios": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "cashflow-ratios"], request=request
                    ),
                    "swe-asset-turnover-ratios": reverse(
                        "wbfdm:statementwithestimates-list",
                        args=[instance.id, "asset-turnover-ratios"],
                        request=request,
                    ),
                    "swe-credit": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "credit"], request=request
                    ),
                    "swe-long-term-solvency": reverse(
                        "wbfdm:statementwithestimates-list", args=[instance.id, "long-term-solvency"], request=request
                    ),
                    "swe-short-term-liquidity": reverse(
                        "wbfdm:statementwithestimates-list",
                        args=[instance.id, "short-term-liquidity"],
                        request=request,
                    ),
                    "valuation_ratios-new": reverse(
                        "wbfdm:valuation_ratios-list", args=[instance.id], request=request
                    ),
                    "income-statement": reverse(
                        "wbfdm:statement-list", args=[instance.id, "income-statement"], request=request
                    ),
                    "balance-sheet": reverse(
                        "wbfdm:statement-list", args=[instance.id, "balance-sheet"], request=request
                    ),
                    "cash-flow-statement": reverse(
                        "wbfdm:statement-list", args=[instance.id, "cash-flow-statement"], request=request
                    ),
                    "officers": reverse(viewname="wbfdm:officers-list", args=[instance.id], request=request),
                    "controversies": reverse(viewname="wbfdm:controversies-list", args=[instance.id], request=request),
                    "pai": reverse(viewname="wbfdm:pai-list", args=[instance.id], request=request),
                }
            )
        return res

    @serializers.register_only_instance_resource()
    def instance_resource(self, instance, request, user, **kwargs):
        content_type = ContentType.objects.get_for_model(instance)
        return {
            "children": reverse("wbfdm:instrument-children-list", args=[instance.id], request=request),
            "news": f'{reverse("wbnews:newsrelationship-list", args=[], request=request)}?content_type={content_type.id}&object_id={instance.id}',
        }

    @serializers.register_resource()
    def register_market_data(self, instance, request, user, **kwargs):
        return {
            "market_data": reverse("wbfdm:market_data-list", args=[instance.id], request=request),
            "cumulativereturn": f'{reverse("wbfdm:market_data-list", args=[instance.id], request=request)}?chart_type=ret',
            "drawdown": f'{reverse("wbfdm:market_data-list", args=[instance.id], request=request)}?chart_type=drawdown',
            "performance_summary": reverse("wbfdm:performance_summary-list", args=[instance.id], request=request),
            "monthly_performances": reverse("wbfdm:monthly_performances-list", args=[instance.id], request=request),
        }

    class Meta(InstrumentModelListSerializer.Meta):
        fields = InstrumentModelListSerializer.Meta.fields + (
            "refinitiv_mnemonic_code",
            "identifier",
            "base_color",
            "old_isins",
            "is_cash",
            "related_instruments",
            "_related_instruments",
        )
