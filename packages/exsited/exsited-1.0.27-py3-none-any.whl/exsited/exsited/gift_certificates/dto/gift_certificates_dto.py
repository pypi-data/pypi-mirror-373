from dataclasses import dataclass
from typing import Union
from exsited.exsited.item.dto.item_dto import PaginationDTO
from exsited.exsited.order.dto.order_dto import CustomAttributesDataDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class AllocationDTO(ABBaseDTO):
    account: str = None
    type: str = None
    date: str = None


@dataclass(kw_only=True)
class TransactionDTO(ABBaseDTO):
    accountingCode: str = None
    type: str = None
    date: str = None
    amount: float = None
    currency: str = None
    reference: str = None


@dataclass(kw_only=True)
class CodeDTO(ABBaseDTO):
    length: str = None
    prefix: str = None


@dataclass(kw_only=True)
class CustomAttributeDataDTO(ABBaseDTO):
    name: str = None
    id: str = None


@dataclass(kw_only=True)
class CustomAttributeResponseDataDTO(ABBaseDTO):
    attribute: list[CustomAttributeDataDTO] = None
    value: str = None


@dataclass(kw_only=True)
class GiftCertificateDTO(ABBaseDTO):
    status: str = None
    account: str = None
    accountingCode: str = None

    amount: str = None
    remainingBalance: str = None
    usedAmount: str = None
    currency: str = None
    expiryDate: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None

    allocations: list[AllocationDTO] = None
    transactions: list[TransactionDTO] = None

    try:
        code: str = None
        customAttributes: list[CustomAttributeResponseDataDTO] = None
    except:
        code: CodeDTO = None
        customAttributes: list[CustomAttributesDataDTO] = None


@dataclass(kw_only=True)
class GiftCertificateResponseDTO(ABBaseDTO):
    status: str = None
    account: str = None
    accountingCode: str = None

    amount: str = None
    remainingBalance: str = None
    usedAmount: str = None
    currency: str = None
    expiryDate: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None

    allocations: list[AllocationDTO] = None
    transactions: list[TransactionDTO] = None


    code: CodeDTO = None
    customAttributes: list[CustomAttributesDataDTO] = None


@dataclass(kw_only=True)
class AllocationListDataDTO(ABBaseDTO):
    allocations: list[AllocationDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class TransactionListDataDTO(ABBaseDTO):
    transactions: list[TransactionDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class GiftCertificatesListDTO(ABBaseDTO):
    giftCertificates: list[GiftCertificateDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class GiftCertificatesListResponseDTO(ABBaseDTO):
    giftCertificates: list[GiftCertificateResponseDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class GiftCertificateAllocationListDTO(ABBaseDTO):
    giftCertificate: AllocationListDataDTO = None


@dataclass(kw_only=True)
class GiftCertificateTransactionsListDTO(ABBaseDTO):
    giftCertificate: TransactionListDataDTO = None


@dataclass(kw_only=True)
class GiftCertificateDetailsDTO(ABBaseDTO):
    giftCertificate: GiftCertificateDTO = None


@dataclass(kw_only=True)
class GiftCertificateDetailsResponseDTO(ABBaseDTO):
    giftCertificate: GiftCertificateResponseDTO = None