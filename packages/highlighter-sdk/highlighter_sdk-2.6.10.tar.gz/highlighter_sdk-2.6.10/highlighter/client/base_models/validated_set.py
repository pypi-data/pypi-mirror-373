from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar("T")


class ValidatedSet(Generic[T]):
    """Set-like collection with object uniqueness via the .id attribute.
    Uses a dict internally to allow values to mutate."""

    def __init__(self, iterable: Iterable[T] | None = None, *, validator: Callable[[T], None] | None = None):
        self.validator = validator
        self._data: dict[object, T] = {}
        if iterable:
            self.update(iterable)  # goes through our validated update

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self._data.values())[key]
        else:
            return self._data[key]

    def _check(self, item: T):
        if not hasattr(item, "id"):
            raise AttributeError(f"Object {item!r} has no `.id` attribute.")
        if self.validator:
            self.validator(item)

    def add(self, item: T):
        self._check(item)
        self._data[item.id] = item

    def append(self, item: T):
        self.add(item)

    def extend(self, iterable: Iterable[T]):
        self.update(iterable)

    def update(self, *iterables: Iterable[T]):
        for iterable in iterables:
            for item in iterable:
                self.add(item)  # validation happens here

    def discard(self, item: T) -> None:
        self._data.pop(item.id, None)

    def remove(self, item: T) -> None:
        if item.id not in self._data:
            raise KeyError(item)
        del self._data[item.id]

    def __contains__(self, item: object) -> bool:
        return hasattr(item, "id") and item.id in self._data

    def __iter__(self):
        return iter(list(self._data.values()))

    def __len__(self) -> int:
        return len(self._data)

    def __ior__(self, other: Iterable[T]) -> "ValidatedSet[T]":
        # |= operator (in-place union)
        self.update(other)
        return self

    def __repr__(self) -> str:
        return f"{type(self).__name__}({list(self._data.values())})"
