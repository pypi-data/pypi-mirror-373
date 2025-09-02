from dataclasses import dataclass, field, asdict
from exsited.exsited.common.dto.common_dto import CurrencyDTO, TimeZoneDTO, PaginationDTO, CustomAttributesDTO, TaxDTO, \
    AddressDTO, CustomFormsDTO, CustomObjectDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO
from exsited.exsited.account.dto.account_nested_dto import AccountingCodeDTO, CommunicationPreferenceDTO, \
    PaymentMethodsDataDTO, BillingPreferencesDTO, PaymentMethodsDTO, PaymentCardMethodsDTO, PaymentCardMethodsDataDTO, \
    PaymentMethodListDTO, AccountContacts, AccountContactsType, AccountContactsUpdate, AccountContactUpdate, \
    AcccountAddressDTO, NoteDataDTO, NoteFileDataDTO, NoteFileUuidDataDTO, AccountImageDataDTO, \
    AccountBillingPreferencesDetailsDTO, \
    AccountBillingPreferencesResponseDetailsDTO, AccountAddressRequestDetailsDTO, AccountAddressResponseDetailsDTO, \
    PaymentMethodListDTO, AccountContacts, AccountContactsType, AccountContactsUpdate, AccountContactUpdate, ContactDTO, \
    PricingLevelDTO, AcccountAddressRequestDTO, ContactRequestDTO


@dataclass(kw_only=True)
class AccountDataDTO(ABBaseDTO):
    name: str = None
    emailAddress: str = None
    status: str = None
    id: str = None
    displayName: str = None
    description: str = None
    invoiceParentAccount: str = None
    type: str = None
    imageUri: str = None
    grantPortalAccess: str = None
    website: str = None
    linkedin: str = None
    twitter: str = None
    facebook: str = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    parentAccount: str = None
    group: str = None
    manager: str = None
    referralTracking: str = None
    salesRep: str = None
    pricingLevel: PricingLevelDTO = None

    currency: CurrencyDTO = None
    timeZone: TimeZoneDTO = None
    tax: TaxDTO = None
    accountingCode: AccountingCodeDTO = None
    communicationPreference: list[CommunicationPreferenceDTO] = None
    paymentMethods: list[PaymentMethodsDataDTO] = None
    billingPreferences: BillingPreferencesDTO = None
    customAttributes: list[CustomAttributesDTO] = None
    try:
        addresses: list[AcccountAddressDTO] = None
        contacts: list[ContactDTO] = None
    except:
        addresses: list[AcccountAddressRequestDTO] = None
        contacts: list[ContactRequestDTO] = None
    customForms: CustomFormsDTO = None
    eventUuid: str = None
    customObjects: list[CustomObjectDTO] = None
    kpis: dict = None



@dataclass(kw_only=True)
class AccountAddressDataDTO(ABBaseDTO):
    id: str = None
    addresses: list[AcccountAddressDTO] = None


@dataclass(kw_only=True)
class AccountNoteDataDTO(ABBaseDTO):
    notes: list[NoteDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class AccountNoteResponseDataDTO(ABBaseDTO):
    notes: NoteDataDTO = None



@dataclass(kw_only=True)
class AccountAddressUuidDataDTO(ABBaseDTO):
    id: str = None
    addresses: AcccountAddressDTO = None


@dataclass(kw_only=True)
class AccountNoteUuidDataDTO(ABBaseDTO):
    note: NoteDataDTO = None


@dataclass(kw_only=True)
class AccountNoteUuidFileDataDTO(ABBaseDTO):
    note: NoteFileDataDTO = None


@dataclass(kw_only=True)
class AccountNoteUuidFileUuidDataDTO(ABBaseDTO):
    note: NoteFileUuidDataDTO = None


@dataclass(kw_only=True)
class AccountCreateDTO(ABBaseDTO):
    account: AccountDataDTO


@dataclass(kw_only=True)
class AccountUpdateInformationDTO(ABBaseDTO):
    account: AccountDataDTO


@dataclass(kw_only=True)
class AccountDetailsDTO(ABBaseDTO):
    account: AccountDataDTO = None


@dataclass(kw_only=True)
class AccountImageDetailsDTO(ABBaseDTO):
    account: AccountImageDataDTO = None


@dataclass(kw_only=True)
class AccountAddressDetailsDTO(ABBaseDTO):
    account: AccountAddressDataDTO = None


@dataclass(kw_only=True)
class AccountNoteDetailsDTO(ABBaseDTO):
    account: AccountNoteDataDTO = None


@dataclass(kw_only=True)
class AccountNoteResponseDetailsDTO(ABBaseDTO):
    account: AccountNoteResponseDataDTO = None


@dataclass(kw_only=True)
class AccountAddressUuidDetailsDTO(ABBaseDTO):
    account: AccountAddressUuidDataDTO = None


@dataclass(kw_only=True)
class AccountNoteUuidDetailsDTO(ABBaseDTO):
    account: AccountNoteUuidDataDTO = None


@dataclass(kw_only=True)
class AccountNoteUuidFileDetailsDTO(ABBaseDTO):
    account: AccountNoteUuidFileDataDTO = None


@dataclass(kw_only=True)
class AccountNoteUuidFileUuidDetailsDTO(ABBaseDTO):
    account: AccountNoteUuidFileUuidDataDTO = None


@dataclass(kw_only=True)
class AccountReactiveResponseDTO(ABBaseDTO):
    eventUuid: str = None

@dataclass(kw_only=True)
class AccountCancelResponseDTO(ABBaseDTO):
    eventUuid: str = None


@dataclass(kw_only=True)
class AccountListDTO(ABBaseDTO):
    accounts: list[AccountDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PaymentMethodsAddDTO(ABBaseDTO):
    account: PaymentMethodsDTO = None

    def method(self, payment_method: PaymentMethodsDataDTO):
        self.account = PaymentMethodsDTO(paymentMethod=payment_method)
        return self


@dataclass(kw_only=True)
class PaymentMethodsDetailsDTO(ABBaseDTO):
    account: PaymentMethodsDTO = None


@dataclass(kw_only=True)
class PaymentCardMethodsAddDTO(ABBaseDTO):
    account: PaymentCardMethodsDTO = None

    def method(self, payment_method: PaymentCardMethodsDataDTO):
        self.account = PaymentCardMethodsDTO(paymentMethod=payment_method)
        return self


@dataclass(kw_only=True)
class PaymentMethodsListDTO(ABBaseDTO):
    account: PaymentMethodListDTO = None


@dataclass(kw_only=True)
class AccountCancelDataDTO(ABBaseDTO):
    effectiveDate: str


@dataclass(kw_only=True)
class AccountCancelDTO(ABBaseDTO):
    account: AccountCancelDataDTO


@dataclass(kw_only=True)
class AccountReactivateDataDTO(ABBaseDTO):
    effectiveDate: str = None


@dataclass(kw_only=True)
class AccountReactivateDTO(ABBaseDTO):
    account: AccountReactivateDataDTO


@dataclass(kw_only=True)
class AccountContactsDTO(ABBaseDTO):
    account: AccountContacts = None


@dataclass(kw_only=True)
class AccountContactsTypeDTO(ABBaseDTO):
    account: AccountContactsType = None


@dataclass(kw_only=True)
class AccountContactUpdateDTO(ABBaseDTO):
    account: AccountContactUpdate = None


@dataclass(kw_only=True)
class AccountContactsUpdateDTO(ABBaseDTO):
    account: AccountContactsUpdate = None


@dataclass(kw_only=True)
class AccountAddressesAdd(ABBaseDTO):
    addresses: list[AddressDTO] = None


@dataclass(kw_only=True)
class AccountAddressesAddDTO(ABBaseDTO):
    account: AccountAddressesAdd = None


@dataclass(kw_only=True)
class AccountBillingPreferencesRequestDTO(ABBaseDTO):
    account: AccountBillingPreferencesDetailsDTO = None


@dataclass(kw_only=True)
class AccountBillingPreferencesResponseDTO(ABBaseDTO):
    account: AccountBillingPreferencesResponseDetailsDTO = None


@dataclass(kw_only=True)
class AccountAddressRequestDTO(ABBaseDTO):
    account: AccountAddressRequestDetailsDTO = None


@dataclass(kw_only=True)
class AccountAddressResponseDTO(ABBaseDTO):
    account: AccountAddressResponseDetailsDTO = None


@dataclass(kw_only=True)
class EmailSentAttachmentDTO(ABBaseDTO):
    name: str = None
    path: str = None
    size: int = None
    type: str = None


@dataclass(kw_only=True)
class EmailSentDetailsDTO(ABBaseDTO):
    uuid: str = None
    messageType: str = None
    status: str = None
    fromEmail: str = None
    to: str = None
    cc: list = None
    bcc: list = None
    subject: str = None
    body: str = None
    additionalTemplate: str = None
    createdAt: str = None
    lastUpdatedAt: str = None
    attachments: list = None

    _custom_field_mapping = {
        "from": "fromEmail"
    }


@dataclass(kw_only=True)
class AccountCommunicationDetailsDTO(ABBaseDTO):
    email: EmailSentDetailsDTO = None

    #Used only in Request as Parent
    # _custom_field_mapping = {
    #     "from": "fromEmail"
    # }


@dataclass(kw_only=True)
class EmailSentAccountDTO(ABBaseDTO):
    communication: AccountCommunicationDetailsDTO = None


@dataclass(kw_only=True)
class EmailSentResponseDTO(ABBaseDTO):
    account: EmailSentAccountDTO = None


@dataclass(kw_only=True)
class AccountCommunicationResponseListDTO(ABBaseDTO):
    emails: EmailSentDetailsDTO = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class EmailGetAccountListDTO(ABBaseDTO):
    communication: AccountCommunicationResponseListDTO = None


@dataclass(kw_only=True)
class EmailGetListResponseDTO(ABBaseDTO):
    account: EmailGetAccountListDTO = None


@dataclass(kw_only=True)
class AccountCommunicationResponseDetailsDTO(ABBaseDTO):
    email: EmailSentDetailsDTO = None


@dataclass(kw_only=True)
class EmailGetAccountDetailsDTO(ABBaseDTO):
    communication: AccountCommunicationResponseDetailsDTO = None


@dataclass(kw_only=True)
class EmailGetDetailsResponseDTO(ABBaseDTO):
    account: EmailGetAccountDetailsDTO = None
