from exsited.exsited.common.common_enum import SortDirection
from exsited.common.sdk_util import SDKUtil
from exsited.exsited.credit_note.credit_note_api_url import CreditNoteApiUrl
from exsited.exsited.credit_note.dto.credit_note_dto import CreditNoteDTO, CreditNoteDetailsDTO, \
    CreditNoteApplicationListDTO, CreditNoteApplicationDetailDTO, InvoiceCreditNoteApplicationListDTO
from exsited.http.ab_rest_processor import ABRestProcessor


class CreditNote(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)
    def details(self, id: str) -> CreditNoteDetailsDTO:
        response = self.get(url=CreditNoteApiUrl.DETAILS.format(id=id), response_obj=CreditNoteDetailsDTO())
        return response

    def credit_note_application_list(self) -> CreditNoteApplicationListDTO:
        response = self.get(url=CreditNoteApiUrl.APPLICATION_LIST, response_obj=CreditNoteApplicationListDTO())
        return response

    def credit_note_application_details(self, uuid: str) -> CreditNoteApplicationDetailDTO:
        response = self.get(url=CreditNoteApiUrl.APPLICATION_DETAILS.format(uuid=uuid), response_obj=CreditNoteApplicationDetailDTO())
        return response

    def invoice_credit_note_application_list(self, id: str) -> InvoiceCreditNoteApplicationListDTO:
        response = self.get(url=CreditNoteApiUrl.INVOICE_CN_APPLICATION_LIST.format(id=id), response_obj=InvoiceCreditNoteApplicationListDTO())
        return response
