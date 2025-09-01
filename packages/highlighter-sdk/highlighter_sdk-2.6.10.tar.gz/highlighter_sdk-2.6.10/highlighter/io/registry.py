"""Central registry mapping *content types* to *PayloadWriter* classes.

The goal: given a **ContentTypeEnum** (and optionally a *sub‑type* string)
return *an *instance* of the corresponding writer* ready to serialise a batch
of :class:`DataSample`s.

A writer must expose two public attributes/methods:

* ``extension`` – file‑extension string (``"mp4"``, ``"png"`` …)
* ``write(samples) -> bytes`` – serialise iterable of ``DataSample`` → bytes

See ``highlighter/io/writers.py`` for concrete implementations such as
:class:`VideoWriter`, :class:`ImageWriter`, or :class:`TextWriter`.
"""

# TODO:
# import logging
from typing import Callable, Dict, Tuple, Type

from highlighter.core.enums import ContentTypeEnum
from highlighter.io.base import PayloadWriter  # the Protocol from earlier

# TODO:
# logger = logging.getLogger(__name__)

# Key is ContentTypeEnum, however we should consider adding subtype (which  may be None) eg., Tuple[ContentTypeEnum, str | None]
_RegistryKey = Tuple[ContentTypeEnum]

# Internal mapping → writer *class* (not instance)
_writer_by_type: Dict[_RegistryKey, Type[PayloadWriter]] = {}


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def register_writer(
    content_type: ContentTypeEnum,
    writer_cls: Type[PayloadWriter],
    *,
    force: bool = False,
    # subtype: str | None = None, # TODO: consider adding
) -> None:
    """Register *writer_cls* for *content_type*.

    Parameters
    ----------
    content_type
        Enum value like ``ContentTypeEnum.IMAGE``.
    writer_cls
        A class implementing the :class:`PayloadWriter` protocol.
    force
        If False (default) and a writer is already registered for the key, a
        ``ValueError`` is raised.  If True, silently overwrites.
    """
    key: _RegistryKey = content_type
    if not force and key in _writer_by_type:
        raise ValueError(f"Writer already registered for {key}")
    _writer_by_type[key] = writer_cls
    # TODO:
    # logger.debug("Registered writer %s for %s", writer_cls.__name__, key)


def get_writer(
    content_type: ContentTypeEnum,
    **kwargs,
) -> PayloadWriter:
    """Instantiate and return the writer for *content_type*.

    ``kwargs`` are forwarded to the writer's constructor.
    """
    key: _RegistryKey = content_type
    try:
        writer_cls = _writer_by_type[key]
    except KeyError as exc:
        available = ", ".join(str(k) for k in _writer_by_type)
        raise ValueError(f"No writer registered for key {key}. Available: {available}") from exc
    return writer_cls(**kwargs)


# --------------------------------------------------------------------------- #
# Default built‑in registrations
# --------------------------------------------------------------------------- #
# Import *after* function definitions to avoid circular dependencies when the
# writers themselves import this registry for registration-at-import‑time.

try:
    from highlighter.io.writers import (  # CSVWriter,
        ImageWriter,
        ObservationWriter,
        TextWriter,
        VideoWriter,
    )
except ModuleNotFoundError:
    raise
    # The host project may choose to provide its own writers – log & continue.
    # TODO:
    # logger.warning("Default writer implementations not found; registry is empty")
else:
    # Basic image/video/text mappings
    register_writer(ContentTypeEnum.IMAGE, ImageWriter)
    register_writer(ContentTypeEnum.VIDEO, VideoWriter)
    register_writer(ContentTypeEnum.TEXT, TextWriter)
    register_writer(ContentTypeEnum.OBSERVATION, ObservationWriter)
    # register_writer(ContentTypeEnum.CSV, CSVWriter)

    # TODO: Consider supporting specialised subtypes
    # eg., register_writer(ContentTypeEnum.TEXT, CSVWriter, subtype="csv")
