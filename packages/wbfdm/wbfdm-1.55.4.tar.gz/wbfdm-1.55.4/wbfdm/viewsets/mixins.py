from django.utils.functional import cached_property
from rest_framework.generics import get_object_or_404

from wbfdm.models import Instrument


class InstrumentMixin:
    kwargs: dict

    @cached_property
    def instrument(self) -> Instrument:
        return get_object_or_404(Instrument, pk=self.kwargs["instrument_id"])
