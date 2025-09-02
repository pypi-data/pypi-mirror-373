from dataclasses import dataclass
from exsited.exsited.common.dto.common_dto import CustomAttributesDTO, CustomObjectDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO

@dataclass(kw_only=True)
class PaymentAppliedDTO(ABBaseDTO):
    processor: str = None
    amount: float = None
    reference: str = None
    method: str = None

@dataclass(kw_only=True)
class CardPaymentAppliedDTO(PaymentAppliedDTO):
    cardType: str = None
    token: str = None
    cardNumber: str = None
    expiryMonth: str = None
    expiryYear: str = None
    additionalFields: dict = None

@dataclass(kw_only=True)
class CreditAppliedDTO(ABBaseDTO):
    id: str = None
    amount: str = None
    code: str = None


@dataclass(kw_only=True)
class giftCertificateAppliedDTO(ABBaseDTO):
    code: str = None
    amount: str = None


@dataclass(kw_only=True)
class InvoiceDTO(ABBaseDTO):
    applied: float = None
    code: str = None
    dueDate: str = None
    issueDate: str = None
    outstanding: float = None
    total: float = None

@dataclass(kw_only=True)
class PaymentDataDTO(ABBaseDTO):
    id: str = None
    date: str = None
    status: str = None
    reconcileStatus: str = None
    totalApplied: float = None
    paymentApplied: list[PaymentAppliedDTO] = None
    note: str = None
    creditApplied: list[CreditAppliedDTO] = None
    invoices: list[InvoiceDTO] = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    saleOrderId: str = None
    customAttributes: list[CustomAttributesDTO] = None
    customObjects: list[CustomObjectDTO] = None
    giftCertificateApplied: list[giftCertificateAppliedDTO] = None


@dataclass(kw_only=True)
class CardPaymentDataDTO(PaymentDataDTO):
    paymentApplied: list[CardPaymentAppliedDTO] = None

@dataclass(kw_only=True)
class PaymentDetailsDTO(ABBaseDTO):
    payment: PaymentDataDTO = None

@dataclass(kw_only=True)
class PaymentCreateDTO(ABBaseDTO):
    payment: PaymentDataDTO = None

@dataclass(kw_only=True)
class CardPaymentCreateDTO(ABBaseDTO):
    payment: CardPaymentDataDTO = None

# New DTO for the given payload
@dataclass(kw_only=True)
class CardDirectDebitPaymentAppliedDTO(PaymentAppliedDTO):
    method: str = None

@dataclass(kw_only=True)
class CardDirectDebitPaymentDataDTO(ABBaseDTO):
    date: str = None
    paymentApplied: list[CardDirectDebitPaymentAppliedDTO] = None

@dataclass(kw_only=True)
class CardDirectDebitPaymentCreateDTO(ABBaseDTO):
    payment: CardDirectDebitPaymentDataDTO = None


@dataclass(kw_only=True)
class PaginationDTO(ABBaseDTO):
    records: int = None
    limit: int = None
    offset: int = None
    previousPage: str = None
    nextPage: str = None

@dataclass(kw_only=True)
class PaymentListDTO(ABBaseDTO):
    payments: list[PaymentDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PaymentInvoiceResponseDTO(ABBaseDTO):
    invoice: PaymentListDTO = None


@dataclass(kw_only=True)
class PaymentAccountResponseDTO(ABBaseDTO):
    account: PaymentListDTO = None


@dataclass(kw_only=True)
class PaymentOrderResponseDTO(ABBaseDTO):
    order: PaymentListDTO = None



@dataclass(kw_only=True)
class CustomAttributeDTO:
    name: str
    value: str

@dataclass(kw_only=True)
class InvoiceMultipleDTO:
    id: str
    amount: str

@dataclass(kw_only=True)
class CreditAppliedDTO:
    id: str
    amount: str

@dataclass(kw_only=True)
class GiftCertificateDTO:
    code: str
    applied: str

@dataclass(kw_only=True)
class AdditionalFieldsDTO:
    hostIp: str

@dataclass(kw_only=True)
class PaymentAppliedMultipleDTO:
    processor: str
    amount: str
    cardType: str
    token: str
    cardNumber: str
    expiryMonth: str
    expiryYear: str
    additionalFields: list[AdditionalFieldsDTO] = None

@dataclass(kw_only=True)
class PaymentMultipleDataDTO:
    id: str
    invoices: list[InvoiceMultipleDTO]
    date: str
    paymentApplied: PaymentAppliedMultipleDTO
    creditApplied: list[CreditAppliedDTO]
    giftCertificates: list[GiftCertificateDTO]
    customAttributes: list[CustomAttributeDTO]

@dataclass(kw_only=True)
class PaymentMultipleRequestDTO(ABBaseDTO):
    payment: PaymentMultipleDataDTO = None