import dataclasses
from enum import Enum
import re
from types import GenericAlias


class PropsModType(Enum):
    CAMEL_TO_SNAKE = "CAMEL_TO_SNAKE"
    SNAKE_TO_CAMEL = "SNAKE_TO_CAMEL"


class DTOBase(object):
    _exclude_props_mod: dict = {}
    _props_mod_type: PropsModType = None
    _camel_to_snake_regex = re.compile(r"(?<!^)(?=[A-Z])")
    _include_null: bool = False

    def convert_snake_to_camel_case(self, text: str) -> str:
        camel_cased = "".join(x.capitalize() for x in text.lower().split("_"))
        if camel_cased:
            return camel_cased[0].lower() + camel_cased[1:]
        else:
            return camel_cased

    def convert_camel_to_snake_case(self, text: str) -> str:
        return self._camel_to_snake_regex.sub("_", text).lower()

    def _get_property_modifier(self):
        if not self._props_mod_type:
            return None
        elif self._props_mod_type == PropsModType.CAMEL_TO_SNAKE:
            return self.convert_camel_to_snake_case
        elif self._props_mod_type == PropsModType.SNAKE_TO_CAMEL:
            return self.convert_snake_to_camel_case
        return None

    def _load_data_class(cls, data: dict):
        if not dataclasses.is_dataclass(cls):
            raise ValueError(f"{cls.__name__} must be a dataclass")
        if not isinstance(data, dict):
            raise ValueError(f"Unable to load dictionary from {cls.__name__}")
        cls.set_deserialize_conf(cls)
        kwargs = cls._get_load_kwargs(cls, data=data)
        return cls(**kwargs)

    def _get_collection_args(self, object_class, index):
        if hasattr(object_class, "__args__") and len(getattr(object_class, "__args__")) > index:
            return getattr(object_class, "__args__")[index]
        return None

    def _load_generic_alias_data(cls, field_type, values):
        generic_class_name = cls._get_collection_args(cls, field_type, 0)
        object_list = []
        for value in values:
            object_list.append(cls._load_data_class(generic_class_name, data=value))
        return object_list

    def _get_load_kwargs(cls, data: dict):
        property_modifier = cls._get_property_modifier(cls)
        field_name_type = {field.name: field.type for field in dataclasses.fields(cls)}
        kwargs = {}

        custom_field_mapping = getattr(cls, "_custom_field_mapping", {})

        for key, value in data.items():
            if property_modifier and (not cls._exclude_props_mod or key not in cls._exclude_props_mod):
                key = property_modifier(cls, text=key)

            if key in custom_field_mapping:
                mapped_key = custom_field_mapping[key]
                kwargs[mapped_key] = value
            elif key in field_name_type:
                field_type = field_name_type[key]
                if isinstance(value, list) and isinstance(field_type, GenericAlias):
                    kwargs[key] = cls._load_generic_alias_data(cls, field_type=field_type, values=value)
                elif isinstance(value, dict) and issubclass(field_type, DTOBase):
                    kwargs[key] = cls._load_data_class(field_type, data=value)
                else:
                    kwargs[key] = value
        return kwargs

    @classmethod
    def load_dict(cls, data: dict):
        return cls._load_data_class(cls, data=data)

    def _dict_factory(self, fields):
        dict_field = {}
        property_modifier = self._get_property_modifier()

        custom_field_mapping = getattr(self.__class__, "_custom_field_mapping", {})

        for (key, value) in fields:
            if key in custom_field_mapping.values():
                key = next(k for k, v in custom_field_mapping.items() if v == key)
            elif property_modifier and (not self._exclude_props_mod or key not in self._exclude_props_mod):
                key = property_modifier(text=key)

            if value is not None or self._include_null:
                dict_field[key] = value
        return dict_field

    def to_dict(self, include_null=False):
        self._include_null = include_null
        self.set_serialize_conf()
        return dataclasses.asdict(self, dict_factory=self._dict_factory)

    def set_serialize_conf(self):
        pass

    def set_deserialize_conf(self):
        pass