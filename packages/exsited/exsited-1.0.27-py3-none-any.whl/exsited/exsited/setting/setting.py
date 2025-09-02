from exsited.common.sdk_util import SDKUtil
from exsited.exsited.common.common_enum import SortDirection
from exsited.exsited.setting.dto.setting_dto import SettingPaymentProcessorListDTO, SettingPricingLevelsListDTO, \
    ItemGroupListDTO, CurrenciesResponseDTO, TaxesResponseDTO, DiscountProfilesResponseDTO, WarehousesResponseDTO, \
    VariationsResponseDTO, ComponentResponseDTO, ShippingProfilesResponseDTO, VariationCreateRequestDTO, \
    VariationUpdateResponseDTO
from exsited.http.ab_rest_processor import ABRestProcessor
from exsited.exsited.setting.setting_api_url import SettingApiUrl


class Setting(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)
    def get_settings(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None):
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS, params=params, response_obj={})
        return response

    def get_settings_payment_processor(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> SettingPaymentProcessorListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_PAYMENT_PROCESSOR, params=params, response_obj=SettingPaymentProcessorListDTO())
        return response

    def get_settings_pricing_levels(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> SettingPricingLevelsListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_PRICING_LEVELS, params=params, response_obj=SettingPricingLevelsListDTO())
        return response

    def get_settings_item_group(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> ItemGroupListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_ITEM_GROUPS, params=params, response_obj=ItemGroupListDTO())
        return response

    def get_settings_currencies(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> CurrenciesResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_CURRENCIES, params=params, response_obj=CurrenciesResponseDTO())
        return response

    def get_settings_taxes(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> TaxesResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_TAXES, params=params, response_obj=TaxesResponseDTO())
        return response

    def get_settings_discount_profiles(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> DiscountProfilesResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_DISCOUNT_PROFILES, params=params, response_obj=DiscountProfilesResponseDTO())
        return response

    def get_settings_warehouses(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> WarehousesResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_WAREHOUSES, params=params, response_obj=WarehousesResponseDTO())
        return response

    def get_settings_shipping_profiles(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> ShippingProfilesResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_SHIPPING_PROFILES, params=params, response_obj=ShippingProfilesResponseDTO())
        return response

    def get_settings_components(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> ComponentResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_COMPONENT, params=params, response_obj=ComponentResponseDTO())
        return response

    def get_settings_variations(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> VariationsResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=SettingApiUrl.SETTINGS_VARIATIONS, params=params, response_obj=VariationsResponseDTO())
        return response

    def variation_update(self, uuid: str, request_data: VariationCreateRequestDTO) -> VariationUpdateResponseDTO:
        response = self.patch(url=SettingApiUrl.SETTINGS_VARIATIONS_UPDATE.format(uuid=uuid), request_obj=request_data,
                              response_obj=VariationUpdateResponseDTO())
        return response





