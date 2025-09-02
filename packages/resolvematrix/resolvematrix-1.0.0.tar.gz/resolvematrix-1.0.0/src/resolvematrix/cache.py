from __future__ import annotations

import abc
import datetime
import typing

if typing.TYPE_CHECKING:
    from .server import ServerDestination

__all__ = ("BasicResolutionCache", "CacheEntry")


class CacheEntry:
    """
    Represents a single cache entry with server name, destination, expiration time, and online status.
    """

    def __init__(self, server_name: str, destination: str | ServerDestination, ttl: float):
        self.server_name = server_name
        self.destination = destination
        self.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=ttl)
        self.offline = False

    @property
    def expired(self):
        return datetime.datetime.now(datetime.timezone.utc) >= self.expires


class BaseCache(abc.ABC):
    """
    A cache implementation that does not store any entries.

    This class overrides all methods of BasicResolutionCache to effectively disable caching.
    It can be used in scenarios where caching is not desired or needed (such as in CI).

    All methods return default values or perform no operations.
    """

    @property
    def size(self) -> int:
        raise NotImplementedError

    def cleanup(self) -> int:
        raise NotImplementedError

    def add(self, server_name: str, destination: str | ServerDestination, ttl: float | None = None) -> None:
        raise NotImplementedError

    def get(self, server_name: str) -> str | ServerDestination | None:
        raise NotImplementedError

    def get_entry(self, server_name: str) -> CacheEntry | None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def remove(self, server_name: str) -> None:
        raise NotImplementedError

    def refresh(self, server_name: str) -> None:
        raise NotImplementedError

    def mark_online(self, server_name: str) -> None:
        raise NotImplementedError

    def mark_offline(self, server_name: str) -> None:
        raise NotImplementedError


class BasicResolutionCache(BaseCache):
    """
    A basic in-memory cache using dictionaries to store resolved server names and their destinations.

    This cache supports separate handling for client and server destinations, TTL management,
    and automatic cleanup of expired entries. It also allows marking servers as online or offline,
    which affects their TTL.

    You can zero any of the TTL parameters to disable that TTL's effect (very not recommended).
    Setting max_entries to zero disables automatic cleanup (also very not recommended). Expired entries that are fetched
    will still be removed on fetch even if max_entries is zero.

    :param default_ttl: The default time-to-live (TTL) for cache entries in seconds. Default is 86400 (24 hours).
    :param max_ttl: The maximum allowable TTL for cache entries in seconds. Default is 172800 (48 hours).
    :param min_ttl: The minimum allowable TTL for cache entries in seconds. Default is 600 (10 minutes).
    :param max_entries: The maximum number of entries allowed in the cache before cleanup is triggered. Default is 100k.
    """

    def __init__(
        self,
        default_ttl: float = 86400.0,
        max_ttl: float = 172800.0,
        min_ttl: float = 600.0,
        max_entries: int = 100_000,
    ):
        super().__init__()
        self.cache: dict[str, dict[str, CacheEntry]] = {"client": {}, "server": {}}
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.min_ttl = min_ttl

    @property
    def size(self) -> int:
        """Returns the total number of entries in the cache."""
        return len(self.cache["client"]) + len(self.cache["server"])

    def cleanup(self) -> int:
        """
        Removes expired entries from the cache.
        """
        if self.max_entries == 0:
            return 0  # automatic cleanup is disabled
        removed = 0
        for entry_type in ("client", "server"):
            to_remove = [name for name, entry in self.cache[entry_type].items() if entry.expired]
            for name in to_remove:
                del self.cache[entry_type][name]
                removed += 1
        return removed

    def add(self, server_name: str, destination: str | ServerDestination, ttl: float | None = None) -> None:
        """
        Adds a new entry to the cache, replacing any existing entry for the same server name.
        :param server_name: The server name to cache.
        :param destination: The server's destination information.
        :param ttl: The TTL to use, or the default if a nullish value is provided.
        :return: self
        """
        if not ttl:
            ttl = self.default_ttl
        ttl = max(self.min_ttl, min(self.max_ttl, ttl))

        entry = CacheEntry(server_name, destination, ttl)
        entry_type = "client" if isinstance(destination, str) else "server"
        self.cache[entry_type][server_name] = entry
        if self.size > self.max_entries:
            self.cleanup()
        return None

    def get(self, server_name: str) -> str | ServerDestination | None:
        """
        Retrieves a cached entry by server name, returning None if not found or expired.
        :param server_name: The server name to look up.
        :return: The cached destination information, or None if not found or expired.
        """
        if self.size > self.max_entries:
            self.cleanup()
        for entry_type in ("client", "server"):
            entry = self.cache[entry_type].get(server_name)
            if entry:
                if entry.expired:
                    del self.cache[entry_type][server_name]
                    return None
                return entry.destination
        return None

    def get_entry(self, server_name: str) -> CacheEntry | None:
        """
        Retrieves the full CacheEntry by server name, returning None if not found or expired.
        :param server_name: The server name to look up.
        :return: The cached CacheEntry, or None if not found or expired.
        """
        if self.size > self.max_entries:
            self.cleanup()
        for entry_type in ("client", "server"):
            entry = self.cache[entry_type].get(server_name)
            if entry:
                if entry.expired:
                    del self.cache[entry_type][server_name]
                    return None
                return entry

    def clear(self) -> None:
        """
        Clears all entries from the cache.
        :return: self
        """
        self.cache = {"client": {}, "server": {}}

    def remove(self, server_name: str) -> bool:
        """
        Removes a specific entry from the cache by server name.
        :param server_name: The server name to remove.
        :return: True if an entry was removed, False if not found.
        """
        for entry_type in ("client", "server"):
            if server_name in self.cache[entry_type]:
                del self.cache[entry_type][server_name]
                return True
        return False

    def refresh(self, server_name: str) -> None:
        """
        Refreshes a server's TTL to the default TTL.
        Has no effect if the server is not found or is marked offline.

        :param server_name: the server name to refresh
        """
        for entry_type in ("client", "server"):
            entry = self.cache[entry_type].get(server_name)
            if entry and not entry.offline:
                entry.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                    seconds=self.default_ttl
                )
                return

    def mark_online(self, server_name: str) -> None:
        """
        Marks a server as online and sets its TTL to the default TTL.
        Has no effect if the server is already marked online.

        :param server_name: the server name to mark as online
        """
        for entry_type in ("client", "server"):
            entry = self.cache[entry_type].get(server_name)
            if entry:
                if not entry.offline:
                    return
                entry.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                    seconds=self.default_ttl
                )
                entry.offline = False
                return

    def mark_offline(self, server_name: str) -> None:
        """
        Marks a server as offline by setting its TTL to the minimum TTL.
        Has no effect if the server is already marked offline.

        :param server_name: the server name to mark as offline
        """
        for entry_type in ("client", "server"):
            entry = self.cache[entry_type].get(server_name)
            if entry:
                if entry.offline:
                    return
                entry.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=self.min_ttl)
                entry.offline = True
                return


class VoidResolutionCache(BaseCache):
    """
    A cache implementation that does not store any entries.

    This class overrides all methods of BasicResolutionCache to effectively disable caching.
    It can be used in scenarios where caching is not desired or needed (such as in CI).

    All methods return default values or perform no operations.
    """

    @property
    def size(self) -> int:
        return 0

    def cleanup(self) -> int:
        return 0

    def add(self, server_name: str, destination: str | ServerDestination, ttl: float | None = None) -> None:
        return None

    def get(self, server_name: str) -> str | ServerDestination | None:
        return None

    def get_entry(self, server_name: str) -> CacheEntry | None:
        return None

    def clear(self) -> None:
        return None

    def remove(self, server_name: str) -> None:
        return None

    def refresh(self, server_name: str) -> None:
        return None

    def mark_online(self, server_name: str) -> None:
        return None

    def mark_offline(self, server_name: str) -> None:
        return None
