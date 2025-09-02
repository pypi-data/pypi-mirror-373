from exsited.exsited.common.common_enum import SortDirection
from exsited.exsited.order.dto.order_dto import OrderCreateDTO, OrderDetailsDTO, OrderListDTO, OrderCancelResponseDTO, \
    OrderUpgradeDowngradeDTO, OrderDowngradeDetailsDTO, ContractAdjustmentPreviewResponseDTO, OrderDowngradePreviewDTO, \
    ContractAdjustmentPreviewRequestDTO, OrderUpgradePreviewDTO, OrderDowngradeDTO, OrderUpgradeDTO, \
    OrderPaymentMethodsResponseDTO
from exsited.exsited.order.dto.order_nested_dto import ContractAdjustmentPreviewDTO
from exsited.exsited.order.dto.order_dto import OrderCreateDTO, OrderDetailsDTO, OrderListDTO, OrderCancelResponseDTO, \
    AccountOrdersResponseDTO
from exsited.exsited.order.dto.order_nested_dto import OrderLineDTO
from exsited.exsited.order.dto.usage_dto import UsageCreateDTO, UsageDataDTO, UsageListDTO, UsageModifyDataDTO, \
    UsageUpdateDataDTO, MultipleUsageCreateDTO, MultipleUsageResponseDTO
from exsited.exsited.order.order_api_url import OrderApiUrl
from exsited.common.sdk_util import SDKUtil
from exsited.http.ab_rest_processor import ABRestProcessor


class Order(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def create(self, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.post(url=OrderApiUrl.ORDERS, request_obj=request_data, response_obj=OrderDetailsDTO())
        return response

    def list(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> OrderListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=OrderApiUrl.ORDERS, params=params, response_obj=OrderListDTO())
        return response

    def usage_list(self, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None) -> UsageListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=OrderApiUrl.USAGE_LIST, params=params, response_obj=UsageListDTO())
        return response

    def details(self, id: str) -> OrderDetailsDTO:
        response = self.get(url=OrderApiUrl.ORDERS + f"/{id}", response_obj=OrderDetailsDTO())
        return response

    def usage_details(self, uuid: str) -> UsageDataDTO:
        response = self.get(url=OrderApiUrl.USAGE_DETAILS + f"/{uuid}", response_obj=UsageDataDTO())
        return response

    def usage_modify(self, uuid: str, request_data: UsageCreateDTO) -> UsageDataDTO:
        response = self.patch(url=OrderApiUrl.USAGE_MODIFY.format(uuid=uuid),request_obj=request_data, response_obj=UsageModifyDataDTO())
        return response

    def usage_update(self, uuid: str, request_data: UsageCreateDTO) -> UsageDataDTO:
        response = self.put(url=OrderApiUrl.USAGE_UPDATE.format(uuid=uuid),request_obj=request_data, response_obj=UsageUpdateDataDTO())
        return response

    def usage_delete(self, uuid: str):
        response = self.delete_request(url=OrderApiUrl.USAGE_DELETE.format(uuid=uuid))
        return response


    def cancel(self, id: str, effective_date: str) -> OrderCancelResponseDTO:
        response = self.post(url=OrderApiUrl.ORDER_CANCEL.format(id=id),
                             json_dict={"order": {"effective_date": effective_date}},
                             response_obj=OrderCancelResponseDTO())
        return response

    def add_usage(self, request_data: UsageCreateDTO) -> UsageDataDTO:
        response = self.post(url=OrderApiUrl.USAGE_ADD, request_obj=request_data, response_obj=UsageCreateDTO())
        return response

    def add_multiple_usage(self, request_data: MultipleUsageCreateDTO) -> MultipleUsageResponseDTO:
        response = self.post(url=OrderApiUrl.USAGE_ADD, request_obj=request_data, response_obj=MultipleUsageResponseDTO())
        return response

    def create_with_purchase(self, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.post(url=OrderApiUrl.PURCHASE_ORDER_CREATE, request_obj=request_data,
                             response_obj=OrderDetailsDTO())
        return response

    def create_with_contract(self, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.post(url=OrderApiUrl.CONTRACT_ORDER_CREATE, request_obj=request_data,
                             response_obj=OrderDetailsDTO())
        return response

    def upgrade(self, order_id: str, request_data: OrderUpgradeDTO) -> OrderDetailsDTO:
        response = self.post(url=OrderApiUrl.ORDER_UPGRADE.format(id=order_id), request_obj=request_data,
                             response_obj=OrderDetailsDTO())
        return response

    def contract_adjustment(self, order_id: str, request_data: ContractAdjustmentPreviewRequestDTO) -> ContractAdjustmentPreviewResponseDTO:
        response = self.post(url=OrderApiUrl.CONTRACT_ADJUSTMENT.format(id=order_id), request_obj=request_data,
                             response_obj=ContractAdjustmentPreviewResponseDTO())
        return response

    def upgrade_preview(self, order_id: str, request_data: OrderUpgradePreviewDTO) -> OrderUpgradeDowngradeDTO:
        response = self.post(url=OrderApiUrl.ORDER_UPGRADE_PREVIEW.format(id=order_id), request_obj=request_data,
                             response_obj=OrderUpgradeDowngradeDTO())
        return response

    def downgrade(self, order_id: str, request_data: OrderDowngradeDTO) -> OrderDowngradeDetailsDTO:
        response = self.post(url=OrderApiUrl.ORDER_DOWNGRADE.format(id=order_id), request_obj=request_data,
                             response_obj=OrderDowngradeDetailsDTO())
        return response

    def downgrade_preview(self, order_id: str, request_data: OrderDowngradePreviewDTO) -> OrderUpgradeDowngradeDTO:
        response = self.post(url=OrderApiUrl.ORDER_DOWNGRADE_PREVIEW.format(id=order_id), request_obj=request_data,
                             response_obj=OrderUpgradeDowngradeDTO())
        return response

    def reactivate(self, id: str, effective_date: str) -> OrderCancelResponseDTO:
        response = self.post(url=OrderApiUrl.ORDER_REACTIVATE.format(id=id),
                             json_dict={"order": {"effective_date": effective_date}},
                             response_obj=OrderCancelResponseDTO())
        return response

    def preorder(self, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.post(url=OrderApiUrl.ORDER_PREORDER, request_obj=request_data, response_obj=OrderDetailsDTO())
        return response

    def change(self, id: str, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.post(url=OrderApiUrl.ORDER_CHANGE.format(id=id),
                             request_obj=request_data,
                             response_obj=OrderDetailsDTO())
        return response

    def delete(self, id: str):
        response = self.delete_request(url=OrderApiUrl.ORDER_DELETE.format(id=id), response_obj={})
        return response

    def order_quote_pdf(self, id: str):
        response = self.get(url=OrderApiUrl.ORDER_QUOTE_PDF.format(id=id))
        return response

    def information(self, id: str) -> OrderDetailsDTO:
        response = self.get(url=OrderApiUrl.ORDER_INFORMATION.format(id=id), response_obj=OrderDetailsDTO())
        return response

    def billing_preferences(self, id: str) -> OrderDetailsDTO:
        response = self.get(url=OrderApiUrl.ORDER_BILLING_PREFERENCES.format(id=id), response_obj=OrderDetailsDTO())
        return response

    def lines(self, id: str) -> OrderDetailsDTO:
        response = self.get(url=OrderApiUrl.ORDER_LINES.format(id=id), response_obj=OrderDetailsDTO())
        return response

    def lines_charge(self, id: str, charge_uuid: str) -> OrderDetailsDTO:
        response = self.get(url=OrderApiUrl.ORDER_LINES_CHARGE.format(id=id, uuid=charge_uuid),
                            response_obj=OrderDetailsDTO())
        return response

    def account_list(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
                     order_by: str = None) -> AccountOrdersResponseDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=OrderApiUrl.ORDERS_ACCOUNT.format(id=id), params=params,
                            response_obj=AccountOrdersResponseDTO())
        return response

    def update_information(self, id: str, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.patch(url=OrderApiUrl.ORDER_INFORMATION.format(id=id), request_obj=request_data,
                              response_obj=OrderDetailsDTO())
        return response

    def update_line_information(self, id: str, uuid: str, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.patch(url=OrderApiUrl.ORDER_LINES_INFORMATION.format(id=id, uuid=uuid),
                              request_obj=request_data, response_obj=OrderDetailsDTO())
        return response

    def update_billing_preference(self, id: str, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.put(url=OrderApiUrl.ORDER_BILLING_PREFERENCES.format(id=id),
                            request_obj=request_data, response_obj=OrderDetailsDTO())
        return response

    def fill_in_billing_preference(self, id: str, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.patch(url=OrderApiUrl.ORDER_BILLING_PREFERENCES.format(id=id),
                            request_obj=request_data, response_obj=OrderDetailsDTO())
        return response

    def relinquish(self, id: str, request_data: OrderCreateDTO) -> OrderDetailsDTO:
        response = self.post(url=OrderApiUrl.ORDER_RELINQUISH.format(id=id),
                             request_obj=request_data, response_obj=OrderDetailsDTO())
        return response

    def payment_methods(self, id: str) -> OrderPaymentMethodsResponseDTO:
        response = self.get(url=OrderApiUrl.PAYMENT_METHODS.format(id=id), response_obj=OrderPaymentMethodsResponseDTO())
        return response