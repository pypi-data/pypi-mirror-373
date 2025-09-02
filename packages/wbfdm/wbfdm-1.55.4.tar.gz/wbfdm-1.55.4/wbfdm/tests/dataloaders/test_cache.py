import pytest
from django.core.cache import cache as cache_layer
from faker import Faker

from wbfdm.dataloaders.cache import Cache

fake = Faker()


class TestCache:
    @pytest.fixture
    def cache(self):
        return Cache()

    def test_initialize(self, cache):
        cache.missing_keys = ["a"]
        cache.missing_ids = ("a",)
        cache.missing_symbols = ("a",)
        cache.initialize([1], ["a", "b"])

        # ensure initialize reset the missing attributes set
        assert cache.missing_keys == list()
        assert cache.missing_ids == set()
        assert cache.missing_symbols == set()
        assert cache.id_symbol_pairs == [("1", "a"), ("1", "b")]

        cache.initialize([1, 2], ["a"])
        assert cache.id_symbol_pairs == [("1", "a"), ("2", "a")]

    def test__get_cache_key(self, cache):
        assert cache._get_cache_key("a", "b") == "a_b"

    def test__deserialize_cache(self, cache):
        assert cache._deserialize_cache("1", "symbol", "value") == {
            cache.identifier_key: 1,
            cache.symbol_key: "symbol",
            cache.value_key: "value",
        }

    def test_fetch_from_cache(self, cache):
        cache.initialize([1], ["a"])
        assert list(cache.fetch_from_cache()) == list()
        assert cache.missing_keys == ["1_a"]
        assert cache.missing_symbols == {"a"}
        assert cache.missing_ids == {"1"}

        cache.initialize([1], ["a"])
        assert list(cache.fetch_from_cache()) == []
        assert cache.missing_keys == ["1_a"]

        value = fake.pyfloat()
        cache_layer.set("1_a", value)
        cache.initialize([1], ["a"])
        assert list(cache.fetch_from_cache()) == [{"instrument_id": 1, "factor_code": "a", "value": value}]
        assert cache.missing_keys == list()

        cache_layer.set("1_a", None)
        cache.initialize([1], ["a"])
        assert list(cache.fetch_from_cache()) == list()
        assert cache.missing_keys == list()

    def test_write(self, cache):
        cache.missing_keys = ["1_a"]
        value = fake.pyfloat()
        cache.write({"instrument_id": 1, "factor_code": "a", "value": value})
        assert cache.missing_keys == list()
        assert cache_layer.get("1_a") == value

    def test_close(self, cache):
        cache.missing_keys = ["3_c"]
        sentinel = object()
        assert cache_layer.get("3_c", sentinel) == sentinel
        cache.close()
        assert cache_layer.get("3_c", sentinel) is None
