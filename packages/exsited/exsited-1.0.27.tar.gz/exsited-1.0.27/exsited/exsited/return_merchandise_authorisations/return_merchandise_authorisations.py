from exsited.exsited.common.common_enum import SortDirection
from exsited.common.sdk_util import SDKUtil
from exsited.exsited.return_merchandise_authorisations.dto.return_merchandise_authorisations_dto import \
    ReturnMerchandiseAuthorisationListDTO, ReturnMerchandiseAuthorisationDetailsDTO, \
    InvoiceReturnMerchandiseAuthorisationListDTO, InvoiceReturnMerchandiseAuthorisationDetailsDTO, \
    ReceiveReturnMerchandiseAuthorisationListDTO, ReceiveReturnMerchandiseAuthorisationDetailsDTO, \
    CreateReturnMerchandiseAuthorisationDTO, CreateReceiveReturnMerchandiseAuthorisationsDTO, \
    CreateReceiveReturnMerchandiseAuthorisationDetailsDTO
from exsited.exsited.return_merchandise_authorisations.return_merchandise_authorisations_api_url import \
    ReturnMerchandiseAuthorisationsApiUrl
from exsited.http.ab_rest_processor import ABRestProcessor


class ReturnMerchandiseAuthorisations(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)
    def list(self, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None) -> ReturnMerchandiseAuthorisationListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=ReturnMerchandiseAuthorisationsApiUrl.LIST, params=params, response_obj=ReturnMerchandiseAuthorisationListDTO())
        return response

    def receive_list(self, id: str, rma_id: str, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None) -> ReceiveReturnMerchandiseAuthorisationListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=ReturnMerchandiseAuthorisationsApiUrl.RECEIVE_LIST.format(id=id, rma_id=rma_id), params=params, response_obj=ReceiveReturnMerchandiseAuthorisationListDTO())
        return response

    def details(self, id: str) -> ReturnMerchandiseAuthorisationDetailsDTO:
        response = self.get(url=ReturnMerchandiseAuthorisationsApiUrl.LIST + f"/{id}", response_obj=ReturnMerchandiseAuthorisationDetailsDTO())
        return response

    def receive_details(self, id: str, rma_id: str, rec_id: str) -> ReceiveReturnMerchandiseAuthorisationDetailsDTO:
        response = self.get(url=ReturnMerchandiseAuthorisationsApiUrl.RECEIVE_DETAILS.format(id=id, rma_id=rma_id, rec_id=rec_id), response_obj=ReceiveReturnMerchandiseAuthorisationDetailsDTO())
        return response

    def invoice_list(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None) -> InvoiceReturnMerchandiseAuthorisationListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=ReturnMerchandiseAuthorisationsApiUrl.INVOICE_RMA_LIST.format(id=id), params=params, response_obj=InvoiceReturnMerchandiseAuthorisationListDTO())
        return response

    def invoice_rma_details(self, id: str, rma_id: str) -> InvoiceReturnMerchandiseAuthorisationDetailsDTO:
        response = self.get(url=ReturnMerchandiseAuthorisationsApiUrl.INVOICE_RMA_DETAILS.format(id=id, rma_id=rma_id), response_obj=InvoiceReturnMerchandiseAuthorisationDetailsDTO())
        return response

    def invoice_rma_create(self, id: str, request_data: CreateReturnMerchandiseAuthorisationDTO) -> InvoiceReturnMerchandiseAuthorisationDetailsDTO:
        response = self.post(url=ReturnMerchandiseAuthorisationsApiUrl.INVOICE_RMA_CREATE.format(id=id), request_obj=request_data, response_obj=InvoiceReturnMerchandiseAuthorisationDetailsDTO())
        return response

    def invoice_receive_rma_create(self, id: str, rma_id: str, request_data: CreateReceiveReturnMerchandiseAuthorisationsDTO) -> CreateReceiveReturnMerchandiseAuthorisationDetailsDTO:
        response = self.post(url=ReturnMerchandiseAuthorisationsApiUrl.INVOICE_RECEIVE_RMA_CREATE.format(id=id, rma_id=rma_id), request_obj=request_data, response_obj=CreateReceiveReturnMerchandiseAuthorisationDetailsDTO())
        return response
