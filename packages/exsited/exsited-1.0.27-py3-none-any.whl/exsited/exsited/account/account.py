import os

from exsited.exsited.account.account_api_url import AccountApiUrl
from exsited.exsited.account.dto.account_dto import AccountCreateDTO, AccountDetailsDTO, AccountListDTO, \
    AccountUpdateInformationDTO, AccountContactsDTO, PaymentMethodsAddDTO, PaymentMethodsDetailsDTO, \
    PaymentCardMethodsAddDTO, \
    PaymentMethodsListDTO, AccountCancelDTO, AccountCancelDataDTO, AccountReactivateDataDTO, AccountReactivateDTO, \
    AccountContactsTypeDTO, AccountContactUpdateDTO, AccountContactsUpdateDTO, AccountReactiveResponseDTO, \
    AccountAddressesAddDTO, AccountCancelResponseDTO, AccountAddressDetailsDTO, AccountAddressUuidDetailsDTO, \
    AccountNoteDetailsDTO, AccountNoteUuidDetailsDTO, AccountNoteUuidFileDetailsDTO, AccountNoteUuidFileUuidDetailsDTO, \
    AccountImageDetailsDTO, AccountNoteResponseDetailsDTO, AccountBillingPreferencesRequestDTO, \
    AccountBillingPreferencesResponseDTO, AccountAddressRequestDTO, AccountAddressResponseDTO, EmailSentResponseDTO, \
    EmailGetListResponseDTO, EmailGetDetailsResponseDTO
from exsited.exsited.account.dto.account_nested_dto import AccountContactsUpdate, ContactDTO
from exsited.exsited.common.common_enum import SortDirection
from exsited.common.sdk_util import SDKUtil
from exsited.http.ab_rest_processor import ABRestProcessor
import mimetypes

class Account(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def create(self, request_data: AccountCreateDTO) -> AccountDetailsDTO:
        response = self.post(url=AccountApiUrl.ACCOUNTS, request_obj=request_data, response_obj=AccountDetailsDTO())
        return response

    def add_image(self, file_url: str, account_id: str) -> AccountImageDetailsDTO:
        mime_type, _ = mimetypes.guess_type(file_url)
        if not mime_type:
            raise ValueError(f"Unable to determine MIME type for file: {file_url}")

        with open(file_url, "rb") as image_file:
            files = {
                "image": (file_url.split("\\")[-1], image_file, mime_type)
            }
            response = self.post(url=AccountApiUrl.ACCOUNTS_IMAGE.format(id=account_id), file=files, response_obj=AccountImageDetailsDTO())
        return response

    def add_notes_uuid(self, file_url: str, account_id: str, note_uuid:str) -> AccountNoteResponseDetailsDTO:
        if file_url:
            mime_type, _ = mimetypes.guess_type(file_url)
            if not mime_type:
                raise ValueError(f"Unable to determine MIME type for file: {file_url}")

            with open(file_url, "rb") as image_file:
                files = {
                    "file": (file_url.split("\\")[-1], image_file, mime_type)
                }

                response = self.post(
                    url=AccountApiUrl.ACCOUNTS_NOTE_UUID.format(id=account_id,uuid=note_uuid),
                    file=files,
                    response_obj=AccountNoteResponseDetailsDTO()
                )
            return response


    def add_notes(self, file_url: str = None, account_id: str = "", datas: str = "") -> AccountNoteResponseDetailsDTO:
        note = {
            "note": datas
        }

        if file_url:
            mime_type, _ = mimetypes.guess_type(file_url)
            if not mime_type:
                raise ValueError(f"Unable to determine MIME type for file: {file_url}")

            with open(file_url, "rb") as image_file:
                files = {
                    "file": (file_url.split("\\")[-1], image_file, mime_type)
                }

                response = self.post(
                    url=AccountApiUrl.ACCOUNTS_NOTE.format(id=account_id),
                    data=note,
                    file=files,
                    response_obj=AccountNoteResponseDetailsDTO()
                )
        else:
            response = self.post(
                url=AccountApiUrl.ACCOUNTS_NOTE.format(id=account_id),
                data=note,
                response_obj=AccountNoteResponseDetailsDTO()
            )

        return response

    def create_v3(self, request_data: AccountCreateDTO) -> AccountDetailsDTO:
        response = self.post(url=AccountApiUrl.ACCOUNTS_V3, request_obj=request_data, response_obj=AccountDetailsDTO())
        return response

    def list(self, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> AccountListDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=AccountApiUrl.ACCOUNTS, params=params, response_obj=AccountListDTO())
        return response

    def details(self, id: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNTS_V3 + f"/{id}", response_obj=AccountDetailsDTO())
        return response

    def get_image(self, id: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNTS_IMAGE.format(id=id), response_obj=AccountImageDetailsDTO())
        return response

    def address_details(self, id: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNTS_ADDRESS.format(id=id), response_obj=AccountAddressDetailsDTO())
        return response

    def note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None) -> AccountDetailsDTO:
        params = SDKUtil.init_pagination_params(limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=AccountApiUrl.ACCOUNTS_NOTE.format(id=id), params=params, response_obj=AccountNoteDetailsDTO())
        return response

    def address_uuid_details(self, id: str, uuid: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNTS_ADDRESS_UUID.format(id=id, uuid=uuid), response_obj=AccountAddressUuidDetailsDTO())
        return response

    def note_uuid_details(self, id: str, uuid: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNTS_NOTE_UUID.format(id=id, uuid=uuid), response_obj=AccountNoteUuidDetailsDTO())
        return response

    def note_uuid_files_details(self, id: str, uuid: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNTS_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=AccountNoteUuidFileDetailsDTO())
        return response

    def note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNTS_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=AccountNoteUuidFileUuidDetailsDTO())
        return response

    def details_information(self, id: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNT_INFORMATION.format(id=id), response_obj=AccountDetailsDTO())
        return response

    def cancel(self, id: str, request_data: AccountCancelDataDTO):
        cancel_request = AccountCancelDTO(account=request_data)
        response = self.post(url=AccountApiUrl.ACCOUNT_CANCEL.format(id=id), request_obj=cancel_request,
                             response_obj=AccountCancelResponseDTO())
        return response

    def reactivate(self, id: str, request_data: AccountReactivateDataDTO) -> AccountDetailsDTO:
        reactivate_request = AccountReactivateDTO(account=request_data)
        response = self.post(url=AccountApiUrl.ACCOUNT_REACTIVATE.format(id=id), request_obj=reactivate_request,
                             response_obj=AccountReactiveResponseDTO())
        return response

    def reactivate_v3(self, id: str, request_data: AccountReactivateDataDTO) -> AccountDetailsDTO:
        reactivate_request = AccountReactivateDTO(account=request_data)
        response = self.post(url=AccountApiUrl.ACCOUNT_REACTIVATE_V3.format(id=id), request_obj=reactivate_request,
                             response_obj=AccountReactiveResponseDTO())
        return response

    def delete(self, id: str):
        response = self.delete_request(url=AccountApiUrl.ACCOUNT_DELETE.format(id=id))
        return response

    def delete_image(self, id: str):
        response = self.delete_request(url=AccountApiUrl.ACCOUNTS_IMAGE.format(id=id))
        return response

    def delete_address_uuid(self, id: str, uuid: str):
        response = self.delete_request(url=AccountApiUrl.ACCOUNTS_ADDRESS_UUID.format(id=id, uuid=uuid))
        return response

    def delete_note_uuid(self, id: str, uuid: str):
        response = self.delete_request(url=AccountApiUrl.ACCOUNTS_NOTE_UUID.format(id=id, uuid=uuid))
        return response

    def delete_note_uuid_file_uuid(self, id: str, uuid: str, file_uuid: str):
        response = self.delete_request(url=AccountApiUrl.ACCOUNTS_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid))
        return response

    def contact_delete(self, id: str, contact_type: str):
        response = self.delete_request(
            url=AccountApiUrl.ACCOUNT_CONTACT_DELETE.format(id=id, contact_type=contact_type))
        return response

    def update_information(self, id: str, request_data: AccountUpdateInformationDTO) -> AccountDetailsDTO:
        response = self.patch(url=AccountApiUrl.ACCOUNT_UPDATE_INFORMATION.format(id=id), request_obj=request_data,
                              response_obj=AccountDetailsDTO())
        return response

    def update_address(self, id: str, uuid:str, request_data: AccountAddressRequestDTO) -> AccountAddressResponseDTO:
        response = self.patch(url=AccountApiUrl.ACCOUNTS_ADDRESS_UUID.format(id=id, uuid=uuid), request_obj=request_data,
                              response_obj=AccountAddressResponseDTO())
        return response

    def update_billing_preferences(self, id: str, request_data: AccountBillingPreferencesRequestDTO) -> AccountBillingPreferencesResponseDTO:
        response = self.put(url=AccountApiUrl.ACCOUNT_BILLING_PREFERENCE.format(id=id), request_obj=request_data,
                              response_obj=AccountBillingPreferencesResponseDTO())
        return response

    def get_contacts(self, id: str) -> AccountContactsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNT_CONTACTS.format(id=id), response_obj=AccountContactsDTO())
        return response

    def get_contact_type(self, id: str, contact_type: str) -> AccountContactsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNT_CONTACT_TYPE.format(id=id, contact_type=contact_type),
                            response_obj=AccountContactsDTO())
        return response

    def update_contact(self, id: str, contact_type: str,
                       request_data: AccountContactUpdateDTO) -> AccountContactsUpdateDTO:
        response = self.put(url=AccountApiUrl.ACCOUNT_CONTACT_UPDATE.format(id=id, contact_type=contact_type),
                            request_obj=request_data, response_obj=AccountContactsUpdateDTO)
        return response

    def update_contact_v3(self, id: str, contact_type: str,
                       request_data: AccountContactUpdateDTO) -> AccountContactsUpdateDTO:
        response = self.put(url=AccountApiUrl.ACCOUNT_CONTACT_UPDATE_V3.format(id=id, contact_type=contact_type),
                            request_obj=request_data, response_obj=AccountContactsUpdateDTO)
        return response

    def add_payment_method(self, account_id: str, request_data: PaymentMethodsAddDTO) -> PaymentMethodsDetailsDTO:
        response = self.post(url=AccountApiUrl.ACCOUNT_PAYMENT_METHODS.format(id=account_id), request_obj=request_data,
                             response_obj=PaymentMethodsDetailsDTO())
        return response

    def add_payment_card_method(self, account_id: str,
                                request_data: PaymentCardMethodsAddDTO) -> PaymentMethodsDetailsDTO:
        response = self.post(url=AccountApiUrl.ACCOUNT_PAYMENT_METHODS.format(id=account_id), request_obj=request_data,
                             response_obj=PaymentMethodsDetailsDTO())
        return response

    def add_payment_card_method_v3(self, account_id: str,
                                request_data: PaymentCardMethodsAddDTO) -> PaymentMethodsDetailsDTO:
        response = self.post(url=AccountApiUrl.ACCOUNT_PAYMENT_METHODS_V3.format(id=account_id), request_obj=request_data,
                             response_obj=PaymentMethodsDetailsDTO())
        return response

    def list_payment_method(self, account_id: str) -> PaymentMethodsListDTO:
        response = self.get(url=AccountApiUrl.ACCOUNT_PAYMENT_METHODS.format(id=account_id),
                            response_obj=PaymentMethodsListDTO())
        return response

    def delete_payment_method(self, account_id: str, reference: str):
        response = self.delete_request(
            url=AccountApiUrl.EACH_PAYMENT_METHODS.format(id=account_id, reference=reference))
        return response

    def delete_payment_method_v3(self, account_id: str, reference: str):
        response = self.delete_request(
            url=AccountApiUrl.EACH_PAYMENT_METHODS_V3.format(id=account_id, reference=reference))
        return response

    def payment_method_details(self, account_id: str, reference: str) -> PaymentMethodsDetailsDTO:
        response = self.get(url=AccountApiUrl.EACH_PAYMENT_METHODS.format(id=account_id, reference=reference),
                            response_obj=PaymentMethodsDetailsDTO())
        return response

    def billing_preference_details(self, account_id: str) -> AccountDetailsDTO:
        response = self.get(url=AccountApiUrl.ACCOUNT_BILLING_PREFERENCE.format(id=account_id),
                            response_obj=AccountDetailsDTO())
        return response

    def add_addresses(self, id: str, request_data: AccountAddressesAddDTO) -> AccountDetailsDTO:
        response = self.post(url=AccountApiUrl.ACCOUNT_ADDRESSES.format(id=id),
                             request_obj=request_data, response_obj=AccountDetailsDTO())
        return response

    def update_payment_method(self, id: str, reference: str,
                              request_data: PaymentMethodsAddDTO) -> PaymentMethodsDetailsDTO:
        response = self.patch(url=AccountApiUrl.ACCOUNT_PAYMENT_METHODS_UPDATE.format(id=id, reference=reference),
                              request_obj=request_data, response_obj=PaymentMethodsDetailsDTO())
        return response

    def modify_contact(self, id: str, contact_type: str,
                       request_data: AccountContactUpdateDTO) -> AccountContactsUpdateDTO:
        response = self.patch(url=AccountApiUrl.ACCOUNT_CONTACT_MODIFY.format(id=id, contact_type=contact_type),
                              request_obj=request_data, response_obj=AccountContactsUpdateDTO())
        return response

    def account_sent_email(self, file_url: str = None, account_id: str = "", email_data: dict = None):
        if not account_id:
            raise ValueError("Account ID is required")

        if not email_data or not isinstance(email_data, dict):
            raise ValueError("Invalid or missing 'email_data' parameter. Expected a dictionary.")

        cc_emails = ",".join(email_data.get("cc", [])) if email_data.get("cc") else ""
        bcc_emails = ",".join(email_data.get("bcc", [])) if email_data.get("bcc") else ""

        data = {
            "to": email_data.get("to", ""),
            "cc": cc_emails,
            "bcc": bcc_emails,
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", "")
        }

        files = None
        if file_url:
            mime_type, _ = mimetypes.guess_type(file_url)
            if not mime_type:
                raise ValueError(f"Unable to determine MIME type for file: {file_url}")

            file_name = os.path.basename(file_url)
            file = open(file_url, "rb")

            files = {
                "attachment": (file_name, file, mime_type)
            }

            try:
                response = self.post(
                    url=AccountApiUrl.ACCOUNT_SENT_EMAIL.format(id=account_id),
                    data=data,
                    file=files,
                    response_obj=EmailSentResponseDTO()
                )
                return response
            finally:
                if file_url:
                    file.close()

        else:
            response = self.post(
                url=AccountApiUrl.ACCOUNT_SENT_EMAIL.format(id=account_id),
                data=data,
                response_obj=EmailSentResponseDTO()
            )

        return response

    def account_get_email(self, id: str) -> EmailGetListResponseDTO:
        response = self.get(url=AccountApiUrl.ACCOUNT_SENT_EMAIL.format(id=id), response_obj=EmailGetListResponseDTO())
        return response

    def account_get_email_uuid(self, id: str, uuid: str) -> EmailGetDetailsResponseDTO:
        response = self.get(url=AccountApiUrl.ACCOUNT_SENT_EMAIL_UUID.format(id=id,uuid=uuid), response_obj=EmailGetDetailsResponseDTO())
        return response
