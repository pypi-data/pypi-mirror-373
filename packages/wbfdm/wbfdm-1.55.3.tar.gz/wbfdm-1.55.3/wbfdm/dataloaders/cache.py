import itertools
from typing import Any, Generic, Iterable, TypedDict, TypeVar, cast

from django.core.cache import cache

T = TypeVar("T", bound=TypedDict)


class Cache(Generic[T]):
    """
    A Cache Class to handle 3-Dimensional data (identifier-key-value)
    """

    def __init__(
        self,
        identifier_key: str = "instrument_id",
        symbol_key: str = "factor_code",
        value_key: str = "value",
        timeout: int | None = None,
    ):
        """
        Constructor of the Cache Class
        Args:
            identifier_key: The lookup identifier field. Default to `instrument_id`
            symbol_key: The symbol lookup field. Default to `factor_code`
            value_key: The value lookup field. Default to `value`
            timeout: The cache timeout configuration value. Default to None (never expired)
        """
        self.identifier_key = identifier_key
        self.symbol_key = symbol_key
        self.value_key = value_key
        self.timeout = timeout
        self.id_symbol_pairs: list[tuple[str, str]] = []
        self.missing_keys = []
        self.missing_ids = set()
        self.missing_symbols = set()

    def _get_cache_key(self, id: str, symbol: str) -> str:
        """
        Generate the key used in the caching layer based on the given ID and symbol.

        Args:
            id (str): The ID to be used in the cache key.
            symbol (str): The symbol to be used in the cache key.

        Returns:
            str: A cache key in the format "id_symbol" where both the ID and symbol
            are in lowercase.
        """
        return f"{str(id).lower()}_{symbol.lower()}"

    def _deserialize_cache(self, id: str, symbol: str, value: Any) -> T:
        """
        Data retreived from cache is deserialized using this method. We expect a key value format which is converted into a dictionary with keys as identifier, symbol and value

        Args:
            id: identifier
            symbol: symbol
            value: value

        Returns:
            a dictionary with keys as identifier, symbol and value
        """
        res = {self.identifier_key: int(id), self.symbol_key: symbol, self.value_key: value}
        return cast(T, res)

    def initialize(self, ids: list[int], symbols: list[str]):
        """
        Initialize the instance with a list of IDs and symbols.

        This method takes a list of identifiers and a list of symbols and creates a list of
        tuples containing all possible pairs of identifiers (converted to strings) and symbols.
        It also initializes sets for symbol and identifiers not present in cache

        Args:
            ids (list[int]): A list of integer IDs.
            symbols (list[str]): A list of symbol strings.
        """
        self.id_symbol_pairs = list(map(lambda x: (str(x[0]), x[1]), itertools.product(ids, symbols)))
        self.missing_ids = set()
        self.missing_symbols = set()
        self.missing_keys = list()

    def fetch_from_cache(self) -> Iterable[T]:
        """
        Fetch values already stored in the cache.

        This method iterates over all identifiers and symbols pair and return the cached value if it exists or mark this pair as missing

        Yields:
            T: Deserialized cached values.
        """
        sentinel = object()
        for id, symbol in self.id_symbol_pairs:
            key = self._get_cache_key(id, symbol)
            cached_value = cache.get(key, sentinel)
            if cached_value is not None and cached_value is not sentinel:
                yield self._deserialize_cache(id, symbol, cached_value)
            elif (
                cached_value is sentinel
            ):  # otherwise, it's literal None and then it means the cache contains "None" for that key
                self.missing_symbols.add(symbol)
                self.missing_ids.add(id)
                self.missing_keys.append(key)

    def write(self, row: T) -> T:
        """
        Write given row into the cache

        Args:
            row: a dictionary typed object

        Returns:
            a dictionary typed object
        """
        if (key := row.get(self.identifier_key)) and (symbol := row.get(self.symbol_key)):
            value = row.get(self.value_key)
            key = self._get_cache_key(str(key), str(symbol))
            cache.set(key, value, timeout=self.timeout)
            if key in self.missing_keys:  # mark row's key are "handled"
                self.missing_keys.remove(key)
        return row

    def close(self):
        """
        Close cache stream by fixing missing keys not handled as None value in the cache (it shows that the value was actually fetched but didn't returned any value)
        """
        for key in self.missing_keys:
            cache.set(key, None, timeout=self.timeout)
