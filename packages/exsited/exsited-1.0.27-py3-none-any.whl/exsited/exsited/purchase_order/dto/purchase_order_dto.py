from dataclasses import dataclass
from exsited.exsited.common.dto.common_dto import TaxDTO, PaginationDTO, CustomAttributesDTO, CustomObjectDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO
from exsited.exsited.common.dto.common_dto import PaginationDTO

@dataclass(kw_only=True)
class PurchaseOrderCurrencyDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    link: str = None


@dataclass(kw_only=True)
class PurchaseOrderPricingRuleDTO(ABBaseDTO):
    uuid: str = None
    version: str = None
    priceType: str = None
    price: str = None
    uom: str = None
    warehouse: str = None
    pricingVersion: str = None
    latestUsedPricingVersion: str = None


@dataclass(kw_only=True)
class PurchaseOrderItemPriceSnapshotDTO(ABBaseDTO):
    pricingRule: PurchaseOrderPricingRuleDTO = None


@dataclass(kw_only=True)
class PurchaseOrderTaxCodeDTO(ABBaseDTO):
    uuid: str = None
    code: str = None
    rate: str = None
    link: str = None


@dataclass(kw_only=True)
class PurchaseOrderItemPurchaseTaxConfigurationDTO(ABBaseDTO):
    purchasePriceIsTaxInclusive: str = None
    taxCode: PurchaseOrderTaxCodeDTO = None


@dataclass(kw_only=True)
class KPIDTO(ABBaseDTO):
    totalExpense: float = None
    estimatedTotal: float = None
    totalOutstanding: float = None
    totalOverdue: float = None
    lastInvoiceIssueDate: str = None
    lastInvoiceTotal: float = None
    totalPurchaseInvoice: float = None
    lastReactivatedOn: str = None
    lastCalcelledOn: str = None
    lastChangedOn: str = None
    lastDeletedOn: str = None
    issueDate: str = None

@dataclass(kw_only=True)
class PurchaseOrderItemAccountingCodeDTO(ABBaseDTO):
    costOfGoodsSold: str = None


@dataclass(kw_only=True)
class PurchaseOrderLineDTO(ABBaseDTO):
    subtotal: str = None
    total: str = None
    tax: str = None
    itemUuid: str = None
    itemId: str = None
    itemName: str = None
    itemQuantity: str = None
    itemOrderQuantity: str = None
    itemPriceSnapshot: PurchaseOrderItemPriceSnapshotDTO = None
    itemPurchaseTaxConfiguration: PurchaseOrderItemPurchaseTaxConfigurationDTO = None
    itemPriceTaxExempt: str = None
    itemPriceTax: TaxDTO = None
    purchaseOrderNote: str = None
    itemAccountingCode: PurchaseOrderItemAccountingCodeDTO = None
    op: str = None
    uuid: str = None
    version: str = None
    itemSerialOrBatchNumber: str = None
    taxExemptWhenSold: str = None



@dataclass(kw_only=True)
class PurchaseOrderDTO(ABBaseDTO):
    status: str = None
    id: str = None
    currency: PurchaseOrderCurrencyDTO = None
    supplierInvoiceId: str = None
    saleOrderId: str = None
    issueDate: str = None
    dueDate: str = None
    expectedCompletionDate: str = None
    subtotal: str = None
    tax: str = None
    total: str = None
    priceTaxInclusive: str = None
    purchaseOrderNote: str = None
    accountId: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list[CustomAttributesDTO] = None
    customObjects: list[CustomObjectDTO] = None
    lines: list[PurchaseOrderLineDTO] = None
    kpis: KPIDTO = None


@dataclass(kw_only=True)
class PurchaseOrderDataDTO(ABBaseDTO):
    status: str = None
    id: str = None
    currency: str = None
    saleOrderId: str = None
    supplierInvoiceId: str = None
    issueDate: str = None
    dueDate: str = None
    expectedCompletionDate: str = None
    subtotal: str = None
    tax: str = None
    total: str = None
    priceTaxInclusive: str = None
    purchaseOrderNote: str = None
    accountId: str = None
    createdBy: str = None
    createdOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list = None
    customObjects: list = None
    lines: list[PurchaseOrderLineDTO] = None

    effectiveDate: str = None


@dataclass(kw_only=True)
class PurchaseOrderLineUuidDTO(ABBaseDTO):
    line: PurchaseOrderLineDTO = None



@dataclass(kw_only=True)
class PurchaseOrderDetailsDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderDTO = None


@dataclass(kw_only=True)
class PurchaseOrderLineUuidDetailsDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderLineUuidDTO = None


@dataclass(kw_only=True)
class PurchaseOrderCreateDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderChangeDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderDTO = None


@dataclass(kw_only=True)
class PurchaseOrderListDTO(ABBaseDTO):
    purchaseOrders: list[PurchaseOrderDTO] = None
    pagination: PaginationDTO = None
