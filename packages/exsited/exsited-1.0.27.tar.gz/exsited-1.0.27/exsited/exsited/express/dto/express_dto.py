# express_dto.py

from dataclasses import dataclass
from typing import List

from exsited.exsited.order.dto.order_dto import OrderDataDTO
from exsited.exsited.order.dto.order_nested_dto import OrderPropertiesDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class PricingRuleDTO(ABBaseDTO):
    price: str = None


@dataclass(kw_only=True)
class ItemPriceSnapshotDTO(ABBaseDTO):
    pricingRule: PricingRuleDTO = None


@dataclass(kw_only=True)
class ItemPriceTaxDTO(ABBaseDTO):
    uuid: str = None
    code: str = None
    rate: float = None

@dataclass(kw_only=True)
class PaymentAppliedDTO(ABBaseDTO):
    processor: str = None
    amount: str = None

@dataclass(kw_only=True)
class PaymentDTO(ABBaseDTO):
    paymentApplied: List[PaymentAppliedDTO] = None

@dataclass(kw_only=True)
class InvoiceDTO(ABBaseDTO):
    payment: PaymentDTO = None

@dataclass(kw_only=True)
class ContractPropertiesDTO(ABBaseDTO):
    requireCustomerAcceptance: str = None
    requiresPaymentMethod: str = None
    initialContractTerm: str = None
    renewAutomatically: str = None
    autoRenewalTerm: str = None
    allowEarlyTermination: str = None
    applyEarlyTerminationCharge: str = None
    allowPostponement: str = None
    maximumDurationPerPostponement: str = None
    maximumPostponementCount: str = None
    allowTrial: str = None
    startContractAfterTrialEnds: str = None
    trialPeriod: str = None
    allowDowngrade: str = None
    periodBeforeDowngrade: str = None
    allowDowngradeCharge: str = None
    downgradeChargeType: str = None
    downgradeChargeFixed: str = None
    allowUpgrade: str = None

@dataclass(kw_only=True)
class OrderLineDTO(ABBaseDTO):
    itemId: str = None
    itemOrderQuantity: int = None
    itemPriceSnapshot: ItemPriceSnapshotDTO = None
    itemPriceTax: ItemPriceTaxDTO = None
    packageName: str = None

@dataclass(kw_only=True)
class OrderDTO(ABBaseDTO):
    lines: List[OrderLineDTO] = None
    invoice: InvoiceDTO = None
    allowContract: str = None
    contractProperties: ContractPropertiesDTO = None
    properties: OrderPropertiesDTO = None

@dataclass(kw_only=True)
class AccountDTO(ABBaseDTO):
    id: str = None
    try:
        order: OrderDTO = None
    except:
        order: OrderDataDTO = None

@dataclass(kw_only=True)
class ExpressDTO(ABBaseDTO):
    account: AccountDTO = None
    _custom_field_mapping = {
        "isTaxExemptWhenSold": "isTaxExemptWhenSold"
    }
