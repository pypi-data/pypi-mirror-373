from dataclasses import dataclass
from exsited.exsited.common.dto.common_dto import TaxDTO, CurrencyDTO
from exsited.exsited.payment.dto.payment_dto import PaymentDataDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class OrderItemAccountingCodeDTO(ABBaseDTO):
    salesRevenue: str = None


@dataclass(kw_only=True)
class OrderItemPricingRuleDTO(ABBaseDTO):
    price: str
    uuid: str = None
    price: str = None
    version: str = None
    priceType: str = None
    uom: str = None
    pricePeriod: str = None
    pricingSchedule: str = None
    pricingLevel: str = None
    pricingMethod: str = None
    warehouse: str = None


@dataclass(kw_only=True)
class OrderItemPropertiesDTO(ABBaseDTO):
    billingMode: str = None
    chargingPeriod: str = None
    chargingStartDate: str = None
    chargingAndBillingAlignment: bool = None
    proRataPartialChargingPeriod: bool = None
    proRataPartialPricingPeriod: bool = None


@dataclass(kw_only=True)
class OrderItemSaleTaxConfigurationDTO(ABBaseDTO):
    salePriceIsBasedOn: str = None
    taxCode: TaxDTO = None


@dataclass(kw_only=True)
class OrderItemPriceSnapshotDTO(ABBaseDTO):
    pricingRule: OrderItemPricingRuleDTO = None

    def add_rule(self, price: str):
        self.pricingRule = OrderItemPricingRuleDTO(price=price)
        return self


@dataclass(kw_only=True)
class PurchaseInvoiceDataPurchasePaymentAppliedDTO(ABBaseDTO):
    processor: str = None
    reference: str = None


@dataclass(kw_only=True)
class PurchaseInvoiceDataPurchasePaymentDTO(ABBaseDTO):
    date: str = None
    purchasePaymentApplied: list[PurchaseInvoiceDataPurchasePaymentAppliedDTO] = None


@dataclass(kw_only=True)
class PurchaseInvoiceDataDTO(ABBaseDTO):
    issueDate: str = None
    dueDate: str = None
    purchasePayment: PurchaseInvoiceDataPurchasePaymentDTO = None

@dataclass(kw_only=True)
class POInformationDTO(ABBaseDTO):
    id: str = None
    name: str = None
    accountId: str = None
    currency: str = None
    itemQuantity: str = None
    taxExemptWhenSold: str = None
    itemPriceSnapshot: OrderItemPriceSnapshotDTO = None
    purchaseInvoice: PurchaseInvoiceDataDTO = None
    taxExemptWhenPurchase: str = None


@dataclass(kw_only=True)
class OrderPurchaseDTO(ABBaseDTO):
    createPo: str = None
    poInformation: POInformationDTO = None

@dataclass(kw_only=True)
class PreOrderStockDetailsDTO(ABBaseDTO):
    pendingReserve: str = None
    reserved: str = None
    sold: str = None


@dataclass(kw_only=True)
class DiscountProfileDTO(ABBaseDTO):
    name: str = None
    uuid: str = None
    type: str = None
    amount: str = None
    redemptionCode: str = None


@dataclass(kw_only=True)
class SalesRevenueDetailsDTO(ABBaseDTO):
    salesRevenue: str = None

@dataclass(kw_only=True)
class itemCustomAttributesDataDTO(ABBaseDTO):
    name: str = None
    value: str = None

@dataclass(kw_only=True)
class AccountingCodeDTO(ABBaseDTO):
    salesRevenue: str = None

@dataclass(kw_only=True)
class OrderLineDTO(ABBaseDTO):
    itemId: str = None
    itemOrderQuantity: str = None
    itemUuid: str = None
    itemName: str = None
    shippingCost: str = None
    itemInvoiceNote: str = None
    itemDescription: str = None
    itemType: str = None
    itemChargeType: str = None
    chargeItemUuid: str = None
    version: str = None
    itemPriceTax: TaxDTO = None
    isTaxExemptWhenSold: str = None
    taxExemptWhenSold: str = None

    itemPriceSnapshot: OrderItemPriceSnapshotDTO = None
    itemSaleTaxConfiguration: OrderItemSaleTaxConfigurationDTO = None
    purchaseOrder: OrderPurchaseDTO = None
    packageName: str = None
    itemSerialOrBatchNumber: str = None
    itemCustomAttributes: list[itemCustomAttributesDataDTO] = None
    op: str = None
    uuid: str = None
    itemProperties: OrderItemPropertiesDTO = None

    subtotal: str = None
    total: str = None
    tax: TaxDTO = None

    itemUom: str = None
    itemWarehouse: str = None
    pricingSnapshotUuid: str = None
    chargingStartDate: str = None
    alternateChargingStartDate: str = None
    chargingEndDate: str = None
    alternateChargingEndDate: str = None
    uuid: str = None

    itemPrice: str = None
    itemDiscountAmount: str = None
    taxAmount: str = None
    operation: str = None


    discount: str = None
    uom: str = None
    warehouse: str = None
    quantity: str = None
    try:
        accountingCode: AccountingCodeDTO = None
        itemAccountingCode: OrderItemAccountingCodeDTO = None
    except:
        accountingCode: str = None
        itemAccountingCode: str = None

    preOrderStockDetails: PreOrderStockDetailsDTO = None
    expectedDeliveryDate: str = None

    purchaseOrderId: str = None
    purchaseInvoiceId: str = None
    itemId: str = None
    itemName: str = None
    itemOrderQuantity: str = None



@dataclass(kw_only=True)
class OrderPropertiesDTO(ABBaseDTO):
    communicationProfile: str = None
    invoiceMode: str = None
    invoiceTerm: str = None
    billingPeriod: str = None
    paymentProcessor: str = None
    paymentMode: str = None
    paymentTerm: str = None
    paymentTermAlignment: str = None
    fulfillmentMode: str = None
    fulfillmentTerm: str = None
    consolidateInvoice: str = None
    consolidateKey: str = None


@dataclass(kw_only=True)
class ContractPropertiesDTO(ABBaseDTO):
    requireCustomerAcceptance: str = None
    requiresPaymentMethod: str = None
    initialContractTerm: str = None
    renewAutomatically: str = None
    autoRenewalEndsOn: str = None
    autoRenewalRequireCustomerAcceptance: str = None
    autoRenewalTerm: str = None
    allowEarlyTermination: str = None
    earlyTerminationMinimumPeriod: str = None
    applyEarlyTerminationCharge: str = None
    earlyTerminationChargeType: str = None
    terminationPercentageCharge: str = None
    terminationAccountingCode: str = None
    allowPostponement: str = None
    maximumDurationPerPostponement: str = None
    maximumPostponementCount: str = None
    allowTrial: str = None
    startContractAfterTrialEnds: str = None
    trialPeriod: str = None
    trialEndDate: str = None
    trialRequiresPaymentMethod: str = None
    allowDowngrade: str = None
    periodBeforeDowngrade: str = None
    allowDowngradeCharge: str = None
    downgradeChargeType: str = None
    downgradeChargeFixed: str = None
    downgradeChargePercentage: str = None
    downgradeBillingPeriodCount: str = None
    allowUpgrade: str = None
    terminationFixedCharge: str = None
    terminationNoticePeriod: str = None





@dataclass(kw_only=True)
class OrderItemPriceTaxDTO(ABBaseDTO):
    uuid: str = None
    code: str = None
    rate: str = None

@dataclass(kw_only=True)
class UpgradeDowngradePreviewDTO(ABBaseDTO):
    subTotal: str = None
    taxTotal: str = None
    discountTotal: str = None
    shippingTotal: str = None
    total: str = None
    currency: str = None


@dataclass(kw_only=True)
class ContractAdjustmentPreviewDTO(ABBaseDTO):
    subTotal: str = None
    taxTotal: str = None
    discountTotal: str = None
    shippingTotal: str = None
    total: str = None
    currency: str = None
    oldTotal: str = None
    totalChanged: str = None
    totalDue: str = None


@dataclass(kw_only=True)
class KpisDTO(ABBaseDTO):
    startDate: str = None
    estimatedTotal: float = None
    totalRevenue: float = None
    monthlyRecurringRevenue: float = None
    totalCollected: float = None
    totalOutstanding: float = None
    totalDue: float = None
    lastInvoiceIssueDate: str = None
    lastInvoiceTotal: float = None
    totalInvoice: float = None
    nextInvoiceIssueDate: str = None
    lastReactivatedOn: str = None
    lastCancelledOn: str = None
    lastChangedOn: str = None
    lastDeletedOn: str = None


@dataclass(kw_only=True)
class InvoiceExpressDTO(ABBaseDTO):
    payment: PaymentDataDTO = None
    status: str = None
    id: str = None
    type: str = None
    customerPurchaseOrderId: str = None
    billingStartDate: str = None
    alternateBillingStartDate: str = None
    billingEndDate: str = None
    alternateBillingEndDate: str = None
    issueDate: str = None
    alternateIssueDate: str = None
    dueDate: str = None
    alternateDueDate: str = None
    subtotal: str = None
    shippingCost: str = None
    accountName: str = None
    tax: str = None
    taxTotal: str = None
    total: str = None
    paid: str = None
    due: str = None
    paymentStatus: str = None
    discountAmount: str = None
    priceTaxInclusive: str = None
    invoiceNote: str = None
    accountId: str = None
    orderId: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None

    customForms: dict = None
    currency: CurrencyDTO = None

    kpis: KpisDTO = None

    customAttributes: list = None
    customObjects: list = None
    customForm: dict = None
