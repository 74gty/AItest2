from copy import deepcopy
from datetime import UTC, datetime, timedelta


class MemoryCache:
    def __init__(self, ttl_seconds=300):
        self.ttl = timedelta(seconds=ttl_seconds)
        self._data = {}

    def get(self, key):
        record = self._data.get(key)
        if not record:
            return None

        expires_at, value = record
        if datetime.now(UTC) > expires_at:
            self._data.pop(key, None)
            return None

        return deepcopy(value)

    def set(self, key, value):
        self._data[key] = (datetime.now(UTC) + self.ttl, deepcopy(value))

    def clear(self):
        self._data.clear()
