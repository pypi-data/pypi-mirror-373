import requests
from .types import *
from ._version import __version__

__all__ = ['KeyMintSDK', 'KeyMintApiError', '__version__']

class KeyMintSDK:
    def __init__(self, access_token: str, base_url: str = "https://api.keymint.dev"):
        if not access_token:
            raise ValueError("Access token is required to initialize the SDK.")
        
        self.access_token = access_token
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _handle_request(self, method: str, endpoint: str, params: dict = None, query_params: dict = None):
        url = f'{self.base_url}{endpoint}'
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=query_params, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=self.headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=params, headers=self.headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=query_params, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            try:
                error_data = http_err.response.json()
                raise KeyMintApiError(
                    message=error_data.get('message', 'An API error occurred'),
                    code=error_data.get('code', -1),
                    status=http_err.response.status_code
                )
            except ValueError:
                raise KeyMintApiError(
                    message=str(http_err),
                    code=-1,
                    status=http_err.response.status_code
                )
        except Exception as err:
            raise KeyMintApiError(message=str(err), code=-1)

    def create_key(self, params: CreateKeyParams) -> CreateKeyResponse:
        """
        Creates a new license key.
        :param params: Parameters for creating the key.
        :returns: The created key information.
        """
        return self._handle_request('POST', '/key', params)

    def activate_key(self, params: ActivateKeyParams) -> ActivateKeyResponse:
        """
        Activates a license key for a specific device.
        :param params: Parameters for activating the key.
        :returns: The activation status.
        """
        return self._handle_request('POST', '/key/activate', params)

    def deactivate_key(self, params: DeactivateKeyParams) -> DeactivateKeyResponse:
        """
        Deactivates a device from a license key.
        :param params: Parameters for deactivating the key.
        :returns: The deactivation confirmation.
        """
        return self._handle_request('POST', '/key/deactivate', params)

    def get_key(self, params: GetKeyParams) -> GetKeyResponse:
        """
        Retrieves detailed information about a specific license key.
        :param params: Parameters for fetching the key details.
        :returns: The license key details.
        """
        query_params = {
            'productId': params['productId'],
            'licenseKey': params['licenseKey']
        }
        return self._handle_request('GET', '/key', query_params=query_params)

    def block_key(self, params: BlockKeyParams) -> BlockKeyResponse:
        """
        Blocks a specific license key.
        :param params: Parameters for blocking the key.
        :returns: The block confirmation.
        """
        return self._handle_request('POST', '/key/block', params)

    def unblock_key(self, params: UnblockKeyParams) -> UnblockKeyResponse:
        """
        Unblocks a previously blocked license key.
        :param params: Parameters for unblocking the key.
        :returns: The unblock confirmation.
        """
        return self._handle_request('POST', '/key/unblock', params)

    # Customer Management Methods
    
    def create_customer(self, params: CreateCustomerParams) -> CreateCustomerResponse:
        """
        Creates a new customer.
        :param params: Parameters for creating the customer.
        :returns: The created customer information.
        """
        return self._handle_request('POST', '/customer', params)

    def get_all_customers(self) -> GetAllCustomersResponse:
        """
        Retrieves all customers associated with the authenticated user's account.
        :returns: List of all customers.
        """
        return self._handle_request('GET', '/customer')

    def get_customer_by_id(self, params: GetCustomerByIdParams) -> GetCustomerByIdResponse:
        """
        Retrieves detailed information about a specific customer by their unique ID.
        :param params: Parameters containing the customer ID.
        :returns: The customer information.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('GET', '/customer/by-id', query_params=query_params)

    def update_customer(self, params: UpdateCustomerParams) -> UpdateCustomerResponse:
        """
        Updates an existing customer's information.
        :param params: Parameters for updating the customer.
        :returns: The update confirmation.
        """
        return self._handle_request('PUT', '/customer/by-id', params)

    def delete_customer(self, params: DeleteCustomerParams) -> DeleteCustomerResponse:
        """
        Permanently deletes a customer and all associated license keys.
        :param params: Parameters containing the customer ID.
        :returns: The deletion confirmation.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('DELETE', '/customer/by-id', query_params=query_params)

    def get_customer_with_keys(self, params: GetCustomerWithKeysParams) -> GetCustomerWithKeysResponse:
        """
        Retrieves detailed information about a customer along with their license keys.
        :param params: Parameters containing the customer ID.
        :returns: The customer information with associated license keys.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('GET', '/customer/keys', query_params=query_params)

    def toggle_customer_status(self, params: ToggleCustomerStatusParams) -> ToggleCustomerStatusResponse:
        """
        Toggles the active status of a customer account (disable or enable).
        :param params: Parameters containing the customer ID.
        :returns: The status toggle confirmation.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('POST', '/customer/disable', params=None, query_params=query_params)

    def get_customer_with_keys(self, params: GetCustomerWithKeysParams) -> GetCustomerWithKeysResponse:
        """
        Retrieves detailed information about a customer along with their license keys.
        :param params: Parameters containing the customer ID.
        :returns: The customer information with associated license keys.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('GET', '/customer/keys', query_params=query_params)
