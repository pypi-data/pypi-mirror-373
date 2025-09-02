from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.contrib.auth.models import Permission
from django.db import models
from django.db.models import Q
from slugify import slugify
from wbcore.contrib.authentication.models import User
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler
from wbcore.contrib.notifications.dispatch import send_notification

from .instrument import InstrumentImportHandler


class InstrumentListImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbfdm.InstrumentListThroughModel"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)

    def _deserialize(self, data: Dict[str, Any]):
        if from_date := data.get("from_date", None):
            data["from_date"] = datetime.strptime(from_date, "%Y-%m-%d").date()
        if to_date := data.get("to_date", None):
            data["to_date"] = datetime.strptime(to_date, "%Y-%m-%d").date()
        if instrument_list_data := data.pop("instrument_list", None):
            if isinstance(instrument_list_data, int):
                data["instrument_list"] = self.model.instrument_list.get_queryset().get(id=instrument_list_data)
            elif isinstance(instrument_list_data, dict) and "name" in instrument_list_data:
                data["instrument_list"] = self.model.instrument_list.get_queryset().get_or_create(
                    identifier=instrument_list_data.pop("identifier", slugify(instrument_list_data["name"])),
                    **instrument_list_data,
                )[0]
        if instrument_data := data.pop("instrument", None):
            data["instrument"] = self.instrument_handler.process_object(
                instrument_data, only_security=True, read_only=True
            )[0]
        # we try to automatically match the instrument name against a already known matched row
        if instrument_str := data.get("instrument_str"):
            already_existing_rows = self.model.objects.filter(
                instrument__isnull=False,
                instrument_str=instrument_str,
                instrument_list=data.get("instrument_list", None),
            )
            if already_existing_rows.count() == 1:
                data["instrument"] = already_existing_rows.first().instrument
        if "instrument_list" not in data:
            raise DeserializationError("Instrument List not find in this row")

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        if instrument := data.get("instrument", None):
            return self.model.objects.filter(
                instrument=instrument,
                instrument_list=data["instrument_list"],
            ).first()

    def _post_processing_objects(
        self,
        created_objs: List[models.Model],
        modified_objs: List[models.Model],
        unmodified_objs: List[models.Model],
    ):
        objs = modified_objs + unmodified_objs + created_objs
        lists = set(map(lambda x: x.instrument_list, objs))
        leftovers_objs = self.model.objects.filter(instrument_list__in=lists)
        for obj in objs:
            leftovers_objs = leftovers_objs.exclude(id=obj.id)
        leftovers_objs.delete()

        instrument_dict = defaultdict(list)
        for obj in modified_objs + created_objs:
            instrument_dict[obj.instrument_list].append(obj)
        for instrument_list, items in instrument_dict.items():
            if items:
                report = """
                <p>List of instrument added or modified:</p>
                <ul>
                """
                for item in items:
                    if item.instrument:
                        report += f"<li>{item.instrument_str} (automatically link to {item.instrument}</li>"
                    else:
                        report += f"<li>{item.instrument_str}</li>"
                report += "</ul>"
                perm = Permission.objects.get(codename="administrate_instrumentlist")
                for user in (
                    User.objects.filter(is_active=True)
                    .filter(Q(groups__permissions=perm) | Q(user_permissions=perm))
                    .distinct()
                ):
                    send_notification(
                        code="wbfdm.instrument_list_add",
                        name=f"Instruments have been added or modified into the instrument list {instrument_list.name}",
                        body=report,
                        user=user,
                        reverse_name="wbfdm:instrumentlist-detail",
                        reverse_args=[instrument_list.id],
                    )
