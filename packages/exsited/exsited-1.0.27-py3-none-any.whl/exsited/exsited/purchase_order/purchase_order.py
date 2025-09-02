
from exsited.exsited.common.common_enum import SortDirection
from exsited.exsited.purchase_order.dto.purchase_order_dto import PurchaseOrderDetailsDTO, PurchaseOrderListDTO, \
    PurchaseOrderDTO, PurchaseOrderCreateDTO, PurchaseOrderDataDTO, PurchaseOrderLineUuidDetailsDTO, \
    PurchaseOrderChangeDTO
from exsited.exsited.purchase_order.purchase_order_api_url import PurchaseOrderApiUrl
from exsited.common.sdk_util import SDKUtil
from exsited.http.ab_rest_processor import ABRestProcessor


class PurchaseOrder(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def list(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> PurchaseOrderListDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=PurchaseOrderApiUrl.PURCHASE_ORDERS, params=params, response_obj=PurchaseOrderListDTO())
        return response

    def details(self, id: str) -> PurchaseOrderDetailsDTO:
        response = self.get(url=PurchaseOrderApiUrl.PURCHASE_ORDER_DETAILS.format(id=id),
                            response_obj=PurchaseOrderDetailsDTO())
        return response

    def delete(self, id: str) -> PurchaseOrderDetailsDTO:
        response = self.delete_request(url=PurchaseOrderApiUrl.PURCHASE_ORDER_DELETE.format(id=id),
                            response_obj=PurchaseOrderDetailsDTO())
        return response

    def reactivate(self, id: str) -> PurchaseOrderDetailsDTO:

        response = self.post(url=PurchaseOrderApiUrl.PURCHASE_ORDER_REACTIVATE.format(id=id),
                             response_obj=PurchaseOrderDetailsDTO())
        return response

    def cancel(self, id: str) -> PurchaseOrderDetailsDTO:
        response = self.post(url=PurchaseOrderApiUrl.PURCHASE_ORDER_CANCEL.format(id=id),
                             response_obj=PurchaseOrderDetailsDTO())
        return response

    def information(self, id: str) -> PurchaseOrderDetailsDTO:
        response = self.get(url=PurchaseOrderApiUrl.PURCHASE_ORDER_INFO.format(id=id),
                            response_obj=PurchaseOrderDetailsDTO())
        return response

    def line_uuid(self, id: str, uuid:str) -> PurchaseOrderLineUuidDetailsDTO:
        response = self.get(url=PurchaseOrderApiUrl.PURCHASE_ORDER_LINE_UUID.format(id=id, uuid=uuid),
                            response_obj=PurchaseOrderLineUuidDetailsDTO())
        return response

    def po_line(self, id: str) -> PurchaseOrderDetailsDTO:
        response = self.get(url=PurchaseOrderApiUrl.PURCHASE_ORDER_LINE.format(id=id),
                            response_obj=PurchaseOrderDetailsDTO())
        return response

    def create(self, request_data: PurchaseOrderCreateDTO) -> PurchaseOrderDetailsDTO:
        response = self.post(url=PurchaseOrderApiUrl.PURCHASE_ORDERS,
                             request_obj=request_data,
                             response_obj=PurchaseOrderDetailsDTO())
        return response

    def purchase_order_change(self, id:str, request_data: PurchaseOrderChangeDTO) -> PurchaseOrderDetailsDTO:
        response = self.post(url=PurchaseOrderApiUrl.PURCHASE_ORDER_CHANGE.format(id=id),
                             request_obj=request_data,
                             response_obj=PurchaseOrderDetailsDTO())
        return response
