from exsited.exsited.refund.dto.refund_dto import RefundDetailsDTO, AccountRefundListDTO
from exsited.exsited.refund.refund_api_url import (RefundApiUrl)
from exsited.http.ab_rest_processor import ABRestProcessor


class Refund(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def details(self, id: str) -> RefundDetailsDTO:
        response = self.get(url=RefundApiUrl.DETAILS.format(id=id), response_obj=RefundDetailsDTO())
        return response

    def account_refund_list(self, id: str) -> AccountRefundListDTO:
        response = self.get(url=RefundApiUrl.ACCOUNT_REFUND_LIST.format(id=id), response_obj=AccountRefundListDTO())
        return response

    def create(self, cn_id: str, request_data: RefundDetailsDTO) -> RefundDetailsDTO:
        response = self.post(url=RefundApiUrl.CREATE.format(cn_id=cn_id), request_obj=request_data, response_obj=RefundDetailsDTO())
        return response

    def delete(self, id: str):
        response = self.delete_request(url=RefundApiUrl.REFUND_DELETE.format(id=id))
        return response

