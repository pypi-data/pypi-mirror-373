from exsited.exsited.common.common_enum import SortDirection
from exsited.exsited.payment.dto.payment_dto import PaymentDetailsDTO, PaymentCreateDTO, CardPaymentCreateDTO, \
    CardDirectDebitPaymentCreateDTO, PaymentInvoiceResponseDTO, PaymentListDTO, PaymentAccountResponseDTO, \
    PaymentOrderResponseDTO, PaymentMultipleRequestDTO
from exsited.exsited.payment.payment_api_url import PaymentApiUrl
from exsited.common.sdk_util import SDKUtil
from exsited.http.ab_rest_processor import ABRestProcessor

class Payment(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def create(self, invoice_id: str, request_data: PaymentCreateDTO) -> PaymentDetailsDTO:
        response = self.post(url=PaymentApiUrl.PAYMENT_CREATE.format(invoice_id=invoice_id), request_obj=request_data, response_obj=PaymentDetailsDTO())
        return response

    def invoice_details(self, id: str) -> PaymentInvoiceResponseDTO:
        response = self.get(url=PaymentApiUrl.PAYMENT_DETAILS_INVOICE.format(id=id), response_obj=PaymentInvoiceResponseDTO)
        return response

    def list(self, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None) -> PaymentListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=PaymentApiUrl.PAYMENT_LIST, params=params, response_obj=PaymentListDTO())
        return response

    def details(self, id: str) -> PaymentDetailsDTO:
        response = self.get(url=PaymentApiUrl.PAYMENT_DETAILS.format(id=id), response_obj=PaymentDetailsDTO())
        return response

    def account_details(self, id: str) -> PaymentAccountResponseDTO:
        response = self.get(url=PaymentApiUrl.PAYMENT_ACCOUNT_DETAILS.format(id=id), response_obj=PaymentAccountResponseDTO())
        return response

    def order_details(self, id: str) -> PaymentOrderResponseDTO:
        response = self.get(url=PaymentApiUrl.PAYMENT_ORDER_DETAILS.format(id=id), response_obj=PaymentOrderResponseDTO())
        return response

    def delete(self, id: str):
        response = self.delete_request(url=PaymentApiUrl.PAYMENT_DELETE.format(id=id))
        return response