from typing import Any, Optional, Type, Union
from uuid import UUID, uuid4

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

__all__ = ["LabeledUUID"]


class LabeledUUID(UUID):
    """LabeledUUID behaves exactly like a UUID, but has
    an additional 'label' field that is added to .__repr__() and .pretty()
    for readability
    """

    def __init__(self, *args, label: Optional[str] = None, **kwargs):
        if args and isinstance(args[0], UUID):
            args = list(args)
            args[0] = str(args[0])

        if args and isinstance(args[0], str):
            args = list(args)
            s = args[0]
            parts = s.split("|")
            if len(parts) == 2:
                uuid_str, label = parts
                args[0] = uuid_str
            elif len(parts) == 1:
                uuid_str = parts[0]
                args[0] = uuid_str
        super().__init__(*args, **kwargs)

        # Why not simply 'self.label = ... ?' I hear you ask.
        # The base class UUID is immutable so it blocks __setattr__, see:
        #   https://github.com/python/cpython/blob/main/Lib/uuid.py#L277
        # This is the way they do it in the UUID base class' constructor, see:
        #   https://github.com/python/cpython/blob/main/Lib/uuid.py#L222
        object.__setattr__(self, "_label", "" if label is None else label)

    def __repr__(self) -> str:
        return self.short_str()

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return str(self) == other
        else:
            return super().__eq__(other)

    def __hash__(self) -> int:
        # Is this the same as not overriding __hash__? You'd think that
        # wouldn't you, but no __hash__ is special. See:
        #
        #   https://stackoverflow.com/a/53519136
        return super().__hash__()

    @property
    def label(self) -> str:
        return getattr(self, "_label", "")

    @classmethod
    def uuid4(cls, label: Optional[str] = None):
        return cls(int=uuid4().int, label=label)

    @classmethod
    def from_str(cls, s):
        """Init from formatted string

        Args:
            s: 01234567-0123-0123-0123-012345678901|My label
        """
        uuid_str, label = s.split("|")
        return cls(uuid_str, label=label)

    @classmethod
    def from_dict(cls, *, uuid: Union[str, UUID], label: str):
        if isinstance(uuid, UUID):
            return cls(str(uuid), label=label)
        assert isinstance(uuid, str)
        return cls(uuid, label=label)

    def short_str(self) -> str:
        """1234..8901|My label"""
        uuid_str = str(self)
        short_uuid = f"{uuid_str[:4]}..{uuid_str[-4:]}"
        label = getattr(self, "label", "")
        return f"{short_uuid}|{label}" if label else short_uuid

    def verbose_str(self) -> str:
        """01234567-0123-0123-0123-012345678901|My label"""
        uuid_str = str(self)
        short_uuid = f"{uuid_str[:4]}..{uuid_str[-4:]}"
        label = getattr(self, "label", "")
        return f"{uuid_str}|{label}" if label else short_uuid

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        assert source is LabeledUUID

        # Union schema can handle
        # str, uuid or dict
        # if dict, the 'uuid' value can be a str or uuid object
        custom_schema = core_schema.union_schema(
            [
                core_schema.str_schema(),  # Handle string inputs
                core_schema.uuid_schema(),  # Handle UUID inputs
                core_schema.typed_dict_schema(
                    {
                        "uuid": core_schema.typed_dict_field(
                            core_schema.union_schema([core_schema.str_schema(), core_schema.uuid_schema()])
                        ),
                        "label": core_schema.typed_dict_field(core_schema.str_schema()),
                    }
                ),
            ]
        )
        return core_schema.no_info_after_validator_function(cls.validate, custom_schema)

    @classmethod
    def validate(cls, value: Any) -> "LabeledUUID":
        if isinstance(value, cls):
            return value
        elif isinstance(value, (str, UUID)):
            return LabeledUUID(value)
        elif isinstance(value, dict):
            assert "uuid" in value
            return LabeledUUID.from_dict(**value)
        else:
            raise ValueError(f"Invalid LabeledUUID {value}")

    @staticmethod
    def _serialize(value: "LabeledUUID") -> str:
        return str(value)
