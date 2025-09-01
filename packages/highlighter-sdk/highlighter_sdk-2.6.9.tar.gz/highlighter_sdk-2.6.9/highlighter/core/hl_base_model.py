import re
from collections.abc import MutableMapping
from typing import List, Optional, Type, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict

__all__ = [
    "BelongsTo",
    "GQLBaseModel",
    "HLDataModel",
    "HLModelMap",
    "HasMany",
    "camel_to_snake",
    "snake_to_camel",
]


def camel_to_snake(s):
    if s.isupper():
        return s
    snake = re.sub("([A-Z])", r"_\g<1>", s).lower()
    if snake.startswith("_"):
        snake = snake[1:]
    return snake


def snake_to_camel(s):
    if s.isupper():
        return s
    first, *rest = s.split("_")
    return first + "".join(x.capitalize() for x in rest)


def map_keys_deeply(x, f):
    if isinstance(x, dict):
        result = {f(k): map_keys_deeply(v, f) for k, v in x.items()}
    elif isinstance(x, list):
        result = [map_keys_deeply(element, f) for element in x]
    else:
        result = x
    return result


class IdentityMap:
    def __init__(self):
        self._objects = {}

    def get(self, obj_cls, obj_id):
        return self._objects.get((obj_cls, obj_id))

    def add(self, obj):
        obj_cls = type(obj)
        obj_id = obj.get_id()
        self._objects[(obj_cls, obj_id)] = obj

    def remove(self, obj_cls, obj_id):
        _ = self._objects.pop((obj_cls, obj_id), None)


class GQLBaseModel(BaseModel):
    """To allow for seamless integration with the GraphQL CamelCaseWorld and
    th_python_snake_case_world. We have this customized Pydantic BaseModel.

    This expects all fields are defined in snake_case.
    When serialized the resulting dict will have CamelCase keys,
    this allows it to play nice with GraphQL.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    def __init__(self, *args, **kwargs):
        kwargs = map_keys_deeply(kwargs, camel_to_snake)
        super().__init__(*args, **kwargs)

    def gql_dict(self):
        d = self.model_dump(exclude_none=True)
        d = map_keys_deeply(d, snake_to_camel)
        return d


class HLDataModel(GQLBaseModel):
    """Adds the IdentityMap pattern to GQLBaseModel provide an API that ensures
    only one instance of an object is being accessed and modified in the code.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", validate_assignment=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._get_identity_map().add(self)
        self._get_has_many_relationships()

    @classmethod
    def _get_identity_map(cls) -> IdentityMap:
        """Get the identity map for the current class (subclass)."""
        if not hasattr(cls, "_identity_map"):
            # Create a new identity map for the subclass
            cls._identity_map = IdentityMap()
        return cls._identity_map

    @classmethod
    def _add_has_many_relationship(cls, field, target_cls, back_populates):
        cls._get_has_many_relationships().append(
            {
                "field": field,
                "target_cls": target_cls,
                "back_populates": back_populates,
            }
        )

    @classmethod
    def _get_has_many_relationships(cls) -> List:
        if not hasattr(cls, "_has_many_relationships"):
            # Create a new identity map for the subclass
            cls._has_many_relationships = []
        return cls._has_many_relationships

    def get_id(self):
        """subclasses must have an .id member. Or you need to override this method"""
        try:
            return self.id  # type: ignore
        except AttributeError as _:
            raise AttributeError(
                f"{self.__class__.__name__} has no member self.id. "
                "Did you need to override def get_id(self)?"
            )

    @classmethod
    def find_by_id(cls, obj_id):
        return cls._get_identity_map().get(cls, obj_id)

    @classmethod
    def remove_by_id(cls, obj_id):
        return cls._get_identity_map().remove(cls, obj_id)


class HLModelMap(MutableMapping):

    def __init__(
        self,
        t: Union[Type, List],
        owner: Optional[HLDataModel] = None,
        back_populates: Optional[str] = None,
    ) -> None:
        """A typed dict that also does the book keeping to make sure
        references to the owner object is maintained

        Args
        """
        self._dict = {}

        self.owner = owner
        self.back_populates = back_populates

        # We may be dealing with repeatededly wrapped classes
        # so we use this to ensure we're adding properties to
        # the correct classes
        if isinstance(t, type):
            self._t = t
        elif _t := getattr(t, "original_class", None):
            # In this case 't' is an instance of the HasMany decorator
            self._t = _t
        elif isinstance(t, list):
            self._t = type(t[0])
            for item in t:
                self.add(item)
        else:
            raise ValueError("Could not infer HLModelMap type")

    def _validate_item(self, item) -> Union[UUID, int, str]:
        if not isinstance(item, self._t):
            raise TypeError(f"Invalid type, expected {self._t} got {type(item)}")

        id = item.get_id()
        return id

    def add(self, item):
        """Add an item to the HLModelMap and update the associated
        references
        """

        self._validate_item(item)

        if (self.owner is not None) and (self.back_populates is not None):
            # if isinstance(self.target_cls, str):
            #    target_cls = import_attr(self.target_cls)
            #    assert isinstance(target_cls, type)
            #    self.target_cls = target_cls

            # owner_inst = self.target_cls.find_by_id(self.owner_id)
            # if self.owner.get_id() != item.get_id():
            #    setattr(item, self.back_populates, self.owner)
            setattr(item, self.back_populates, self.owner)

        self._dict[item.get_id()] = item

    def remove(self, item):
        id = self._validate_item(item)
        del self._dict[id]

    def items(self):
        return self._dict.items()

    def keys(self):
        return list(self._dict.keys())

    def values(self):
        return list(self._dict.values())

    def clear(self):
        self._dict = {}

    def __len__(self):
        return len(self._dict)

    def __getitem__(self, id):
        return self._dict[id]

    def __setitem__(self, id, item):
        assert id == item.get_id()
        self.add(item)

    def __contains__(self, item):
        return (item.get_id() in self._dict) and (self._dict[item.get_id()] is item)

    def __repr__(self) -> str:
        return str(self._dict)

    def __delitem__(self, item):
        self.remove(item)

    def __iter__(self):
        return iter(self.values())


def HasMany(
    field,
    target_cls,
    back_populates,
):
    """

    Args:
        target_cls:   Import string to the class that 'is the many' class.
        field: The field of on the owner class that has the HLModelMap containing the target_cls instnaces
        back_populates: The name of the field on the target_cls that refers back to the owner instance

    Example:

        @HasMany("highlighter.client.Annotation", "annotations", "entity")
        class Entity(HLDataModel):
            id: UUID
            annotations: HLModelMap = ...

        class Annotation(HLDataModel):
            id: UUID
            entity: Entity  # Not 100% correct, but illustrative, see note.


        Note: We would normally use the 'BelongsTo' decorator on the Annotation class
        that would add and 'entity' property to the Annotation class that looks
        up the Entity instance by entity_id.
    """

    class Decorator:
        _is_decorator = True

        def __init__(self, cls):
            # We may be dealing with repeatededly wrapped classes
            # so we use this to ensure we're adding properties to
            # the correct classes
            self.cls = getattr(cls, "original_class", cls)
            self.cls._add_has_many_relationship(field, target_cls, back_populates)

        def __call__(self, *args, **kwargs):
            def transform_list_to_hlmodelmap(value):
                if isinstance(value, list):
                    return HLModelMap(value)
                return value

            for rel in self.cls._get_has_many_relationships():
                if rel["field"] in kwargs:
                    kwargs[rel["field"]] = transform_list_to_hlmodelmap(kwargs[rel["field"]])

            instance = self.cls(*args, **kwargs)
            for rel in self.cls._get_has_many_relationships():
                # TODO: instantiate field in the future
                field = getattr(instance, rel["field"])
                setattr(field, "owner", instance)
                setattr(field, "back_populates", rel["back_populates"])
            return instance

        def __getattr__(self, name):
            # Forward attribute access to the class (for class methods and attributes)
            return getattr(self.cls, name)

        @property
        def original_class(self):
            """Access the original, unwrapped class by following the __wrapped__ chain"""
            cls = self.cls
            # Follow the __wrapped__ chain until we hit the original class
            while hasattr(cls, "__wrapped__"):
                cls = cls.__wrapped__
            return cls

    return Decorator


def import_attr(item):
    import importlib

    parts = item.split(".")
    module_name = ".".join(parts[:-1])
    class_name = parts[-1]
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def BelongsTo(
    field: str,
    target_cls: Union[type, str],
    back_populates: str,
    back_populates_id_field: Optional[str] = None,
):

    if back_populates_id_field is None:
        back_populates_id_field = f"{field}_id"

    def decorator(
        cls,
        field=field,
        target_cls=target_cls,
        back_populates=back_populates,
        back_populates_id_field=back_populates_id_field,
    ):
        """

        Args:
            field: The name of the property to add to the decorated class the
            will lookup an instnace to the owner.

            target_cls: Import path to the cls that the decorated class belongs to

            back_populates: The fiend name on the owner that refers to a
            collection of the decorated class. Must be a HLModelMap.

            back_populates_id_field: The field name on the decorated class
            that refers to the owner. If None will be f'{field}_id'


        @BelongsTo(
                   "entity",
                   "highlighter.client.Entity",
                   "annotations",
                   )
        class Annotation():
          id: UUID
          entity_id: UUID

        class Entity():
          id: UUID
          annotations: HLModelMap(Annotation) ...

        """
        _cls_name = target_cls.split(".")[-1]
        if field is None:
            field = camel_to_snake(_cls_name)

        def _get_belongs_to_class(
            target_cls=target_cls,
            back_populates=back_populates,
            field=field,
            back_populates_id_field=back_populates_id_field,
        ):
            _cls = import_attr(target_cls)
            if back_populates_id_field is None:
                back_populates_id_field = f"{field}_id"
            return _cls, back_populates, field, back_populates_id_field

        # Equivalent to:
        # @property
        # def entity(self):
        #    if self.entity_id is None:
        #        return None
        #    return Entity.find_by_id(self.entity_id)
        def _getter(self):
            target_cls, _, _, back_populates_id_field = _get_belongs_to_class()
            id = getattr(self, back_populates_id_field)
            if id is None:
                return None
            return target_cls.find_by_id(id)

        # @entity.setter
        # def entity(self, v: Optional["Entity"]):
        #    if self.entity_id is None:
        #        if v is not None:
        #            self.entity_id = v.id
        #            Entity.find_by_id(v.id).annotations.add(self)

        #    else:
        #        if v is None:
        #            if self in Entity.find_by_id(self.entity_id).annotations:
        #                Entity.find_by_id(self.entity_id).annotations.remove(self)
        #            self.entity_id = None

        #        elif self not in Entity.find_by_id(v.id).annotations:
        #            self.entity_id = v.id
        #            Entity.find_by_id(v.id).annotations.add(self)
        def _setter(self, v):
            if getattr(self, "_add_in_progress", False):
                return
            target_cls, _, _, back_populates_id_field = _get_belongs_to_class()
            id = getattr(self, back_populates_id_field)
            if id is None:
                if v is not None:
                    setattr(self, back_populates_id_field, v.get_id())
                    new_belongs_to_inst = getattr(target_cls, "find_by_id")(v.get_id())

                    self._add_in_progress = True
                    getattr(new_belongs_to_inst, back_populates).add(self)
                    self._add_in_progress = False

            else:
                if v is None:
                    old_belongs_to_inst = getattr(target_cls, "find_by_id")(id)
                    old_belongs_to_collection = getattr(old_belongs_to_inst, back_populates)
                    if self in old_belongs_to_collection:
                        old_belongs_to_collection.remove(self)
                    setattr(self, back_populates_id_field, None)

                else:
                    new_belongs_to_inst = getattr(target_cls, "find_by_id")(v.get_id())
                    new_belongs_to_collection = getattr(new_belongs_to_inst, back_populates)
                    if self not in new_belongs_to_collection:
                        setattr(self, back_populates_id_field, v.get_id())

                        self._add_in_progress = True
                        new_belongs_to_collection.add(self)
                        self._add_in_progress = False

                    old_belongs_to_inst = getattr(target_cls, "find_by_id")(id)
                    old_belongs_to_collection = getattr(old_belongs_to_inst, back_populates)
                    if self in old_belongs_to_collection:
                        old_belongs_to_collection.remove(self)

        # We may be dealing with repeatededly wrapped classes
        # so we use this to ensure we're adding properties to
        # the correct classes
        original_class = getattr(cls, "original_class", cls)
        setattr(original_class, field, property(_getter, _setter))

        return original_class

    return decorator
