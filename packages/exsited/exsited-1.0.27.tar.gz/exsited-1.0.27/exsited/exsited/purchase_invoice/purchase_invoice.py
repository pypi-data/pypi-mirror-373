
from exsited.exsited.common.common_enum import SortDirection
from exsited.exsited.purchase_invoice.dto.purchase_invoice_dto import PurchaseInvoiceListDTO, PurchaseInvoiceDetailDTO, \
    PurchaseInvoiceAccountDetailDTO, PurchaseInvoiceCancelDTO, PurchaseInvoiceCancelDataDTO, \
    PurchaseInvoiceCancelResponseDTO, PurchaseInvoiceReactiveDataDTO, PurchaseInvoiceReactiveDTO, \
    PurchaseInvoiceReactiveResponseDTO, PurchaseInvoiceLineDetailDTO, PurchaseInvoiceRequestDTO
from exsited.exsited.purchase_invoice.purchase_invoice_api_url import PurchaseInvoiceApiUrl
from exsited.common.sdk_util import SDKUtil
from exsited.http.ab_rest_processor import ABRestProcessor


class PurchaseInvoice(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def list(self, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None) -> PurchaseInvoiceListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE, params=params, response_obj=PurchaseInvoiceListDTO())
        return response

    def details(self, id: str) -> PurchaseInvoiceDetailDTO:
        response = self.get(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE_DETAILS.format(id=id),
                            response_obj=PurchaseInvoiceDetailDTO())
        return response

    def line_details(self, id: str, uuid: str) -> PurchaseInvoiceLineDetailDTO:
        response = self.get(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE_LINE_DETAILS.format(id=id, uuid=uuid),
                            response_obj=PurchaseInvoiceLineDetailDTO())
        return response

    def account_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None) -> PurchaseInvoiceAccountDetailDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE_ACCOUNT_DETAILS.format(id=id),
                            params=params, response_obj=PurchaseInvoiceAccountDetailDTO())
        return response

    def cancel(self, id: str, request_data: PurchaseInvoiceCancelDataDTO):
        cancel_request = PurchaseInvoiceCancelDTO(purchaseInvoice=request_data)
        response = self.post(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE_CANCEL.format(id=id), request_obj=cancel_request, response_obj=PurchaseInvoiceCancelResponseDTO())
        return response

    def reactive(self, id: str, request_data: PurchaseInvoiceReactiveDataDTO):
        cancel_request = PurchaseInvoiceReactiveDTO(purchaseInvoice=request_data)
        response = self.post(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE_REACTIVE.format(id=id), request_obj=cancel_request, response_obj=PurchaseInvoiceReactiveResponseDTO())
        return response

    def delete(self, id: str):
        response = self.delete_request(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE_DELETE.format(id=id))
        return response

    def create_from_purchase_order(self, purchase_order_id: str, request_data: PurchaseInvoiceDetailDTO):
        response = self.post(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE_FROM_PURCHASE_ORDER.format(purchase_order_id=purchase_order_id), request_obj=request_data, response_obj=PurchaseInvoiceDetailDTO())
        return response

    def create(self, request_data: PurchaseInvoiceRequestDTO):
        response = self.post(url=PurchaseInvoiceApiUrl.PURCHASE_INVOICE, request_obj=request_data, response_obj=PurchaseInvoiceDetailDTO())
        return response
