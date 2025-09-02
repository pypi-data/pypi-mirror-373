from exsited.sdlize.dto_base import DTOBase, PropsModType


class ABBaseDTO(DTOBase):
    def set_serialize_conf(self):
        self._props_mod_type = PropsModType.CAMEL_TO_SNAKE

    def set_deserialize_conf(self):
        self._props_mod_type = PropsModType.SNAKE_TO_CAMEL
