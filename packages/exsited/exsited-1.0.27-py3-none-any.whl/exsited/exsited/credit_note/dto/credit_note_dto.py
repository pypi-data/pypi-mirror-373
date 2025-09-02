from dataclasses import dataclass

from exsited.exsited.common.dto.common_dto import PaginationDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO

@dataclass(kw_only=True)
class CustomAttributesDetailsDTO(ABBaseDTO):
    name: str = None
    value: str = None

@dataclass(kw_only=True)
class CreditNoteDTO(ABBaseDTO):
    status: str = None
    id: str = None
    date: str = None
    amount: str = None
    invoiceId: str = None
    remainingBalance: str = None
    refundable: str = None
    paymentId: str = None
    customAttributes: list[CustomAttributesDetailsDTO] = None
    customObjects: list = None
    version: str = None
    createdBy: str = None
    createdOn: str = None
    updatedBy: str = None
    updatedOn: str = None
    uuid: str = None
    accountId: str = None


@dataclass(kw_only=True)
class CreditNoteApplicationDTO(ABBaseDTO):
    date: str = None
    amount: str = None
    creditNoteId: str = None
    paymentId: str = None
    refundId: str = None
    remainingBalance: str = None
    createdBy: str = None
    createdOn: str = None
    uuid: str = None
    version: str = None



@dataclass(kw_only=True)
class CreditNoteDetailsDTO(ABBaseDTO):
    creditNote: CreditNoteDTO = None


@dataclass(kw_only=True)
class CreditNoteApplicationListDTO(ABBaseDTO):
    creditNoteApplications: list[CreditNoteApplicationDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class CreditNoteApplicationDetailDTO(ABBaseDTO):
    creditNoteApplication: CreditNoteApplicationDTO = None

@dataclass(kw_only=True)
class InvoiceCreditNoteApplicationListDTO(ABBaseDTO):
    invoice: CreditNoteApplicationListDTO = None

