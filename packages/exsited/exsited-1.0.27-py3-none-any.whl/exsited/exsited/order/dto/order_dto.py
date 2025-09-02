from dataclasses import dataclass

from exsited.exsited.account.dto.account_nested_dto import CommunicationPreferenceDTO, PaymentMethodsDataDTO
from exsited.exsited.common.dto.common_dto import CustomFormsDTO, CurrencyDTO, TimeZoneDTO, TaxDTO, PaginationDTO, \
    AddressDTO, ShippingProfileDTO
from exsited.exsited.order.dto.order_nested_dto import OrderLineDTO, OrderItemPriceSnapshotDTO, OrderPropertiesDTO, \
    ContractPropertiesDTO, UpgradeDowngradePreviewDTO, KpisDTO, DiscountProfileDTO, ContractAdjustmentPreviewDTO, \
    InvoiceExpressDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class KPIStatsDTO(ABBaseDTO):
    startDate: str = None
    estimatedTotal: float = None
    totalRevenue: float = None
    monthlyRecurringRevenue: float = None
    totalCollected: float = None
    totalOutstanding: float = None
    totalDue: float = None
    lastInvoiceIssueDate: str = None
    lastInvoiceTotal: float = None
    totalInvoice: int = None
    nextInvoiceIssueDate: str = None
    lastReactivatedOn: str = None
    lastCancelledOn: str = None
    lastChangedOn: str = None
    lastDeletedOn: str = None


@dataclass(kw_only=True)
class CustomAttributesDataDTO(ABBaseDTO):
    name: str = None
    value: str = None


@dataclass(kw_only=True)
class OrderDataDTO(ABBaseDTO):
    accountId: str = None
    bulkid: str = None
    requestid: str = None
    status: str = None
    id: str = None
    uuid: str = None
    version: str = None
    preOrder: str = None
    quoteOrder: str = None
    name: str = None
    displayName: str = None
    description: str = None
    manager: str = None
    referralAccount: str = None
    shippingCost: str = None
    origin: str = None
    invoiceNote: str = None
    billingStartDate: str = None
    orderStartDate: str = None
    nextBillingFromDate: str = None
    nextBillingFromDateUtc: str = None
    trialRequiresPaymentMethod: str = None
    priceTaxInclusive: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    allowContract: str = None

    lines: list[OrderLineDTO] = None
    customForms: CustomFormsDTO = None
    try:
        currency: CurrencyDTO = None
    except:
        currency: str = None
    timeZone: TimeZoneDTO = None
    properties: OrderPropertiesDTO = None

    contractProperties: ContractPropertiesDTO = None
    billingAddress: AddressDTO = None
    shippingAddress: AddressDTO = None
    shippingProfile: ShippingProfileDTO = None
    defaultWarehouse: str = None
    customObjects: list = None
    isTaxExemptWhenSold: str = None
    kpis: KpisDTO = None
    lineItems: list = None
    effectiveDate: str = None
    charge: OrderLineDTO = None
    communicationPreference: list[CommunicationPreferenceDTO] = None
    line: OrderLineDTO = None
    customAttributes: list[CustomAttributesDataDTO] = None
    customerPurchaseOrderId: str = None
    discountProfile: DiscountProfileDTO = None

    accountName: str = None
    currencyId: str = None
    total: str = None
    subtotal: str = None
    tax: str = None

    invoiceId: str = None
    paymentId: str = None
    invoice: InvoiceExpressDTO = None


    def add_line(self, item_id: str, quantity: str, price: str = None):
        line = OrderLineDTO(itemId=item_id, itemOrderQuantity=quantity)
        if price:
            line.itemPriceSnapshot = OrderItemPriceSnapshotDTO().add_rule(price=price)
        if not self.lines:
            self.lines = []
        self.lines.append(line)
        return self


@dataclass(kw_only=True)
class OrderCreateDTO(ABBaseDTO):
    order: OrderDataDTO


@dataclass(kw_only=True)
class OrderDowngradeDetailsDTO(ABBaseDTO):
    order: OrderDataDTO = None
    eventUuid: str = None


@dataclass(kw_only=True)
class OrderDetailsDTO(ABBaseDTO):
    order: OrderDataDTO = None
    eventUuid: str = None


@dataclass(kw_only=True)
class OrderListDTO(ABBaseDTO):
    orders: list[OrderDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class OrderCancelResponseDTO(ABBaseDTO):
    eventUuid: str = None
    order: OrderDataDTO = None


@dataclass(kw_only=True)
class AccountOrdersResponseDTO(ABBaseDTO):
    account: OrderListDTO = None


@dataclass(kw_only=True)
class OrderUpgradeDowngradeDTO(ABBaseDTO):
    preview: UpgradeDowngradePreviewDTO = None


@dataclass(kw_only=True)
class OrderUpgradeDTO(ABBaseDTO):
    effectiveDate: str = None
    effectiveImmediately: str = None
    redemptionCode: str = None
    discountPercentage: str = None
    lines: list[OrderLineDTO] = None


@dataclass(kw_only=True)
class OrderUpgradePreviewDTO(ABBaseDTO):
    effectiveDate: str = None
    effectiveImmediately: str = None
    redemptionCode: str = None
    discountPercentage: str = None
    lines: list[OrderLineDTO] = None
    properties: OrderPropertiesDTO = None


@dataclass(kw_only=True)
class OrderDowngradeDTO(ABBaseDTO):
    effectiveDate: str = None
    effectiveImmediately: str = None
    redemptionCode: str = None
    discountPercentage: str = None
    lines: list[OrderLineDTO] = None
    properties: OrderPropertiesDTO = None


@dataclass(kw_only=True)
class OrderDowngradePreviewDTO(ABBaseDTO):
    effectiveDate: str = None
    effectiveImmediately: str = None
    redemptionCode: str = None
    discountPercentage: str = None
    lines: list[OrderLineDTO] = None
    properties: OrderPropertiesDTO = None


@dataclass(kw_only=True)
class ContractAdjustmentPreviewRequestDTO(ABBaseDTO):
    effectiveDate: str = None
    effectiveImmediately: str = None
    redemptionCode: str = None
    discountPercentage: str = None
    lines: list[OrderLineDTO] = None
    properties: OrderPropertiesDTO = None


@dataclass(kw_only=True)
class ContractAdjustmentPreviewResponseDTO(ABBaseDTO):
    preview: ContractAdjustmentPreviewDTO = None


@dataclass(kw_only=True)
class OrderPaymentMethodDataDTO(ABBaseDTO):
    paymentMethods: list[PaymentMethodsDataDTO] = None

@dataclass(kw_only=True)
class OrderPaymentMethodsResponseDTO(ABBaseDTO):
    order: OrderPaymentMethodDataDTO = None

