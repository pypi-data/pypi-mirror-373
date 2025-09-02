from exsited.exsited.common.common_enum import SortDirection
from exsited.common.sdk_util import SDKUtil
from exsited.exsited.purchase_payments.dto.purchase_payments_dto import PurchasePaymentsListDTO, \
    PurchasePaymentsDetailsDTO, PurchasePaymentUpdateRequestDTO, PurchasePaymentsUpdateResponseDTO, PurchasePaymentRequestDTO, PurchasePaymentResponseDTO
from exsited.exsited.purchase_payments.purchase_payments_api_url import PurchasePaymentsApiUrl

from exsited.http.ab_rest_processor import ABRestProcessor


class PurchasePayments(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def list(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> PurchasePaymentsListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=PurchasePaymentsApiUrl.PURCHASE_PAYMENTS, params=params, response_obj=PurchasePaymentsListDTO())
        return response

    def details(self, id: str) -> PurchasePaymentsDetailsDTO:
        response = self.get(url=PurchasePaymentsApiUrl.PURCHASE_PAYMENTS_DETAILS.format(id=id),
                            response_obj=PurchasePaymentsDetailsDTO())
        return response

    def update(self, purchase_payment_id: str, request_data: PurchasePaymentUpdateRequestDTO) -> PurchasePaymentsUpdateResponseDTO:
        response = self.patch(url=PurchasePaymentsApiUrl.PURCHASE_PAYMENTS_DETAILS.format(id=purchase_payment_id),
                              request_obj=request_data, response_obj=PurchasePaymentsUpdateResponseDTO())
        return response

    def delete(self, purchase_payment_id: str) -> dict:
        response = self.delete_request(url=PurchasePaymentsApiUrl.PURCHASE_PAYMENTS_DETAILS.format(id=purchase_payment_id), response_obj={})
        return response

    def create(self, request_data: PurchasePaymentRequestDTO) -> PurchasePaymentResponseDTO:
        response = self.post(url=PurchasePaymentsApiUrl.PURCHASE_PAYMENTS, request_obj=request_data, response_obj=PurchasePaymentResponseDTO())
        return response

    def create_from_purchase_invoice(self, purchase_invoice_id: str, request_data: PurchasePaymentRequestDTO) -> PurchasePaymentResponseDTO:
        response = self.post(url=PurchasePaymentsApiUrl.PURCHASE_PAYMENTS_FROM_PURCHASE_INVOICE.format(purchase_invoice_id=purchase_invoice_id), request_obj=request_data, response_obj=PurchasePaymentResponseDTO())
        return response
