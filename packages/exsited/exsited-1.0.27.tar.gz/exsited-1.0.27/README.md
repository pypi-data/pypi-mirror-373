# Exsited Python SDK
The Exsited Python SDK provides an easy-to-use library for integrating Exsited services into your project. This includes Custom Integration, Onsite Integration and all APIs.

***
## Table of Contents
- [Requirements](#Requirements)
- [Installation](#Installation)
- [Configuration](#Configuration)
- [Authentication](#Authentication)
- [Getting Started](#Getting-Started)
- [Testing](#Testing)
- [API Documentation](#API-Documentation)
- [Usage charge_item_uuid Association](#Usage-charge_item_uuid-Association)
# Requirements
Python 3.12 and Later

# Installation
```bash
#Navigate to the project directory
cd exsited-python

# Install virtualenv
pip install virtualenv

# Create Virtual Environment
python -m venv venv

# Active virtual Environment from windows
venv\Scripts\activate

# Upgrade the pip
python -m pip install --upgrade pip


# Install setup tools
pip install setuptools

# Install app Dependency
pip install -e .

# Usage association Dependencies
pip install peewee
pip install mysql-connector-python


```


# Configuration

To set up the Exsited SDK, you'll require your `Client ID`, `Client Secret`, and `Redirect URL`. If you have not received these details already, please reach out to your designated client contact to obtain them



# Authentication
1. **Locate `common_data.py`:** Open the SKD project directory on an IDE and navigate to the `common_data.py` file which is located in the following path: `tests/common/common_data.py`.
2. **Update `get_request_token_dto` function:** Within the `common_data.py` class, locate the method named `get_request_token_dto` and update it with the credentials you were provided.
<img src="blob:https://webalive.atlassian.net/c058a466-42ce-405e-b3ca-dfbbb81a9939#media-blob-url=true&id=ee9aff06-3e79-4823-b0bf-9ef83f5d3c9a&collection=contentId-558825510&contextId=558825510&mimeType=image%2Fpng&name=image.png&size=435487&width=2049&height=922&alt=image.png" alt="">

3. **Provide Credential Values:** Populate the mandatory fields (`clientId`, `clientSecret`, `redirectUri`, and `ExsitedUrl`) within the `RequestTokenDTO` object. However, **replace the placeholder values**  in the following code block with your actual credentials:

### Code Example:
```python
def get_request_token_dto():
    return RequestTokenDTO(
        grantType="client_credentials",
        clientId="[YOUR_CLIENT_ID]",  # Replace with your actual Client ID
        clientSecret="[YOUR_CLIENT_SECRET]",  # Replace with your actual Client Secret
        redirectUri="[YOUR_REDIRECT_URI]",  # Replace with your actual Redirect URL
        ExsitedUrl="[YOUR_EXSITED_SERVER_URL]" # Replace with your Exsited server URL, 
    )
 ```
### Credentials Table
| Key          | value                     | 
|--------------|---------------------------|
| clientId     | "[YOUR_CLIENT_ID]"        | 
| clientSecret | "[YOUR_CLIENT_SECRET]"    | 
| redirectUri  | "[YOUR_REDIRECT_URI]"       | 
| ExsitedUrl   | "[YOUR_EXSITED_SERVER_URL]" | 

# Getting Started
Follow the common pattern to test the functions on the SDK. All the tests can be done on the test files located in the Tests directory.

### Testing SDK Functions

### Example Method 1: `test_account_create_basic`
***

### Request Parameters

| Parameter       | Description                                             | Type             | Required |
|-----------------|---------------------------------------------------------|------------------|----------|
| account         | Contains the account details to be created.             | `AccountDataDTO` | Yes      |
| account.name    | The name of the account.                                | `str`            | Yes      |
| account.emailAddress | The email address associated with the account.     | `str`            | Yes      |

### Example Request Data (JSON Representation)

```json
{
  "account": {
    "name": "Example Name",
    "emailAddress": "example@example.com"
  }
}
```
### Function Signature
```Python
def test_account_create_basic():
    SDKConfig.PRINT_REQUEST_DATA = False
    SDKConfig.PRINT_RAW_RESPONSE = False

    token_file_path = "shared_token.json"
    file_token_mgr = FileTokenManager(token_file_path)

    exsited_sdk: ExsitedSDK = ExsitedSDK().init_sdk(
        request_token_dto=CommonData.get_request_token_dto(),
        file_token_mgr=file_token_mgr
    )

    try:
        # You will edit the following request_data
        request_data = AccountCreateDTO(account=AccountDataDTO(name="Example Name", emailAddress="example@example.com"))
        
        response = exsited_sdk.account.create(request_data=request_data)
        print(response)
    except ABException as ab:
        print(ab)
        print(ab.get_errors())
        print(ab.raw_response)
```

### Example Method 2: `test_order_create_basic`
***
| Parameter  | Description                                 | Type | Required |
|------------|---------------------------------------------|------|----------|
| accountId  | The ID of the account associated with the order. | str  | Yes      |
| item_id    | The ID of the item being ordered.           | str  | Yes      |
| quantity   | The quantity of the item being ordered.     | str  | Yes      |

```json
{
  "order": {
    "accountId": "30PS79",
    "lines": [
      {
        "item_id": "ITEM-0055",
        "quantity": "1"
      }
    ]
  }
}
```
### Function Signature
```Python
def test_order_create_basic():
    SDKConfig.PRINT_REQUEST_DATA = True
    SDKConfig.PRINT_RAW_RESPONSE = False

    token_file_path = "shared_token.json"
    file_token_mgr = FileTokenManager(token_file_path)

    exsited_sdk: ExsitedSDK = ExsitedSDK().init_sdk(
        request_token_dto=CommonData.get_request_token_dto(),
        file_token_mgr=file_token_mgr
    )

    try:
        # You will edit the following request_data
        request_data = OrderCreateDTO(order=OrderDataDTO(accountId="30PS79").add_line(item_id="ITEM-0055", quantity="1"))
        response = exsited_sdk.order.create(request_data=request_data)
        print(response)
        
    except ABException as ab:
        print(ab)
        print(ab.get_errors())
        print(ab.raw_response)

```
***
### Response
| Field    | Description                                                 |
|----------|-------------------------------------------------------------|
| response | The response from the the method being called.              |
| errors   | Any errors encountered during the account creation process. |

### Error Handling
| Field           | Description                                             |
|-----------------|---------------------------------------------------------|
| ab              | The exception object.                                   |
| ab.get_errors() | A list of errors that occurred during the account creation process. |
| ab.raw_response | The raw response data from the API call, useful for debugging. |

# Testing
### Executing Functions
To test the SDK functions, adhere to the common pattern outlined below. All tests should be conducted using the provided test files located in the "Tests" directory.

1. Set up the environment: Ensure that the SDK configuration is appropriately initialized for testing purposes.

2. Customize request data: Adjust the `request_data` as needed for the specific function being tested.

3. Execute the function: Call the desired function from the SDK, updating the `request_data` inside the function body.

### Required Fields
The following tables contain for the required fields for the test cases
### Account

| Function Name                     | Required Fields                |
|-----------------------------------|--------------------------------|
| test_account_create_basic        | name, emailAddress            |
| test_account_update_info         | id (Account ID)               |
| test_account_list_basic          | n/a                            |
| test_account_details             | id (Account ID)               |
| test_account_delete              | id (Account ID)               |
| test_account_payment_methods_add | processorType, default, paymentProcessor, reference |
| test_account_payment_card_methods_add | processorType, default, paymentProcessor, reference, cardType, token, cardNumber, expiryMonth, expiryYear |
| test_list_payment_methods        | account_id (Account ID)       |
| test_delete_payment_methods      | account_id (Account ID), reference |
| test_payment_method_details      | account_id (Account ID), reference |

### Order 
| Function                   | Required Parameters               |
|----------------------------|-----------------------------------|
| test_order_create_basic   | accountId, item_id, quantity (Item Quantity) |
| test_order_list_basic     | n/a                               |
| test_order_details        | id (Order ID)                     |
| test_order_cancel         | id (Order ID), effective_date     |
| test_order_usage_add      | chargeItemUuid, chargingPeriod, quantity, startTime, endTime, type |


### Invoice 
| Function              | Required Parameters |
|-----------------------|----------------------|
| test_invoice_list    | n/a                  |
| test_invoice_details | id                   |

# API Documentation
[API Documentation](https://callservice.atlassian.net/wiki/spaces/Implementa/pages/8159248/API+Documentations)

# Usage `charge_item_uuid` Association



The `order_usage_db` folder contains the functionality for handling database operations related to orders within the Exsited SDK. This module is responsible for connecting to the database, managing orders, processing order data, and saving the relevant information to the database.

### Components of `order_usage_db`

1. **`connect_with_db.py`**  
   - Manages the database connection setup, including functions for establishing and terminating connections

2. **`order_manager.py`**  
   - Manages Order data, to create rows for the database where the relevant associations are made in order to create usages easily using **`charge_item_uuid`**

3. **`order_model.py`**  
   - Contains the structure of the order association table

4. **`order_service.py`**  
   - Contains the function to create the association records

5. **`save_to_db.py`**  
   - Implements the logic to persist order association data to the database. It interacts with the `connect_with_db.py` module to perform save operations.

### Adding Data To the Association Table

After configuring your database connection in `connect_with_db.py`, you can use the other scripts to manage orders and persist data to your database. For example, you can create and process an order using `order_manager.py` and then save it using `save_to_db.py`.

#### Example Workflow

1. **Adding Database Details:**
   In the SaveToDB class within the order_usage_db module, ensure that you update the OrderManager 
   initialization with your specific database connection details, such as the database name, username, 
   password, and host address.
2. ```python
   class SaveToDB:
    def process_order_data(_order_id: str, _account_id: str, _item_id: str, _item_name: str, _charge_item_uuid: str):
        # Add your database details below
        order_manager = OrderManager('your_database_name', 'your_username', 'your_password', 'your_host_address')
        order_manager.connect_to_db()
        order_manager.process_order(
            account_id=_account_id,
            order_id=_order_id,
            item_id=_item_id,
            item_name=_item_name,
            charge_item_uuid=_charge_item_uuid
        )
        order_manager.disconnect_from_db()
   
3. Once the database details and other necessary configurations have been added, you can use the following example to add an order. 
This will automatically update the association tables, allowing you to retrieve the relevant details needed to update usage data.
   
   ```python
   def test_order_create_basic():
    SDKConfig.PRINT_REQUEST_DATA = True
    SDKConfig.PRINT_RAW_RESPONSE = False

    token_file_path = "shared_token.json"
    file_token_mgr = FileTokenManager(token_file_path)

    exsited_sdk: ExsitedSDK = ExsitedSDK().init_sdk(
        request_token_dto=CommonData.get_request_token_dto(),
        file_token_mgr=file_token_mgr
    )

    try:
        request_data = OrderCreateDTO(
            order=OrderDataDTO(accountId="AC01").add_line(item_id="ITEM-001", quantity="1"))
        response = exsited_sdk.order.create(request_data=request_data)
        
        if response.order:
            account_id = response.order.accountId
            order_id = response.order.id
            for line in response.order.lines:
                if line.itemChargeType == 'METERED':
                     #Note: The item must be of type "Metered" for the association data to be stored.
                    SaveToDB.process_order_data(_account_id=account_id, _order_id=order_id, _item_id=line.itemId,
                                     _item_name=line.itemName, _charge_item_uuid=line.chargeItemUuid)
    except ABException as ab:
        print(ab)
        print(ab.get_errors())
        print(ab.raw_response)