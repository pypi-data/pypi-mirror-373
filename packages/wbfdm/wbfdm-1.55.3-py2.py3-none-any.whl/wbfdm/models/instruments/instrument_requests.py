from typing import Any, Dict, Optional

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from wbcore.contrib.authentication.models import User
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.geography.models import Geography
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.tags.models import Tag
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.models import WBModel

from wbfdm.models.instruments.classifications import Classification

from .instruments import Instrument, InstrumentType


class InstrumentRequest(WBModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"
        DRAFT = "DRAFT", "Draft"

    status = FSMField(
        default=Status.DRAFT,
        choices=Status.choices,
        verbose_name="Status",
        help_text="The Request Status (default to Pending)",
    )
    requester = models.ForeignKey(
        "directory.Person",
        related_name="instrument_requests",
        on_delete=models.SET_NULL,
        verbose_name="Requester",
        null=True,
        blank=True,
    )
    handler = models.ForeignKey(
        "directory.Person",
        related_name="handled_instrument_requests",
        on_delete=models.SET_NULL,
        verbose_name="Handler",
        null=True,
        blank=True,
    )
    notes = models.TextField(null=True, blank=True, verbose_name="Notes")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created", help_text="The request creation time")
    instrument_data = models.JSONField(default=dict, verbose_name="Instrument Data")
    created_instrument = models.OneToOneField(
        "wbfdm.Instrument", on_delete=models.CASCADE, blank=True, null=True, related_name="creation_request"
    )

    def __str__(self):
        return f'Instrument Request - {self.Status[self.status].label} ({"".join([f"{k}={v}" for k, v in self.instrument_data.items()])})'

    @property
    def deserialize_instrument_data(self) -> tuple[Dict[str, Any], Dict[str, Any]]:
        instrument_data = self.instrument_data.copy()
        many_to_many_data = dict()
        if currency_id := instrument_data.get("currency", None):
            instrument_data["currency"] = Currency.objects.filter(id=currency_id).first()
        if country_id := instrument_data.get("country", None):
            instrument_data["country"] = Geography.countries.filter(id=country_id).first()
        if instrument_type_id := instrument_data.get("instrument_type", None):
            instrument_data["instrument_type"] = InstrumentType.objects.get(id=instrument_type_id)
        if tags_list := instrument_data.pop("tags", None):
            many_to_many_data["tags"] = [Tag.objects.filter(id=tag_id).first() for tag_id in tags_list]
        if classifications_list := instrument_data.pop("classifications", None):
            many_to_many_data["classifications"] = [
                Classification.objects.filter(id=classification_id).first()
                for classification_id in classifications_list
            ]
        instrument_data["is_investable_universe"] = True
        return instrument_data, many_to_many_data

    def _check_already_existing_instrument(self):
        return (
            (isin := self.instrument_data.get("isin", None)) and Instrument.objects.filter(isin=isin).exists()
        ) or (
            (ric := self.instrument_data.get("refinitiv_identifier_code", None))
            and Instrument.objects.filter(refinitiv_identifier_code=ric).exists()
        )

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.APPROVED,
        permission=lambda instance, user: user.has_perm("wbfdm.administrate_instrument"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbfdm:instrumentrequest",),
                icon=WBIcon.APPROVE.icon,
                key="approve",
                label="Approve",
                action_label="Approve",
                description_fields="<p>You are sure to approve this request?</p>",
            )
        },
    )
    def approve(self, by: Optional[User] = None, **kwargs):
        deserialize_instrument_data, many_to_many_data = self.deserialize_instrument_data
        created_instrument = Instrument.objects.create(**deserialize_instrument_data)
        for key, items in many_to_many_data.items():
            getattr(created_instrument, key).set(items)
        if profile := getattr(by, "profile", None):
            self.handler = profile
        self.created_instrument = created_instrument

    def can_approve(self):
        if self._check_already_existing_instrument():
            return {"non_field_errors": [_("An instrument already exists with the proposed identifier")]}

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.DENIED,
        permission=lambda instance, user: user.has_perm("wbfdm.administrate_instrument"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbfdm:instrumentrequest",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label="Deny",
                action_label="Deny",
                description_fields="<p>You are sure to deny this request?</p>",
            )
        },
    )
    def deny(self, by: Optional[User] = None, **kwargs):
        if profile := getattr(by, "profile", None):
            self.handler = profile

    @transition(
        field=status,
        source=[Status.DENIED],
        target=Status.DRAFT,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbfdm:instrumentrequest",),
                icon=WBIcon.SEND.icon,
                key="backtodraft",
                label="Back To Draft",
                action_label="Back To Draft",
                description_fields="<p>You are sure to put this request back to draft?</p>",
            )
        },
    )
    def backtodraft(self, by: Optional[User] = None, **kwargs):
        pass

    @transition(
        field=status,
        source=[Status.DRAFT],
        target=Status.PENDING,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbfdm:instrumentrequest",),
                icon=WBIcon.SEND.icon,
                key="submit",
                label="Submit",
                action_label="Submit",
                description_fields="<p>You are sure to submit this request back?</p>",
            )
        },
    )
    def submit(self, by: Optional[User] = None, **kwargs):
        pass

    def can_submit(self) -> Dict[str, Any]:
        if self._check_already_existing_instrument():
            return {"non_field_errors": [_("An instrument already exists with the proposed identifier")]}

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbfdm:instrumentrequestrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "Request {{id}} ({{status}})"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbfdm:instrumentrequest"
