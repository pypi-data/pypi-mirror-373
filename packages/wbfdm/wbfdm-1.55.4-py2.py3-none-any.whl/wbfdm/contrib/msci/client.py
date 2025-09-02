from contextlib import suppress
from datetime import UTC, datetime
from typing import Generator

import requests
from django.core.cache import cache as cache_layer
from django.utils import timezone
from django.utils.functional import cached_property
from jwt import decode as jwt_decode
from jwt.exceptions import DecodeError
from requests.exceptions import ConnectionError


def is_expired(token: str) -> bool:
    with suppress(DecodeError, KeyError, ValueError):
        expiry_ts = int(jwt_decode(token, options={"verify_signature": False})["exp"])
        expiry_datetime = datetime.fromtimestamp(expiry_ts, UTC)
        return expiry_datetime < timezone.now()
    return True


class MSCIClient:
    AUTH_SERVER_ULR: str = "https://accounts.msci.com/oauth/token"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    @cached_property
    def oauth_token(self) -> str:
        token = cache_layer.get("msci_oauth_token")
        if not token or is_expired(token):
            resp = requests.post(
                self.AUTH_SERVER_ULR,
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                    "audience": "https://esg/data",
                },
            )
            if resp.status_code == requests.codes.ok:
                with suppress(KeyError, requests.exceptions.JSONDecodeError):
                    resp_json = resp.json()
                    token = resp_json["access_token"]
                    expires_in = resp_json["expires_in"]
                    cache_layer.set("msci_oauth_token", token, expires_in)
        if token:
            return token
        raise ConnectionError()

    def esg(self, identifiers: list[str], factors: list[str]) -> Generator[dict[str, str], None, None]:
        with suppress(ConnectionError):
            response = requests.post(
                url="https://api2.msci.com/esg/data/v2.0/issuers",
                json={
                    "issuer_identifier_list": identifiers,
                    "factor_name_list": factors,
                },
                headers={"AUTHORIZATION": f"Bearer {self.oauth_token}"},
            )
            if response.ok:
                for row in response.json().get("result", {}).get("issuers", []):
                    yield row

    def controversies(self, identifiers: list[str], factors: list[str]) -> Generator[dict[str, str], None, None]:
        next_url = "https://api2.msci.com/esg/data/v2.0/issuers"
        offset = 0
        while next_url:
            with suppress(ConnectionError):
                response = requests.post(
                    url=next_url,
                    json={
                        "issuer_identifier_list": identifiers,
                        "factor_name_list": factors,
                        "limit": 100,
                        "offset": offset,
                    },
                    headers={"AUTHORIZATION": f"Bearer {self.oauth_token}"},
                )

                if not response.ok:
                    next_url = None
                else:
                    json_res = response.json()
                    try:
                        next_url = json_res["paging"]["links"]["next"]
                    except KeyError:
                        next_url = None
                    offset += 100
                    for row in json_res.get("result", {}).get("issuers", []):
                        yield row
