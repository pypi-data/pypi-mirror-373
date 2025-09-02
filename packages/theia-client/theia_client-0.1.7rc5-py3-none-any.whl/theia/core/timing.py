import collections
import time
from typing import Deque, Generic, Iterable, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Timer:
    """A timer that can be used to measure the duration of an operation."""

    def __init__(self, duration_s: float | None = None):
        self._start_time = _now()
        self._duration_s = duration_s

    def elapsed_s(self) -> float:
        return _now() - self._start_time

    def is_finished(self) -> bool:
        if self._duration_s is None:
            raise ValueError("Timer has no duration.")
        return self.elapsed_s() >= self._duration_s


class ExpiringSet(Generic[T]):
    """A set whose entries expire after a configured duration."""

    def __init__(self, expiration_s: float):
        super().__init__()
        self._expiration_s = expiration_s
        self._timed_keys: dict[T, float] = {}

    def _discard_expired(self) -> None:
        """Discards expired entries from the dictionary."""
        # Since dict iteration follows insertion order, the oldest values will be
        # encountered first.
        now = _now()
        expired_keys = []
        for key, timestamp in self._timed_keys.items():
            if now - timestamp >= self._expiration_s:
                expired_keys.append(key)
            else:
                break

        for key in expired_keys:
            del self._timed_keys[key]

    def add(self, key: T) -> None:
        self._discard_expired()
        # Remove the object before adding such that insertion order corresponds with age.
        if key in self._timed_keys:
            del self._timed_keys[key]
        self._timed_keys[key] = _now()

    def values(self) -> set[T]:
        self._discard_expired()
        return set(self._timed_keys)

    def contains(self, key: T) -> bool:
        self._discard_expired()
        return key in self._timed_keys


class ExpiringDict(Generic[T, U]):
    """A dictionary whose entries expire after a configured duration."""

    def __init__(self, expiration_s: float):
        super().__init__()
        self._expiration_s = expiration_s
        self._timed_items: dict[T, tuple[float, U]] = {}

    def _discard_expired(self) -> None:
        """Discards expired entries from the dictionary."""
        # Since dict iteration follows insertion order, the oldest values will be
        # encountered first.
        now = _now()
        expired_keys = []
        for key, (timestamp, _) in self._timed_items.items():
            if now - timestamp >= self._expiration_s:
                expired_keys.append(key)
            else:
                break

        for key in expired_keys:
            del self._timed_items[key]

    def set(self, key: T, value: U) -> None:
        # Remove the object before adding such that insertion order corresponds with age.
        if key in self._timed_items:
            del self._timed_items[key]
        self._discard_expired()
        self._timed_items[key] = (_now(), value)

    def items(self) -> Iterable[tuple[T, U]]:
        self._discard_expired()
        return ((k, v) for k, (_, v) in self._timed_items.items())

    def get(self, key: T) -> U | None:
        self._discard_expired()
        item = self._timed_items.get(key)
        if item is None:
            return None
        _, value = item
        return value

    def delete(self, key: T) -> None:
        if key in self._timed_items:
            del self._timed_items[key]


class ExpiringQueue(Generic[T]):
    """A queue whose values expire after a configured duration."""

    def __init__(self, expiration_s: float):
        self._expiration_s = expiration_s
        self._timed_values: Deque[tuple[float, T]] = collections.deque()

    def _discard_expired(self) -> None:
        """Discards expired values from the queue."""
        now = _now()
        while self._timed_values:
            then, _ = self._timed_values[0]
            if now - then >= self._expiration_s:
                self._timed_values.popleft()
            else:
                break

    def append(self, obj: T) -> None:
        # Even though this method does not access the queue, we need to discard expired
        # values to ensure the queue does not grow without bound.
        self._discard_expired()
        self._timed_values.append((_now(), obj))

    def values(self) -> list[T]:
        self._discard_expired()
        return [obj for _, obj in self._timed_values]


class FrequencyCounter:
    """Tracks event frequency within a specified time window."""

    def __init__(self, window_s: float):
        self._window_s = window_s
        self._expiring_q: ExpiringQueue[None] = ExpiringQueue(window_s)

    def update(self) -> None:
        """Records a new event at the current time."""
        self._expiring_q.append(None)

    def frequency(self) -> float:
        """Returns the current event frequency."""
        q_values = self._expiring_q.values()
        return len(q_values) / self._window_s


def _now() -> float:
    return time.perf_counter()
