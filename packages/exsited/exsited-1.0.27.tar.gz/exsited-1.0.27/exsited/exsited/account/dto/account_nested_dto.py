from dataclasses import dataclass
from exsited.sdlize.ab_base_dto import ABBaseDTO
from typing import Union

@dataclass(kw_only=True)
class PaymentProcessorDetailsDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    link: str = None


@dataclass(kw_only=True)
class SpecifiedOrdersDTO(ABBaseDTO):
    orderId: str = None


@dataclass(kw_only=True)
class PaymentMethodsDataDTO(ABBaseDTO):
    processorType: str = None
    paymentProcessor: str = None
    status: str = None
    default: str = None
    reference: str = None
    paymentCount: str = None
    lastUsedOn: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    specifiedOrders: list[Union[str, SpecifiedOrdersDTO]] = None
    useForSpecifiedOrders: str = None
    processor: PaymentProcessorDetailsDTO = None

    cardType: str = None
    token: str = None
    cardNumber: str = None
    expiryMonth: str = None
    expiryYear: str = None
    cardCvv: str = None
    nameOnCard: str = None
    lastUsedResult: str = None
    errorCountSinceLastSuccess: str = None


@dataclass(kw_only=True)
class PaymentMethodsDTO(ABBaseDTO):
    id: str = None
    paymentMethod: PaymentMethodsDataDTO = None


@dataclass(kw_only=True)
class PaymentMethodListDTO(ABBaseDTO):
    id: str = None
    paymentMethods: list[PaymentMethodsDataDTO] = None


@dataclass(kw_only=True)
class PaymentCardMethodsDataDTO(PaymentMethodsDataDTO):
    cardType: str = None
    token: str = None
    cardNumber: str = None
    expiryMonth: str = None
    expiryYear: str = None


@dataclass(kw_only=True)
class AdditionalFieldsDTO(ABBaseDTO):
    hostIp: str = None


@dataclass(kw_only=True)
class PaymentCardDirectDebitDataDTO(PaymentMethodsDataDTO):
    processorType: str = None
    default: str = None
    paymentProcessor: str = None
    accountNumber: str = None
    routingNumber: str = None
    accountName: str = None
    reference: str = None
    additionalFields: AdditionalFieldsDTO = None


@dataclass(kw_only=True)
class PaymentCardMethodsDTO(ABBaseDTO):
    paymentMethod: PaymentCardMethodsDataDTO


@dataclass(kw_only=True)
class BillingPreferencesDTO(ABBaseDTO):
    communicationProfile: str = None
    invoiceMode: str = None
    invoiceTerm: str = None
    billingPeriod: str = None
    billingStartDate: str = None
    billingStartDayOfMonth: str = None
    chargingAndBillingAlignment: str = None
    paymentProcessor: str = None
    paymentMode: str = None
    paymentTerm: str = None
    paymentTermAlignment: str = None


@dataclass(kw_only=True)
class CommunicationPreferenceDTO(ABBaseDTO):
    media: str = None
    isEnabled: bool = None


@dataclass(kw_only=True)
class AccountingCodeDTO(ABBaseDTO):
    accountReceivable: str = None


@dataclass(kw_only=True)
class SalutationDTO(ABBaseDTO):
    id: int = None
    name: str = None
    link: str = None


@dataclass(kw_only=True)
class DesignationDTO(ABBaseDTO):
    id: int = None
    name: str = None
    link: str = None


@dataclass(kw_only=True)
class EmailDTO(ABBaseDTO):
    address: str = None
    doNotEmail: str = None


@dataclass(kw_only=True)
class AccountImageDataDTO(ABBaseDTO):
    imageUri: str = None
    accountId: str = None


@dataclass(kw_only=True)
class PhoneDTO(ABBaseDTO):
    countryCode: str = None
    areaCode: str = None
    number: str = None
    full: str = None
    doNotEmail: str = None
    doNotCall: str = None


@dataclass(kw_only=True)
class CustomAttributeDTO(ABBaseDTO):
    name: str = None
    value: str = None


@dataclass(kw_only=True)
class ContactRequestDTO(ABBaseDTO):
    type: str = None
    typeDisplayName: str = None
    billingContact: bool = None
    shippingContact: bool = None
    salutation: SalutationDTO = None
    designation: DesignationDTO = None
    firstName: str = None
    middleName: str = None
    lastName: str = None
    email: EmailDTO = None
    addressLine_1: str = None
    addressLine_2: str = None
    addressLine_3: str = None
    addressLine_4: str = None
    addressLine_5: str = None
    postCode: str = None
    city: str = None
    state: str = None
    country: str = None
    phone: PhoneDTO = None
    try:
        fax:  PhoneDTO = None
        mobile:  PhoneDTO = None
    except:
        fax: str = None
        mobile: str = None
    receiveBillingInformation: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list[CustomAttributeDTO] = None


@dataclass(kw_only=True)
class PricingLevelDTO(ABBaseDTO):
    name: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ContactDTO(ABBaseDTO):
    type: str = None
    typeDisplayName: str = None
    billingContact: bool = None
    shippingContact: bool = None
    salutation: SalutationDTO = None
    designation: DesignationDTO = None
    firstName: str = None
    middleName: str = None
    lastName: str = None
    email: EmailDTO = None
    addressLine1: str = None
    addressLine2: str = None
    addressLine3: str = None
    addressLine4: str = None
    addressLine5: str = None
    postCode: str = None
    city: str = None
    state: str = None
    country: str = None
    phone: PhoneDTO = None
    try:
        fax:  PhoneDTO = None
        mobile:  PhoneDTO = None
    except:
        fax: str = None
        mobile: str = None
    receiveBillingInformation: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    customAttributes: list[CustomAttributeDTO] = None


@dataclass(kw_only=True)
class AccountContacts(ABBaseDTO):
    id: str = None  # Default value set to None
    contacts: list[ContactDTO] = None


@dataclass(kw_only=True)
class AccountContactsType(ABBaseDTO):
    id: str = None  # Default value set to None
    contacts: ContactDTO = None


@dataclass(kw_only=True)
class AccountContactUpdate(ABBaseDTO):
    contact: ContactDTO = None


@dataclass(kw_only=True)
class AccountContactsUpdate(ABBaseDTO):
    contacts: ContactDTO = None
    id: str = None

@dataclass(kw_only=True)
class AcccountAddressDTO(ABBaseDTO):
    addressLine1: str = None
    addressLine2: str = None
    addressLine3: str = None
    addressLine4: str = None
    addressLine5: str = None
    postCode: str = None
    uuid: str = None
    city: str = None
    state: str = None
    country: str = None
    isDefaultBilling: bool = None
    isDefaultShipping: bool = None


@dataclass(kw_only=True)
class AcccountAddressRequestDTO(ABBaseDTO):
    address_line_1: str = None
    address_line_2: str = None
    address_line_3: str = None
    address_line_4: str = None
    address_line_5: str = None
    postCode: str = None
    uuid: str = None
    city: str = None
    state: str = None
    country: str = None
    isDefaultBilling: bool = None
    isDefaultShipping: bool = None


@dataclass(kw_only=True)
class FileDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    version: str = None

@dataclass(kw_only=True)
class NoteDataDTO(ABBaseDTO):
    uuid: str = None
    version: str = None
    content: str = None
    files: list[FileDTO] = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None


@dataclass(kw_only=True)
class NoteFileDataDTO(ABBaseDTO):
    files: list[FileDTO] = None


@dataclass(kw_only=True)
class NoteFileUuidDataDTO(ABBaseDTO):
    file: FileDTO = None

##############
@dataclass(kw_only=True)
class AccountBillingPreferencesDetailsDTO(ABBaseDTO):
    billingPreferences: BillingPreferencesDTO = None

@dataclass(kw_only=True)
class AccountBillingPreferencesResponseDetailsDTO(ABBaseDTO):
    id: str = None
    billingPreferences: BillingPreferencesDTO = None


@dataclass(kw_only=True)
class AccountAddressRequestDetailsDTO(ABBaseDTO):
    address: AcccountAddressRequestDTO = None


@dataclass(kw_only=True)
class AccountAddressResponseDetailsDTO(ABBaseDTO):
    id: str = None
    addresses: AcccountAddressDTO = None
