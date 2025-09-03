# Postcode.eu API Python Client

A Python client library for the [Postcode.eu API](https://developer.postcode.eu/documentation), providing access to international address autocomplete, Dutch address lookup, and validation services.

## Installation

```bash
uv add postcode-eu-api-client
# Or
pip install postcode-eu-api-client
```


## Quick Start

```python
from postcode_eu_api_client import Client

# Initialize the client
client = Client('your_api_key', 'your_api_secret', 'YourApp/1.0')

# International address autocomplete
import secrets
session_id = secrets.token_hex(16)
result = client.international_autocomplete(
    context='nld',
    term='den',
    session=session_id
)

# Dutch postcode lookup
address = client.dutch_address_by_postcode('1012JS', 1)

# Validate international address
validation = client.validate(
    country='bel',
    postcode='2000',
    locality='antwerpen',
    street='leystraat'
)
```

## API Methods Overview

### International Addresses
- `international_autocomplete()` - Autocomplete an address
- `international_get_details()` - Get address details
- `international_get_supported_countries()` - List supported countries

### Dutch Address Addresses
- `dutch_address_by_postcode()` - Lookup by postcode and house number
- `dutch_address_rd()` - Lookup by RD (Rijksdriehoeksmeting) coordinates
- `dutch_address_lat_lon()` - Lookup by latitude and longitude
- `dutch_address_bag_number_designation()` - Lookup by BAG Number Designation ID
- `dutch_address_bag_addressable_object()` - Lookup by BAG Addressable Object ID
- `dutch_address_postcode_ranges()` - Lookup streets and house number ranges by postcode

### Validate Addresses
- `validate()` - Validate international addresses
- `get_country()` - Get country information

### Accounts
- `account_info()` - Get account information
- `create_client_account()` - Create client account (resellers only)

View full documentation at https://developer.postcode.eu/documentation.

## Exception Handling

The client provides specific exceptions for different error conditions:

```python
from postcode_eu_api_client import Client, InvalidPostcodeException, AuthenticationException

client = Client('key', 'secret', 'platform')

try:
    result = client.dutch_address_by_postcode('invalid', 1)
except InvalidPostcodeException as e:
    print(f"Invalid postcode format: {e}")
except AuthenticationException as e:
    print(f"Authentication failed: {e}")
```

### Available Exceptions

* `PostcodeEuException` - Base exception for all Postcode.eu API client exceptions
* `AuthenticationException` - Authentication failed with the API
* `BadRequestException` - Bad request sent to the API
* `CurlException` - HTTP request error (equivalent to cURL error in PHP)
* `CurlNotLoadedException` - HTTP library not available (equivalent to cURL not loaded in PHP)
* `ForbiddenException` - Access forbidden by the API
* `InvalidJsonResponseException` - Invalid JSON response received from the API
* `InvalidPostcodeException` - Invalid postcode format provided
* `InvalidSessionValueException` - Invalid session value provided
* `NotFoundException` - Resource not found
* `ServerUnavailableException` - API server is unavailable
* `TooManyRequestsException` - Too many requests sent to the API
* `UnexpectedException` - Unexpected response from the API

## Requirements

- Python 3.10+
- A postcode.eu account. Register your account at account.postcode.eu. You can test our service for free.

## Examples

This repository includes examples for each API method. See [examples/README.md](examples/README.md) for usage.

## License

The code is available under the Simplified BSD License, see the included LICENSE file.
