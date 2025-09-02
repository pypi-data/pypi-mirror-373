from dataclasses import dataclass
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class ReturnItemDTO(ABBaseDTO):
    itemId: str = None
    itemName: str = None
    itemUuid: str = None
    rmaReturned: str = None
    rmaRequested: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ReturnMerchandiseAuthorisationDTO(ABBaseDTO):
    id: str = None
    customerReturnStatus: str = None
    customerReturnDate: str = None
    invoiceId: str = None
    note: str = None
    receivedCount: str = None
    returns: list[ReturnItemDTO] = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None


@dataclass(kw_only=True)
class PaginationDTO(ABBaseDTO):
    records: int = None
    limit: int = None
    offset: int = None
    previousPage: str = None
    nextPage: str = None


@dataclass(kw_only=True)
class ReturnMerchandiseAuthorisationListDTO(ABBaseDTO):
    returnMerchandiseAuthorisations: list[ReturnMerchandiseAuthorisationDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class ReturnMerchandiseAuthorisationDetailsDTO(ABBaseDTO):
    returnMerchandiseAuthorisation: ReturnMerchandiseAuthorisationDTO = None



@dataclass(kw_only=True)
class InvoiceReturnMerchandiseAuthorisationListDTO(ABBaseDTO):
    invoice: ReturnMerchandiseAuthorisationListDTO = None


@dataclass(kw_only=True)
class InvoiceReturnMerchandiseAuthorisationDetailsDTO(ABBaseDTO):
    invoice: ReturnMerchandiseAuthorisationDetailsDTO = None



@dataclass(kw_only=True)
class ReceiveReturnItemDTO(ABBaseDTO):
    rmaReceiveQuantity: str = None
    itemId: str = None
    itemName: str = None
    itemUuid: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ReceiveReturnMerchandiseAuthorisationDTO(ABBaseDTO):
    id: str = None
    receiveReturns: list[ReceiveReturnItemDTO] = None
    createdBy: str = None
    createdOn: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ReceiveReturnMerchandiseAuthorisationListDTO(ABBaseDTO):
    receiveReturnMerchandiseAuthorisations: list[ReceiveReturnMerchandiseAuthorisationDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class ReceiveReturnMerchandiseAuthorisationDetailsDTO(ABBaseDTO):
    receiveReturnMerchandiseAuthorisation: ReceiveReturnMerchandiseAuthorisationDTO = None

@dataclass(kw_only=True)
class RmaReturnDataDTO(ABBaseDTO):
    rmaQuantity: str = None
    itemId: str = None
    itemName: str = None
    itemUuid: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ReturnMerchandiseAuthorisationCreationDTO(ABBaseDTO):
    id: str = None  # System-generated if not provided
    date: str = None
    note: str = None
    returns: list[RmaReturnDataDTO] = None

@dataclass(kw_only=True)
class CreateReturnMerchandiseAuthorisationDTO(ABBaseDTO):
    returnMerchandiseAuthorisations: ReturnMerchandiseAuthorisationCreationDTO = None


@dataclass(kw_only=True)
class ReceiveReturnDTO(ABBaseDTO):
    rmaReceiveQuantity: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ReceiveReturnMerchandiseAuthorisationsListDTO(ABBaseDTO):
    receiveReturns: list[ReceiveReturnDTO] = None


@dataclass(kw_only=True)
class CreateReceiveReturnMerchandiseAuthorisationsDTO(ABBaseDTO):
    receiveReturnMerchandiseAuthorisations: ReceiveReturnMerchandiseAuthorisationsListDTO = None


@dataclass(kw_only=True)
class CreateReceiveReturnMerchandiseAuthorisationDetailsDTO(ABBaseDTO):
    returnMerchandiseAuthorisation: ReturnMerchandiseAuthorisationDTO = None
