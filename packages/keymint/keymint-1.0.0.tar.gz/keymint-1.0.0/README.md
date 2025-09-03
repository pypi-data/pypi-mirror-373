# KeyMint Python SDK

Welcome to the official KeyMint SDK for Python! This library provides a simple and convenient way to interact with the KeyMint API, allowing you to manage license keys for your applications with ease.

## ✨ Features

- **Simple & Intuitive**: A clean and modern API that is easy to learn and use.
- **Type Hinting**: Full type hint support for better IDE integration and code safety.
- **Comprehensive**: Complete API coverage for all KeyMint endpoints.
- **Well-Documented**: Clear and concise documentation with plenty of examples.
- **Error Handling**: Standardized error handling to make debugging a breeze.
- **Pythonic Interface**: Clean, intuitive API that follows Python conventions.

## 🚀 Quick Start

Here's a complete example of how to use the SDK to create and activate a license key:

```python
import os
from keymint import KeyMintSDK

def main():
    access_token = os.environ.get('KEYMINT_ACCESS_TOKEN')
    product_id = os.environ.get('KEYMINT_PRODUCT_ID')
    
    if not access_token or not product_id:
        print('Please set KEYMINT_ACCESS_TOKEN and KEYMINT_PRODUCT_ID environment variables.')
        return

    sdk = KeyMintSDK(access_token)

    try:
        # 1. Create a new license key
        create_response = sdk.create_key({
            'productId': product_id,
            'maxActivations': '5',  # Optional: Maximum number of activations
        })
        license_key = create_response['key']
        print(f'Key created: {license_key}')

        # 2. Activate the license key
        activate_response = sdk.activate_key({
            'productId': product_id,
            'licenseKey': license_key,
            'hostId': 'UNIQUE_DEVICE_ID',
        })
        print(f"Key activated: {activate_response['message']}")
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
```

## 📦 Installation

```bash
pip install keymint
```

## 🛠️ Usage

### Initialization

First, import the `KeyMintSDK` and initialize it with your access token. You can find your access token in your [KeyMint dashboard](https://app.keymint.dev/dashboard/developer/access-tokens).

```python
from keymint import KeyMintSDK

access_token = os.environ.get('KEYMINT_ACCESS_TOKEN')
if not access_token:
    raise ValueError('Please set the KEYMINT_ACCESS_TOKEN environment variable.')

sdk = KeyMintSDK(access_token)
```

### API Methods

All methods return a dictionary.

#### License Key Management

| Method          | Description                                     |
| --------------- | ----------------------------------------------- |
| `create_key`    | Creates a new license key.                      |
| `activate_key`  | Activates a license key for a device.          |
| `deactivate_key`| Deactivates a device from a license key.       |
| `get_key`       | Retrieves detailed information about a key.    |
| `block_key`     | Blocks a license key.                           |
| `unblock_key`   | Unblocks a previously blocked license key.     |

#### Customer Management

| Method                     | Description                                     |
| -------------------------- | ----------------------------------------------- |
| `create_customer`          | Creates a new customer.                         |
| `get_all_customers`        | Retrieves all customers.                        |
| `get_customer_by_id`       | Gets a specific customer by ID.                |
| `get_customer_with_keys`   | Gets a customer along with their license keys. |
| `update_customer`          | Updates customer information.                   |
| `toggle_customer_status`   | Toggles customer active status.                |
| `delete_customer`          | Permanently deletes a customer and their keys. |

For more detailed information about the API methods and their parameters, please refer to the [API Reference](#api-reference) section below.

## 📋 Examples

### Customer Management

```python
# Create a new customer
customer_response = sdk.create_customer({
    'name': 'John Doe',
    'email': 'john@example.com'
})

# Get all customers
customers = sdk.get_all_customers()

# Get a specific customer by ID
customer = sdk.get_customer_by_id({
    'customerId': 'customer_123'
})

# Get customer with their license keys
customer_with_keys = sdk.get_customer_with_keys({
    'customerId': customer_response['data']['id']
})

# Get customer with their license keys
customer_keys = sdk.get_customer_with_keys({
    'customerId': customer_response['data']['id']
})

# Update customer
updated_customer = sdk.update_customer({
    'customerId': customer_response['data']['id'],
    'name': 'John Smith',
    'email': 'john.smith@example.com'
})

# Toggle customer status (enable/disable)
toggle_response = sdk.toggle_customer_status({
    'customerId': customer_response['data']['id']
})

# Delete customer permanently (irreversible!)
delete_response = sdk.delete_customer({
    'customerId': customer_response['data']['id']
})
```

### Creating a License Key with a New Customer

```python
license_response = sdk.create_key({
    'productId': os.environ.get('KEYMINT_PRODUCT_ID'),
    'maxActivations': '3',  # Optional
    'newCustomer': {
        'name': 'Jane Doe',
        'email': 'jane@example.com'
    }
})
```

## 🔒 Security Best Practices

Never hardcode your access tokens! Always use environment variables:

1. **Create a `.env` file**:
```bash
KEYMINT_ACCESS_TOKEN=your_actual_token_here
KEYMINT_PRODUCT_ID=your_product_id_here
```

2. **Use environment variables in your code**:
```python
import os
from keymint import KeyMintSDK

access_token = os.environ.get('KEYMINT_ACCESS_TOKEN')
sdk = KeyMintSDK(access_token)
```

⚠️ **Important**: Never commit access tokens to version control.

## 🚨 Error Handling

If an API call fails, the SDK will raise a `KeyMintApiError` exception. This object contains a `message`, `code`, and `status` attribute that you can use to handle the error.

```python
from keymint import KeyMintApiError

try:
    # ...
except KeyMintApiError as e:
    print(f'API Error: {e.message}')
    print(f'Status: {e.status}')
    print(f'Code: {e.code}')
except Exception as e:
    print(f'An unexpected error occurred: {e}')
```

## 📚 API Reference

### `KeyMintSDK(access_token, base_url)`

| Parameter      | Type     | Description                                                                 |
| -------------- | -------- | --------------------------------------------------------------------------- |
| `access_token` | `str`    | **Required.** Your KeyMint API access token.                                |
| `base_url`     | `str`    | *Optional.* The base URL for the KeyMint API. Defaults to `https://api.keymint.dev`. |

### `create_key(params)`

| Parameter        | Type     | Description                                                                 |
| ---------------- | -------- | --------------------------------------------------------------------------- |
| `productId`      | `str`    | **Required.** The ID of the product.                                        |
| `maxActivations` | `str`    | *Optional.* The maximum number of activations for the key.                  |
| `expiryDate`     | `str`    | *Optional.* The expiration date of the key in ISO 8601 format.              |
| `customerId`     | `str`    | *Optional.* The ID of an existing customer to associate with the key.       |
| `newCustomer`    | `dict`   | *Optional.* A dictionary containing the name and email of a new customer.   |

### `activate_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to activate.                                  |
| `hostId`     | `str`    | *Optional.* A unique identifier for the device.                             |
| `deviceTag`  | `str`    | *Optional.* A user-friendly name for the device.                            |

### `deactivate_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to deactivate.                                |
| `hostId`     | `str`    | *Optional.* The ID of the device to deactivate. If omitted, all devices are deactivated. |

### `get_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to retrieve.                                  |

### `block_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to block.                                     |

### `unblock_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to unblock.                                   |

## 📚 API Reference

### `KeyMintSDK(access_token, base_url)`

| Parameter      | Type     | Description                                                                 |
| -------------- | -------- | --------------------------------------------------------------------------- |
| `access_token` | `str`    | **Required.** Your KeyMint API access token.                                |
| `base_url`     | `str`    | *Optional.* The base URL for the KeyMint API. Defaults to `https://api.keymint.dev`. |

### License Key Management Methods

#### `create_key(params)`

| Parameter        | Type     | Description                                                                 |
| ---------------- | -------- | --------------------------------------------------------------------------- |
| `productId`      | `str`    | **Required.** The ID of the product.                                        |
| `maxActivations` | `str`    | *Optional.* The maximum number of activations for the key.                  |
| `expiryDate`     | `str`    | *Optional.* The expiration date of the key in ISO 8601 format.              |
| `customerId`     | `str`    | *Optional.* The ID of an existing customer to associate with the key.       |
| `newCustomer`    | `dict`   | *Optional.* A dictionary containing the name and email of a new customer.   |

#### `activate_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to activate.                                  |
| `hostId`     | `str`    | *Optional.* A unique identifier for the device.                             |
| `deviceTag`  | `str`    | *Optional.* A user-friendly name for the device.                            |

#### `deactivate_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to deactivate.                                |
| `hostId`     | `str`    | *Optional.* The ID of the device to deactivate. If omitted, all devices are deactivated. |

#### `get_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to retrieve.                                  |

#### `block_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to block.                                     |

#### `unblock_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to unblock.                                   |

### Customer Management Methods

#### `create_customer(params)`

| Parameter | Type     | Description                                |
| --------- | -------- | ------------------------------------------ |
| `name`    | `str`    | **Required.** The customer's name.        |
| `email`   | `str`    | **Required.** The customer's email.       |

#### `get_all_customers()`

No parameters required. Returns all customers in your account.

#### `get_customer_by_id(params)`

| Parameter    | Type     | Description                                |
| ------------ | -------- | ------------------------------------------ |
| `customerId` | `str`    | **Required.** The customer's unique ID.   |

#### `get_customer_with_keys(params)`

| Parameter    | Type     | Description                                |
| ------------ | -------- | ------------------------------------------ |
| `customerId` | `str`    | **Required.** The customer's unique ID.   |

#### `update_customer(params)`

| Parameter    | Type     | Description                                |
| ------------ | -------- | ------------------------------------------ |
| `name`       | `str`    | **Required.** The customer's new name.    |
| `email`      | `str`    | **Required.** The customer's new email.   |
| `customerId` | `str`    | **Required.** The customer's unique ID.   |

#### `toggle_customer_status(params)`

| Parameter    | Type     | Description                                |
| ------------ | -------- | ------------------------------------------ |
| `customerId` | `str`    | **Required.** The customer's unique ID.   |

#### `delete_customer(params)`

| Parameter    | Type     | Description                                |
| ------------ | -------- | ------------------------------------------ |
| `customerId` | `str`    | **Required.** The customer's unique ID.   |

⚠️ **Warning**: `delete_customer` permanently deletes the customer and all associated license keys. This action cannot be undone.

## 📜 License

This SDK is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🔄 Breaking Changes in v1.0.0

This SDK has been updated to match the latest KeyMint API changes:

### **New Features**
- ✅ Added comprehensive customer management methods (`create_customer`, `get_all_customers`, `get_customer_by_id`, `get_customer_with_keys`, `update_customer`, `delete_customer`)
- ✅ Updated API endpoints to match new API structure  
- ✅ Enhanced type safety with updated TypedDict definitions
- ✅ `maxActivations` is now optional when creating license keys

### **API Endpoint Changes**
- `/create-key` → `/key`
- `/activate-key` → `/key/activate` 
- `/deactivate-key` → `/key/deactivate`
- `/get-key` → `/key` (now uses GET method)
- `/block-key` → `/key/block`
- `/unblock-key` → `/key/unblock`

### **Breaking Changes**
- Response field names have been updated to camelCase (e.g., `licensee_name` → `licenseeName`)
- The `get_key` method now uses GET request with query parameters instead of POST
- Customer management methods have been completely rewritten with new endpoints
- `get_customer_license_keys()` method has been removed - use `get_customer_with_keys()` instead

### **Migration Guide**
If upgrading from v0.x:
1. Update response field access: `response['licensee_name']` → `response['licenseeName']`
2. Customer management methods now use new parameter structures
3. Replace `get_customer_license_keys()` calls with `get_customer_with_keys()`
4. All API endpoints have been updated - no code changes needed as method signatures remain the same
