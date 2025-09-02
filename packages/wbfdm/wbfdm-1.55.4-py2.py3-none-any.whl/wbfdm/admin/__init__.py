from django.contrib import admin

from .instruments import InstrumentModelAdmin, InstrumentTypeModelAdmin
from .classifications import ClassificationAdmin, ClassificationGroupAdmin
from .exchanges import ExchangeModelAdmin
from .instrument_lists import InstrumentListAdmin
from .instruments_relationships import InstrumentFavoriteGroupModelAdmin
from .esg import ControversyModelAdmin
from .exchanges import ExchangeModelAdmin
from .instrument_prices import InstrumentPriceAdmin
from .instrument_requests import InstrumentRequestModelAdmin
from .options import OptionModelAdmin, OptionAggregateModelAdmin


class ReadOnlyAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return (
            list(self.readonly_fields)
            + [field.name for field in obj._meta.fields]  # type: ignore
            + [field.name for field in obj._meta.many_to_many]  # type: ignore
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyTabularInline(admin.TabularInline):
    show_change_link = True

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
