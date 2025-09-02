import pytest


@pytest.mark.django_db
class TestExchangeModel:
    def test_init(self, exchange):
        assert exchange.id is not None
