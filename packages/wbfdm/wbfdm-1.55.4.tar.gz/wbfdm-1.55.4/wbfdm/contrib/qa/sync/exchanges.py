import pytz
from django.conf import settings
from django.db import connections
from django.db.models import Max
from wbcore.contrib.dataloader.utils import dictfetchall, dictfetchone
from wbcore.contrib.geography.models import Geography
from wbcore.utils.cache import mapping
from wbfdm.models import Exchange
from wbfdm.sync.abstract import Sync


class QAExchangeSync(Sync[Exchange]):
    SOURCE = "qa-ds2-exchange"

    def update(self):
        sql = "SELECT ExchIntCode AS source_id, ExchName AS name, ExchCtryCode AS country_id, ExchMnem AS refinitiv_mnemonic FROM DS2Exchange"
        Exchange.objects.bulk_create(
            map(
                lambda data: Exchange(
                    source=self.SOURCE,
                    source_id=data["source_id"],
                    name=data["name"],
                    country_id=mapping(Geography.countries, "code_2").get(data["country_id"]),
                    refinitiv_mnemonic=data["refinitiv_mnemonic"],
                ),
                dictfetchall(connections["qa"].cursor().execute(sql)),
            ),
            update_conflicts=True,
            update_fields=["name", "country", "refinitiv_mnemonic"],
            unique_fields=["source", "source_id"],
        )

    def update_or_create_item(self, external_id: int) -> Exchange:
        defaults = self.get_item(external_id)
        if country_id := defaults.get("country_id"):
            defaults["country_id"] = mapping(Geography.countries, "code_2").get(country_id)
        exchange, _ = Exchange.objects.update_or_create(
            source=self.SOURCE,
            source_id=external_id,
            defaults=defaults,
        )
        return exchange

    def update_item(self, item: Exchange) -> Exchange:
        return self.update_or_create_item(item.source_id)

    def get_item(self, external_id: int) -> dict:
        sql = "SELECT ExchName AS name, ExchCtryCode AS country_id, ExchMnem AS refinitiv_mnemonic FROM DS2Exchange WHERE ExchIntCode = %s"
        return dictfetchone(connections["qa"].cursor().execute(sql, (external_id,)))

    def trigger_partial_update(self):
        max_last_updated = (
            Exchange.objects.filter(source=self.SOURCE)
            .aggregate(max_last_updated=Max("last_updated"))
            .get("max_last_updated")
        )
        if max_last_updated is None:
            self.update()
        else:
            with connections["qa"].cursor() as cursor:
                cursor.execute(
                    "SELECT MAX(last_user_update) FROM sys.dm_db_index_usage_stats WHERE OBJECT_NAME(object_id) = 'DS2Exchange_changes'"
                )
                max_last_updated_qa = (
                    pytz.timezone(settings.TIME_ZONE).localize(result[0]) if (result := cursor.fetchone()) else None
                )
                if max_last_updated_qa and max_last_updated_qa > max_last_updated:
                    for _, exchange_id in cursor.execute(
                        "SELECT UpdateFlag_, ExchIntCode FROM DS2Exchange_changes"
                    ).fetchall():
                        self.update_or_create_item(exchange_id)
