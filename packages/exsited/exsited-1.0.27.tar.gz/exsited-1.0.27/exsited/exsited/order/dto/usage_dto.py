from dataclasses import dataclass
from exsited.exsited.common.dto.common_dto import CustomAttributesDTO, PaginationDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO
@dataclass(kw_only=True)
class UsageDataDTO(ABBaseDTO):
    uuid: str = None
    version: str = None
    chargeItemUuid: str = None
    chargeItemName: str = None
    chargingPeriod: str = None
    quantity: str = None
    uom: str = None
    startTime: str = None
    endTime: str = None
    type: str = None
    chargeStatus: str = None
    source: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    customAttributes: list[CustomAttributesDTO] = None
    usageReference: str = None


@dataclass(kw_only=True)
class UsageCreateDTO(ABBaseDTO):
    usage: UsageDataDTO = None


@dataclass(kw_only=True)
class MultipleUsageCreateDTO(ABBaseDTO):
    usages: list[UsageDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class MultipleUsageResponseDTO(ABBaseDTO):
    success: list[UsageDataDTO] = None
    failed: list[UsageDataDTO] = None


@dataclass(kw_only=True)
class UsageListDTO(ABBaseDTO):
    usages: list[UsageDataDTO] = None
    pagination: PaginationDTO = None

@dataclass(kw_only=True)
class UsageModifyDataDTO(ABBaseDTO):
    usage: UsageDataDTO = None

@dataclass(kw_only=True)
class UsageUpdateDataDTO(ABBaseDTO):
    usage: UsageDataDTO = None

