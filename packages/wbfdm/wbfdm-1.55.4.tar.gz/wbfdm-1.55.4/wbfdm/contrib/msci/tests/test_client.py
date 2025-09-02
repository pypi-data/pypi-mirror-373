import time
from datetime import datetime

import pytest
from django.core.cache import cache as cache_layer
from django.utils import timezone
from faker import Faker
from jwt import encode
from requests.exceptions import ConnectionError

from ..client import MSCIClient, is_expired

fake = Faker()


class TestMSCIClient:
    @pytest.fixture()
    def jwt(self, expiry_date: datetime):
        payload = {"exp": int(expiry_date.timestamp()), "iat": int(timezone.now().timestamp())}
        return encode(payload, "secret", algorithm="HS256")

    @pytest.fixture()
    def msci_client(self):
        return MSCIClient("username", "password")

    @pytest.mark.parametrize("expiry_date", [fake.past_datetime()])
    def test_is_expired_true(self, expiry_date, jwt):
        assert is_expired(jwt)

    @pytest.mark.parametrize("expiry_date", [fake.future_datetime()])
    def test_is_expired_false(self, expiry_date, jwt):
        assert not is_expired(jwt)

    def test_oauth_token_not_in_cache(self, requests_mock, msci_client):
        access_token = fake.word()
        expiry = fake.pyint(min_value=60)
        requests_mock.post(MSCIClient.AUTH_SERVER_ULR, json={"access_token": access_token, "expires_in": expiry})
        t0 = time.time()
        res = msci_client.oauth_token
        assert res == access_token
        assert cache_layer.get("msci_oauth_token") == access_token
        assert int(cache_layer._expire_info.get(":1:msci_oauth_token")) == int(t0 + expiry)

    @pytest.mark.parametrize("expiry_date", [fake.future_datetime()])
    def test_oauth_token_in_cache_and_valid(self, requests_mock, msci_client, expiry_date, jwt):
        requests_mock.post(MSCIClient.AUTH_SERVER_ULR, json={"access_token": fake.word()})
        cache_layer.set("msci_oauth_token", jwt)
        assert msci_client.oauth_token == jwt

    @pytest.mark.parametrize("expiry_date", [fake.past_datetime()])
    def test_oauth_token_in_cache_but_expired(self, requests_mock, msci_client, expiry_date, jwt):
        requests_mock.post(MSCIClient.AUTH_SERVER_ULR, json={"access_token": fake.word()})
        cache_layer.set("msci_oauth_token", jwt)

        access_token = fake.word()
        requests_mock.post(
            MSCIClient.AUTH_SERVER_ULR, json={"access_token": access_token, "expires_in": fake.pyint(min_value=60)}
        )
        assert msci_client.oauth_token == access_token

    def test_oauth_token_connection_error(self, requests_mock, msci_client):
        cache_layer.clear()
        # keyerror
        requests_mock.post(MSCIClient.AUTH_SERVER_ULR, json={"access_token_typo": fake.word()})
        with pytest.raises(ConnectionError):
            t = msci_client.oauth_token  # noqa

        requests_mock.post(MSCIClient.AUTH_SERVER_ULR, status_code=500)
        with pytest.raises(ConnectionError):
            t = msci_client.oauth_token  # noqa
