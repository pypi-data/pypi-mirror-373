from dataclasses import dataclass

from exsited.exsited.common.dto.common_dto import CustomAttributesDTO, CustomObjectDTO, PaginationDTO, CustomFormsDTO, \
    TaxDTO
from exsited.exsited.purchase_order.dto.purchase_order_dto import PurchaseOrderItemPriceSnapshotDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO

@dataclass(kw_only=True)
class CurrencyLinkDTO(ABBaseDTO):
    rel: str = None
    href: str = None


@dataclass(kw_only=True)
class PurchaseInvoiceCurrencyDTO(ABBaseDTO):
    id: str = None
    name: str = None
    link: CurrencyLinkDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceLineDataDTO(ABBaseDTO):
    subtotal: str = None
    total: str = None
    tax: str = None
    accountingCode: str = None
    itemUuid: str = None
    itemPurchaseOrderQuantity: str = None
    itemUom: str = None
    itemWarehouse: str = None
    uuid: str = None
    version: str = None
    itemId: str = None
    itemName: str = None
    itemQuantity: str = None
    itemPriceSnapshot: PurchaseOrderItemPriceSnapshotDTO = None
    itemPriceTax: TaxDTO = None
    priceTaxExampt: str = None


@dataclass(kw_only=True)
class PurchaseInvoiceKPIDTO(ABBaseDTO):
    outstanding: float = None
    overdue: float = None
    lastPaymentDate: str = None
    paymentApplied: float = None
    creditApplied: float = None
    creditIssued: str = None
    lastReactivatedOn: str = None
    lastCancelledOn: str = None
    lastAmendedOn: str = None
    voidedOn: str = None
    deletedOn: str = None

@dataclass(kw_only=True)
class ExternalBankDetailsDTO(ABBaseDTO):
    bankName: str = None
    bankCode: str = None
    accountName: str = None
    accountNumber: str = None
    swiftBicCode: str = None
    abaRouting: str = None
    bankAccountNumber: str = None


@dataclass(kw_only=True)
class PurchaseInvoiceDTO(ABBaseDTO):
    status: str = None
    id: str = None
    customForm: CustomFormsDTO = None
    currency: PurchaseInvoiceCurrencyDTO = None
    issueDate: str = None
    alternateIssueDate: str = None
    dueDate: str = None
    alternateDueDate: str = None
    subtotal: str = None
    tax: str = None
    total: str = None
    priceTaxInclusive: str = None
    accountId: str = None
    purchaseOrderId: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list[CustomAttributesDTO] = None
    customObjects: list[CustomObjectDTO] = None
    lines: list[PurchaseInvoiceLineDataDTO] = None
    kpis: PurchaseInvoiceKPIDTO = None
    externalBankDetails: ExternalBankDetailsDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceCreateDataDTO(ABBaseDTO):
    status: str = None
    id: str = None
    customForm: CustomFormsDTO = None
    currency: str = None
    issueDate: str = None
    alternateIssueDate: str = None
    dueDate: str = None
    alternateDueDate: str = None
    subtotal: str = None
    tax: str = None
    total: str = None
    priceTaxInclusive: str = None
    accountId: str = None
    purchaseOrderId: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list[CustomAttributesDTO] = None
    customObjects: list[CustomObjectDTO] = None
    lines: list[PurchaseInvoiceLineDataDTO] = None
    kpis: PurchaseInvoiceKPIDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceLineDTO(ABBaseDTO):
    status: str = None
    id: str = None
    customForm: CustomFormsDTO = None
    currency: PurchaseInvoiceCurrencyDTO = None
    issueDate: str = None
    alternateIssueDate: str = None
    dueDate: str = None
    alternateDueDate: str = None
    subtotal: str = None
    tax: str = None
    total: str = None
    priceTaxInclusive: str = None
    accountId: str = None
    purchaseOrderId: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list[CustomAttributesDTO] = None
    customObjects: list[CustomObjectDTO] = None
    line: list[PurchaseInvoiceLineDataDTO] = None
    kpis: PurchaseInvoiceKPIDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceListDTO(ABBaseDTO):
    purchaseInvoices: list[PurchaseInvoiceDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceRequestDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceCreateDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceDetailDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceDTO = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceLineDetailDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceLineDTO = None

@dataclass(kw_only=True)
class PurchaseInvoiceAccountDetailDTO(ABBaseDTO):
    account: PurchaseInvoiceListDTO = None

@dataclass(kw_only=True)
class PurchaseInvoiceCancelDataDTO(ABBaseDTO):
    effectiveDate: str = None

@dataclass(kw_only=True)
class PurchaseInvoiceCancelResponseDTO(ABBaseDTO):
    eventUuid: str = None

@dataclass(kw_only=True)
class PurchaseInvoiceCancelDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceCancelDataDTO = None

@dataclass(kw_only=True)
class PurchaseInvoiceReactiveDataDTO(ABBaseDTO):
    effectiveDate: str = None

@dataclass(kw_only=True)
class PurchaseInvoiceReactiveResponseDTO(ABBaseDTO):
    eventUuid: str = None

@dataclass(kw_only=True)
class PurchaseInvoiceReactiveDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceCancelDataDTO = None
