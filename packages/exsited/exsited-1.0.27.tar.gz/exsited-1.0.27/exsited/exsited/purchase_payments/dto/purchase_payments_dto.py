from dataclasses import dataclass
from exsited.exsited.common.dto.common_dto import CustomAttributesDTO, CustomObjectDTO, PaginationDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class PurchasePaymentAppliedDTO(ABBaseDTO):
    id: str = None
    amount: str = None
    method: str = None
    processor: str = None
    reference: str = None


@dataclass(kw_only=True)
class PurchaseCreditAppliedDTO(ABBaseDTO):
    id: str = None
    amount: float = None


@dataclass(kw_only=True)
class PurchaseInvoiceDTO(ABBaseDTO):
    applied: float = None
    id: str = None
    dueDate: str = None
    issueDate: str = None
    outstanding: float = None
    total: float = None
    amount: str = None


@dataclass(kw_only=True)
class PurchasePaymentDTO(ABBaseDTO):
    status: str = None
    id: str = None
    purchasePaymentDate: str = None
    totalApplied: str = None
    purchaseOrderId: str = None
    purchasePaymentNote: str = None
    purchasePaymentApplied: list[PurchasePaymentAppliedDTO] = None
    purchaseCreditApplied: list[PurchaseCreditAppliedDTO] = None
    purchaseInvoices: list[PurchaseInvoiceDTO] = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list[CustomAttributesDTO] = None
    customObjects: list[CustomObjectDTO] = None
    date: str = None
    note: str = None
    effectiveDate: str = None


@dataclass(kw_only=True)
class PurchasePaymentUpdateDataDTO(ABBaseDTO):
    date: str = None
    note: str = None
    customAttributes: list[CustomAttributesDTO] = None


@dataclass(kw_only=True)
class PurchasePaymentUpdateRequestDTO(ABBaseDTO):
    purchasePayment: PurchasePaymentUpdateDataDTO = None


@dataclass(kw_only=True)
class PurchasePaymentsListDTO(ABBaseDTO):
    purchasePayments: list[PurchasePaymentDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PurchasePaymentsDetailsDTO(ABBaseDTO):
    purchasePayments: PurchasePaymentDTO = None


@dataclass(kw_only=True)
class PurchasePaymentsUpdateResponseDTO(ABBaseDTO):
    purchasePayment: PurchasePaymentDTO = None


@dataclass(kw_only=True)
class PurchasePaymentRequestDTO(ABBaseDTO):
    purchasePayment: PurchasePaymentDTO = None

@dataclass(kw_only=True)
class PurchasePaymentResponseDTO(ABBaseDTO):
    purchasePayment: PurchasePaymentDTO = None
