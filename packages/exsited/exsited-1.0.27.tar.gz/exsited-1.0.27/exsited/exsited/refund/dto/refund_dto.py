from dataclasses import dataclass
from exsited.exsited.common.dto.common_dto import PaginationDTO, CustomAttributesDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class RefundDataDTO(ABBaseDTO):
    status: str = None
    id: str = None
    amount: str = None
    reference: str = None
    note: str = None
    paymentMethod: str = None
    paymentProcessor: str = None
    gatewayResponse: str = None
    creditNoteId: str = None
    customAttributes: list[CustomAttributesDTO] = None
    version: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    date: str = None


@dataclass(kw_only=True)
class RefundDetailsDTO(ABBaseDTO):
    refund: RefundDataDTO = None


@dataclass(kw_only=True)
class RefundListDTO(ABBaseDTO):
    refunds: list[RefundDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class AccountRefundListDTO(ABBaseDTO):
    account: RefundListDTO = None
