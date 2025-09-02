from dataclasses import dataclass
from exsited.sdlize.ab_base_dto import ABBaseDTO
from typing import Union


@dataclass(kw_only=True)
class TaxCodeDTO(ABBaseDTO):
    uuid: str = None
    code: str = None
    rate: float = None
    link: str = None


@dataclass(kw_only=True)
class AccountingCodeDTO(ABBaseDTO):
    salesRevenue: str = None


@dataclass(kw_only=True)
class PricingLevelDTO(ABBaseDTO):
    name: str = None
    uuid: str = None
    isLinked: str = None
    taxExempt: str = None
    salePriceEnteredIsInclusiveOfTax: str = None
    taxCode: str = None
    salePriceIsBasedOn: str = None


@dataclass(kw_only=True)
class PricingModuleDTO(ABBaseDTO):
    price: str = None
    currency: str = None
    uom: str = None
    lastPurchasePrice: str = None
    averagePurchasePrice: str = None


@dataclass(kw_only=True)
class UomDTO(ABBaseDTO):
    name: str = None
    baseUom: str = None
    saleConversionRate: str = None
    purchaseConversionRate: str = None
    usedForSale: str = None
    usedForPurchase: str = None
    isBase: str = None
    isUsedForSale: str = None
    isUsedForPurchase: str = None


@dataclass(kw_only=True)
class CustomAttributesDTO(ABBaseDTO):
    name: str
    value: Union[str, list] = None


@dataclass(kw_only=True)
class PricingDTO(ABBaseDTO):
    type: str = None
    version: str = None
    latestUsedPricingVersion: str = None
    pricingModule: list[PricingModuleDTO] = None


@dataclass(kw_only=True)
class CodesDTO(ABBaseDTO):
    name: str = None
    value: str = None


@dataclass(kw_only=True)
class DimensionDTO(ABBaseDTO):
    uom: str = None
    value: str = None


@dataclass(kw_only=True)
class CurrenciesDTO(ABBaseDTO):
    name: str = None
    usedForSale: str = None
    defaultForSale: str = None
    usedForPurchase: str = None
    defaultForPurchase: str = None
    isUsedForSale: str = None
    isDefaultForSale: str = None
    isUsedForPurchase: str = None
    isDefaultForPurchase: str = None


@dataclass(kw_only=True)
class SaleTaxConfigurationDTO(ABBaseDTO):
    salePriceEnteredIsInclusiveOfTax: str = None
    salePriceIsBasedOn: str = None
    taxCode: TaxCodeDTO = None


@dataclass(kw_only=True)
class SaleChargePropertiesDTO(ABBaseDTO):
    name: str = None
    value: str = None


@dataclass(kw_only=True)
class SaleChargeDTO(ABBaseDTO):
    type: str = None
    pricePeriod: str = None
    properties: list[SaleChargePropertiesDTO] = None


@dataclass(kw_only=True)
class TaxConfigurationDTO(ABBaseDTO):
    purchasePriceEnteredIsInclusiveOfTax: str = None
    taxCode: TaxCodeDTO = None


@dataclass(kw_only=True)
class PurchaseSuppliersDTO(ABBaseDTO):
    id: str = None
    name: str = None
    accountingCode: AccountingCodeDTO = None
    purchaseOrderNote: str = None
    defaultPurchaseCurrency: str = None
    defaultPurchasePrice: str = None
    isTaxExemptWhenPurchase: str = None
    taxConfiguration: TaxConfigurationDTO = None
    pricing: PricingDTO = None


@dataclass(kw_only=True)
class SaleDTO(ABBaseDTO):
    isEnable: str = None
    enabled: str = None
    invoiceNote: str = None
    accountingCode: AccountingCodeDTO = None
    defaultSalePrice: str = None
    shippingProfile: str = None
    taxExemptWhenSold: str = None
    pricingMethod: str = None
    taxConfiguration: SaleTaxConfigurationDTO = None
    pricingProfile: dict = None
    pricingSchedules: list[str] = None
    pricingLevels: list[PricingLevelDTO] = None
    charge: SaleChargeDTO = None
    paymentProperties: list[SaleChargePropertiesDTO] = None
    discountProfile: dict = None
    pricing: PricingDTO = None
    width: DimensionDTO = None
    height: DimensionDTO = None
    length: DimensionDTO = None
    weight: DimensionDTO = None
    useOnSalePrice: str= None
    salePriceVariant: str = None
    salePrice: str = None
    startDate: str = None
    endDate: str = None


@dataclass(kw_only=True)
class PurchaseTaxConfigurationDTO(ABBaseDTO):
    purchasePriceEnteredIsInclusiveOfTax: str = None


@dataclass(kw_only=True)
class PurchasePropertiesDTO(ABBaseDTO):
    name: str = None
    value: str = None


@dataclass(kw_only=True)
class PurchaseDTO(ABBaseDTO):
    isEnable: str = None
    enabled: str = None
    enableSupplierManagement: str = None
    accountingCode: AccountingCodeDTO = None
    purchaseOrderNote: str = None
    defaultPurchasePrice: str = None
    taxExemptWhenPurchase: str = None
    taxConfiguration: PurchaseTaxConfigurationDTO = None
    pricingProfile: dict = None
    purchaseProperties: list[PurchasePropertiesDTO] = None
    pricing: PricingDTO = None
    suppliers: list[PurchaseSuppliersDTO] = None


@dataclass(kw_only=True)
class InventoryWarehouseDTO(ABBaseDTO):
    name: str = None
    uuid: str = None
    link: str = None
    quantityOnHand: str = None
    quantityOnHandValue: str = None
    quantityPromised: str = None
    quantityOnOrder: str = None
    quantityOnReturn: str = None
    quantityOnPurchaseReturn: str = None
    quantityAvailable: str = None
    quantityAvailableValue: str = None
    uom: str = None

    quantity: str = None
    serialNumber: str = None
    batchNumber: str = None
    expiryDate: str = None
    accountingCode: str = None


@dataclass(kw_only=True)
class InventoryPropertiesDTO(ABBaseDTO):
    quantityAvailableForSaleDetermination: list = None
    quantityAvailableForSale: str = None
    enableLowStockNotification: str = None
    lowStockThresholdIsBasedOn: str = None
    enableReordering: str = None
    reorderingThresholdIsBasedOn: str = None

    lowStockThreshold: str = None
    stockRequiredForSale: str = None
    useLastPurchasePrice: str = None
    preferredSupplier: str = None
    reorderingThreshold: str = None
    enablePreordering: str = None
    enableSerialization: str = None
    enableBatchTracking: str = None
    useAtpAsQuantityAvailableForWebhook: str = None


@dataclass(kw_only=True)
class InventoriesDTO(ABBaseDTO):
    isEnabled: str = None
    preorderPeriod: list[str] = None
    warehouseIsEnabled: str = None
    warehouses: list[InventoryWarehouseDTO] = None
    inventoryProperties: InventoryPropertiesDTO = None

    quantity: str = None
    serialNumber: str = None
    batchNumber: str = None
    expiryDate: str = None
    accountingCode: str = None
    defaultWarehouse: str = None


@dataclass(kw_only=True)
class KpisDTO(ABBaseDTO):
    totalRevenue: float = None
    totalCollected: float = None
    totalOutstanding: float = None
    totalOverdue: float = None


@dataclass(kw_only=True)
class CustomFormDTO(ABBaseDTO):
    name: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ItemDataDTO(ABBaseDTO):
    status: str = None
    id: str = None
    name: str = None
    displayName: str = None
    description: str = None
    type: str = None
    baseUom: str = None
    parentItemId: str = None
    origin: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    imageUri: str = None
    group: dict = None
    manager: str = None
    customForm: CustomFormDTO = None
    customAttributes: list[CustomAttributesDTO] = None
    customObjects: list[str] = None
    codes: list[CodesDTO] = None
    uoms: list[UomDTO] = None
    currencies: list[CurrenciesDTO] = None
    sale: SaleDTO = None
    purchase: PurchaseDTO = None
    inventories: InventoriesDTO = None
    kpis: KpisDTO = None
    invoiceNote: str = None
    pricingLevels: str = None
    accountingCode: str = None
    defaultSalePrice: str = None
    isTaxExemptWhenSold: str = None
    pricing_method: str = None
    pricing_schedules: str = None
    charge: SaleChargeDTO = None
    paymentProperties: list[SaleChargePropertiesDTO] = None
    pricing: PricingDTO = None


@dataclass(kw_only=True)
class PaginationDTO(ABBaseDTO):
    records: int = None
    limit: int = None
    offset: int = None
    previousPage: str = None
    nextPage: str = None


@dataclass(kw_only=True)
class ItemListResponseDTO(ABBaseDTO):
    items: list[ItemDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class ItemResponseDTO(ABBaseDTO):
    item: ItemDataDTO = None


@dataclass(kw_only=True)
class ItemActionDTO(ABBaseDTO):
    items: ItemDataDTO = None

@dataclass(kw_only=True)
class SaleResponseDTO(ABBaseDTO):
    sale: SaleDTO = None


@dataclass(kw_only=True)
class ItemSaleResponseDTO(ABBaseDTO):
    item: SaleResponseDTO = None


@dataclass(kw_only=True)
class PurchaseResponseDTO(ABBaseDTO):
    purchase: PurchaseDTO = None


@dataclass(kw_only=True)
class ItemPurchaseResponseDTO(ABBaseDTO):
    item: PurchaseResponseDTO = None


@dataclass(kw_only=True)
class InventoryResponseDTO(ABBaseDTO):
    inventories: InventoriesDTO = None


@dataclass(kw_only=True)
class ItemInventoryResponseDTO(ABBaseDTO):
    item: InventoryResponseDTO = None
