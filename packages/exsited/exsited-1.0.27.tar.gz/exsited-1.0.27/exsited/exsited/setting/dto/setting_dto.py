from dataclasses import dataclass
from typing import Union
from exsited.exsited.common.dto.common_dto import PaginationDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class PaymentProcessorDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    default: str = None
    name: str = None
    displayName: str = None
    description: str = None
    provider: str = None
    currency: str = None


@dataclass(kw_only=True)
class BillingPreferencesDTO(ABBaseDTO):
    communicationProfile: str = None
    invoiceMode: str = None
    invoiceTerm: str = None
    billingPeriod: str = None
    billingStartDate: str = None
    billingStartDayOfMonth: str = None
    paymentProcessor: str = None
    paymentMode: str = None
    paymentTerm: str = None
    paymentTermAlignment: str = None


@dataclass(kw_only=True)
class ItemGroupDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    description: str = None
    imageUri: str = None
    manager: str = None
    billingPreferences: BillingPreferencesDTO = None


@dataclass(kw_only=True)
class PricingLevelsDataDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    description: str = None


@dataclass(kw_only=True)
class CurrencyDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    country: str = None
    symbol: str = None
    currencyCode: str = None
    precision: str = None
    rounding: str = None
    cashRoundingInterval: str = None


@dataclass(kw_only=True)
class TaxDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    country: str = None
    configuration: str = None
    code: str = None
    rate: str = None


@dataclass(kw_only=True)
class RedemptionCodeDTO(ABBaseDTO):
    codeId: str = None
    note: str = None
    maxLimit: str = None
    usageCount: str = None


@dataclass(kw_only=True)
class DiscountProfileDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    description: str = None
    invoiceNote: str = None
    accountingCode: str = None
    discountStartTime: str = None
    discountEndTime: str = None
    discountType: str = None
    fixed: str = None
    percentage: str = None
    maximumUse: str = None
    totalUsageCount: str = None
    maximumUsePerAccount: str = None
    maximumUsePerOrder: str = None
    requiresRedemptionCode: str = None
    redemptionCode: list[RedemptionCodeDTO] = None



@dataclass(kw_only=True)
class WarehouseDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    default: str = None
    name: str = None
    displayName: str = None
    description: str = None
    country: str = None
    state: str = None
    city: str = None
    postCode: str = None


@dataclass(kw_only=True)
class VariationOptionDTO(ABBaseDTO):
    name: str = None
    uuid: str = None


@dataclass(kw_only=True)
class VariationDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    description: str = None
    options: list[VariationOptionDTO] = None


@dataclass(kw_only=True)
class OptionDTO(ABBaseDTO):
    name: str = None
    order: int = None


@dataclass(kw_only=True)
class VariationCreateDataDTO(ABBaseDTO):
    name: str = None
    displayName: str = None
    description: str = None
    options: list[Union[str, OptionDTO]] = None


@dataclass(kw_only=True)
class UseInDTO(ABBaseDTO):
    resource: str = None

@dataclass(kw_only=True)
class ComponentDataDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    description: str = None
    useIn: list[UseInDTO] = None
    relation: str = None


@dataclass(kw_only=True)
class TaxConfigurationDTO(ABBaseDTO):
    uuid: str = None
    code: str = None
    rate: float = None
    link: str = None


@dataclass(kw_only=True)
class ShippingProfileDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    description: str = None
    invoiceNote: str = None
    type: str = None
    fixedAmount: str = None
    isTaxExempt: str = None
    isTaxInclusive: str = None
    taxConfiguration: TaxConfigurationDTO = None
    accountingCode: str = None


@dataclass(kw_only=True)
class ShippingProfilesResponseDTO(ABBaseDTO):
    shippingProfiles: list[ShippingProfileDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class ComponentResponseDTO(ABBaseDTO):
    components: list[ComponentDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class VariationCreateRequestDTO(ABBaseDTO):
    variations: VariationCreateDataDTO = None


@dataclass(kw_only=True)
class VariationsResponseDTO(ABBaseDTO):
    variations: list[VariationDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class VariationUpdateResponseDTO(ABBaseDTO):
    variation: VariationDTO = None



@dataclass(kw_only=True)
class WarehousesResponseDTO(ABBaseDTO):
    warehouses: list[WarehouseDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class DiscountProfilesResponseDTO(ABBaseDTO):
    discountProfiles: list[DiscountProfileDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class TaxesResponseDTO(ABBaseDTO):
    taxes: list[TaxDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class CurrenciesResponseDTO(ABBaseDTO):
    currencies: list[CurrencyDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class SettingPaymentProcessorListDTO(ABBaseDTO):
    paymentProcessors: list[PaymentProcessorDTO] = None


@dataclass(kw_only=True)
class SettingPricingLevelsListDTO(ABBaseDTO):
    pricingLevels: list[PricingLevelsDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class ItemGroupListDTO(ABBaseDTO):
    itemGroup: list[ItemGroupDTO] = None
