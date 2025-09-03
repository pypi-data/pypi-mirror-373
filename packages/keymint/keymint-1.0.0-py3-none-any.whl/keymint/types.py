from typing import TypedDict, Optional, List, Dict, Any

class NewCustomer(TypedDict):
    name: str
    email: Optional[str]

class CreateKeyParams(TypedDict):
    productId: str
    maxActivations: Optional[str]
    expiryDate: Optional[str]
    customerId: Optional[str]
    newCustomer: Optional[NewCustomer]

class CreateKeyResponse(TypedDict):
    code: int
    key: str

class KeyMintApiError(Exception):
    def __init__(self, message: str, code: int, status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status

class ActivateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: Optional[str]
    deviceTag: Optional[str]

class ActivateKeyResponse(TypedDict):
    code: int
    message: str
    licenseeName: Optional[str]
    licenseeEmail: Optional[str]

class DeactivateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: Optional[str]

class DeactivateKeyResponse(TypedDict):
    message: str
    code: int

class DeviceDetails(TypedDict):
    hostId: str
    deviceTag: Optional[str]
    ipAddress: Optional[str]
    activationTime: str

class LicenseDetails(TypedDict):
    id: str
    key: str
    productId: str
    maxActivations: int
    activations: int
    devices: List[DeviceDetails]
    activated: bool
    expirationDate: Optional[str]

class CustomerDetails(TypedDict):
    id: str
    name: Optional[str]
    email: Optional[str]
    active: bool

class GetKeyParams(TypedDict):
    productId: str
    licenseKey: str

class GetKeyResponse(TypedDict):
    data: Dict[str, Any]
    code: int

class BlockKeyParams(TypedDict):
    productId: str
    licenseKey: str

class BlockKeyResponse(TypedDict):
    message: str
    code: int

class UnblockKeyParams(TypedDict):
    productId: str
    licenseKey: str

class UnblockKeyResponse(TypedDict):
    message: str
    code: int

# Customer Management Types

class CreateCustomerParams(TypedDict):
    name: str
    email: str

class CreateCustomerResponse(TypedDict):
    action: str
    status: bool
    message: str
    data: Dict[str, Any]
    code: int

class GetAllCustomersResponse(TypedDict):
    action: str
    status: bool
    data: List[Dict[str, Any]]
    code: int

class GetCustomerByIdParams(TypedDict):
    customerId: str

class GetCustomerByIdResponse(TypedDict):
    action: str
    status: bool
    data: List[Dict[str, Any]]
    code: int

class UpdateCustomerParams(TypedDict):
    name: str
    email: str
    customerId: str

class UpdateCustomerResponse(TypedDict):
    action: str
    status: bool
    code: int

class DeleteCustomerParams(TypedDict):
    customerId: str

class DeleteCustomerResponse(TypedDict):
    action: str
    status: bool
    code: int

class ToggleCustomerStatusParams(TypedDict):
    customerId: str

class ToggleCustomerStatusResponse(TypedDict):
    action: str
    status: bool
    message: str
    code: int

class CustomerLicenseKey(TypedDict):
    id: str
    key: str
    productId: str
    maxActivations: int
    activations: int
    activated: bool
    expirationDate: Optional[str]

class GetCustomerWithKeysParams(TypedDict):
    customerId: str

class GetCustomerWithKeysResponse(TypedDict):
    action: str
    status: bool
    data: Dict[str, Any]  # Contains customer and licenseKeys
    code: int
