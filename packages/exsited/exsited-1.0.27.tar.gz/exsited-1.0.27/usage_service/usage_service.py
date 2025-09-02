from exsited.common.ab_exception import ABException
from exsited.exsited.exsited_sdk import ExsitedSDK
from tests.common.common_data import CommonData
from tests.order_test import test_order_details


class UsageService:
    CALL_ITEM_NAME = "Example Billable Calls"
    MESSAGE_ITEM_NAME = "Example Billable Messages"

    def process_usage_data(self, transformed_usage_data):
        results = []

        for data in transformed_usage_data:
            result = {}

            if "call_id" in data:
                result['itemName'] = self.CALL_ITEM_NAME
                result['callStart'] = data.get('call_start')
                result['callDuration_sec'] = data.get('call_duration_sec')
                result['callDestination'] = data.get('call_destination')
            else:
                result['itemName'] = self.MESSAGE_ITEM_NAME
                result['billingPeriod'] = data.get('billing_period')
                result['messagesSent'] = data.get('messages_sent')
                result['includedMessages'] = data.get('included_messages')

            response = self.get_order_details(data.get('order_id'))
            if response and response.order:
                for line in response.order.lines:
                    if line.itemName == result['itemName']:
                        result['itemType'] = line.itemType
                        result['chargeItemUuid'] = line.chargeItemUuid

            if result.get('chargeItemUuid'):
                results.append(result)

        return results

    def get_order_details(self, id: str):
        exsited_sdk: ExsitedSDK = ExsitedSDK().init_sdk(request_token_dto=CommonData.get_request_token_dto())

        try:
            response = exsited_sdk.order.details(id=id)
            return response
        except ABException as ab:
            error_code = None
            if ab.get_errors() and "errors" in ab.raw_response:
                error_code = ab.raw_response["errors"][0].get("code", None)
            print(f"Error occurred while fetching order details: {error_code}")
            return None
