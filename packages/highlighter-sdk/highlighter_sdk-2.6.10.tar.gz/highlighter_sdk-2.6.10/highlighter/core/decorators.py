import functools
import warnings


def deprecated_class(cls):
    original_init = cls.__init__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        warnings.warn(
            f"{cls.__name__} is deprecated and will be removed in a future version.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls


# Default no-op for runtime assignment later
def noop(fn):
    return fn


# global decorator for functions making network calls which handles retries and circuit breaking
network_fn_decorator = noop  # Will be set by Runtime.start()
