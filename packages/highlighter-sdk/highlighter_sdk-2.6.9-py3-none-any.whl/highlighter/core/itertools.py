import itertools as it

__all__ = ["iterbatch"]


def iterbatch(iterable, batch_size=None):
    if batch_size is None:
        yield iterable
    else:
        iterator = iter(iterable)
        try:
            while True:
                first_elem = next(iterator)
                yield it.chain((first_elem,), it.islice(iterator, batch_size - 1))
        except StopIteration:
            pass
