from django.db.models import Q, QuerySet

from wbfdm.models import Instrument
from wbfdm.sync.abstract import Sync


class MsciInstrumentSync(Sync[Instrument]):
    ESG_PATH = "wbfdm.contrib.msci.dataloaders.esg.MSCIESGDataloader"
    ESG_CONTROVERSY_PATH = "wbfdm.contrib.msci.dataloaders.esg_controversies.MSCIESGControversyDataloader"

    def get_updatable_instruments(self) -> QuerySet[Instrument]:
        return Instrument.objects.filter(
            Q(isin__isnull=False)
            & (Q(dl_parameters__esg__isnull=True) | Q(dl_parameters__esg_controversies__isnull=True))
        )

    def update(self):
        instruments = []

        for instrument in self.get_updatable_instruments():
            self._update_dl_parameters(instrument)
            instruments.append(instrument)

            if len(instruments) % 10000 == 0:
                Instrument.objects.bulk_update(instruments, ["dl_parameters"])
                instruments = []
        Instrument.objects.bulk_update(instruments, ["dl_parameters"])

    def update_or_create_item(self, external_id: int) -> Instrument:
        raise NotImplementedError(f"The {__class__} is not allowed to create instruments")

    def get_item(self, external_id: int) -> dict:
        raise NotImplementedError(f"The {__class__} is not allowed to instantiate from remote resources")

    def _update_dl_parameters(self, instrument) -> Instrument:
        if isin := instrument.isin:
            instrument.dl_parameters["esg"] = {
                "path": self.ESG_PATH,
                "parameters": isin,
            }
            instrument.dl_parameters["esg_controversies"] = {
                "path": self.ESG_CONTROVERSY_PATH,
                "parameters": isin,
            }
        return instrument

    def update_item(self, instrument: Instrument) -> Instrument:
        self._update_dl_parameters(instrument)
        instrument.save()
        return instrument

    def trigger_partial_update(self):
        instruments_to_update = self.get_updatable_instruments()
        instruments_to_update_count = instruments_to_update.count()
        if instruments_to_update_count > 30:
            self.update()
        else:
            for instrument in instruments_to_update:
                self.update_item(instrument)
