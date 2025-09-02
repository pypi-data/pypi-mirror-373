from exsited.exsited.common.common_enum import SortDirection


class SDKUtil:

    @staticmethod
    def get_dict_value(data: dict, key: str, default=None):
        if not data or not key:
            return default
        elif key in data:
            return data[key]
        return default

    @staticmethod
    def init_dict_if_value(data: dict, key: str, value):
        if value:
            data[key] = value
        return data

    @staticmethod
    def init_pagination_params(params: dict = None, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None):
        if not params:
            params = {}
        params = SDKUtil.init_dict_if_value(params, "limit", limit)
        params = SDKUtil.init_dict_if_value(params, "offset", offset)
        params = SDKUtil.init_dict_if_value(params, "direction", str(direction))
        params = SDKUtil.init_dict_if_value(params, "order_by", order_by)
        return params
