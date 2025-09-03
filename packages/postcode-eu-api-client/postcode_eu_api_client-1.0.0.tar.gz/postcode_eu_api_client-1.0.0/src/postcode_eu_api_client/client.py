"""Postcode.eu API client for Python."""

import re
import sys
import importlib.metadata
from typing import Any, cast
from urllib.parse import quote

try:
    import requests
except ImportError:
    raise ImportError("requests library is required. Install it with: pip install requests")

from .exceptions import (
    AuthenticationException,
    BadRequestException,
    CurlException,
    ForbiddenException,
    InvalidJsonResponseException,
    InvalidPostcodeException,
    InvalidSessionValueException,
    NotFoundException,
    ServerUnavailableException,
    TooManyRequestsException,
    UnexpectedException,
)


class Client:
    SESSION_HEADER_KEY = 'X-Autocomplete-Session'
    SESSION_HEADER_VALUE_VALIDATION = r'^[a-z\d\-_.]{8,64}$'

    _SERVER_URL = 'https://api.postcode.eu/'

    def __init__(self, key: str, secret: str, platform: str):
        """
        Initialize the Postcode.eu API client.

        Args:
            key: The Postcode.eu API key, provided when registering an account.
            secret: The Postcode.eu API secret, provided when registering an account.
            platform: A platform identifier, short description of the platform using the API client.
        """
        self._key = key
        self._secret = secret
        self._platform = platform
        self._most_recent_response_headers: dict[str, list[str]] = {}

        # Create a persistent session for connection reuse
        self._session = requests.Session()
        self._session.auth = (self._key, self._secret)
        self._session.headers.update({
            'User-Agent': self._get_user_agent()
        })

    def international_autocomplete(
        self,
        context: str,
        term: str,
        session: str,
        language: str | None = None,
        building_list_mode: str | None = None
    ) -> dict[str, Any]:
        """
        Autocomplete international addresses.

        https://developer.postcode.eu/documentation/international/v1/Autocomplete/autocomplete
        """
        self._validate_session_header(session)
        params = [context, term]

        if building_list_mode is not None:
            params.append(language or '')
            params.append(building_list_mode)
        elif language is not None:
            params.append(language)

        params = [quote(param, safe='') for param in params]
        path = 'international/v1/autocomplete/' + '/'.join(params)

        return self._api_get(path, session)

    def international_get_details(self, context: str, session: str) -> dict[str, Any]:
        """
        Get address information based on the provided autocomplete context.

        https://developer.postcode.eu/documentation/international/v1/Autocomplete/getDetails
        """
        self._validate_session_header(session)
        path = 'international/v1/address/' + quote(context, safe='')

        return self._api_get(path, session)

    def international_get_supported_countries(self) -> list[dict[str, str]]:
        """
        Fetches list of supported countries. Recommended to cache the result.

        https://developer.postcode.eu/documentation/international/v1/Autocomplete/getSupportedCountries
        """
        response = self._api_get('international/v1/supported-countries', None)
        return cast(list[dict[str, str]], response)

    def dutch_address_by_postcode(
        self,
        postcode: str,
        house_number: int,
        house_number_addition: str | None = None
    ) -> dict[str, Any]:
        """
        Get an address based on its unique combination of postcode, house number and house number addition.

        https://developer.postcode.eu/documentation/nl/v1/Address/viewByPostcode
        """
        # Validate postcode format
        postcode = postcode.strip()
        if not self.is_valid_dutch_postcode_format(postcode):
            raise InvalidPostcodeException(
                f'Postcode `{postcode}` has an invalid format, it should be in the format 1234AB.'
            )

        url_parts = [
            'nl/v1/addresses/postcode',
            quote(postcode, safe=''),
            str(house_number),
        ]
        if house_number_addition is not None:
            url_parts.append(quote(house_number_addition.strip(), safe=''))

        return self._api_get('/'.join(url_parts), None)

    def dutch_address_rd(self, rd_x: float, rd_y: float) -> dict[str, Any]:
        """
        Get the closest Dutch address based on Dutch Rijksdriehoeksmeting coordinates.

        https://developer.postcode.eu/documentation/nl/v1/Address/viewByRd
        """
        url_parts = [
            'nl/v1/addresses/rd',
            quote(str(rd_x), safe=''),
            quote(str(rd_y), safe=''),
        ]

        return self._api_get('/'.join(url_parts), None)

    def dutch_address_lat_lon(self, latitude: float, longitude: float) -> dict[str, Any]:
        """
        Get the closest Dutch address based on latitude and longitude.

        https://developer.postcode.eu/documentation/nl/v1/Address/viewByLatLon
        """
        url_parts = [
            'nl/v1/addresses/latlon',
            quote(str(latitude), safe=''),
            quote(str(longitude), safe=''),
        ]

        return self._api_get('/'.join(url_parts), None)

    def dutch_address_bag_number_designation(self, bag_number_designation_id: str) -> dict[str, Any]:
        """
        Get the unique Dutch address connected to a BAG Number Designation ID ("Nummeraanduiding ID").

        https://developer.postcode.eu/documentation/nl/v1/Address/viewByBagNumberDesignationId
        """
        url_parts = [
            'nl/v1/addresses/bag/number-designation',
            quote(bag_number_designation_id, safe=''),
        ]

        return self._api_get('/'.join(url_parts), None)

    def dutch_address_bag_addressable_object(self, bag_addressable_object_id: str) -> dict[str, Any]:
        """
        Get the Dutch address(es) connected to a BAG Addressable Object ID.

        https://developer.postcode.eu/documentation/nl/v1/Address/viewByBagAddressableObjectId
        """
        url_parts = [
            'nl/v1/addresses/bag/addressable-object',
            quote(bag_addressable_object_id, safe=''),
        ]

        return self._api_get('/'.join(url_parts), None)

    def dutch_address_postcode_ranges(self, postcode: str) -> dict[str, Any]:
        """
        Get all streets and house number ranges for the provided postcode.

        https://developer.postcode.eu/documentation/nl/v1/PostcodeRange/viewByPostcode
        """
        # Validate postcode format
        postcode = postcode.strip()
        if not self.is_valid_dutch_postcode_format(postcode):
            raise InvalidPostcodeException(
                f'Postcode `{postcode}` has an invalid format, it should be in the format `1234AB`.'
            )

        url_parts = [
            'nl/v1/postcode-ranges/postcode',
            quote(postcode, safe=''),
        ]

        return self._api_get('/'.join(url_parts), None)

    def validate(
        self,
        country: str,
        postcode: str | None = None,
        locality: str | None = None,
        street: str | None = None,
        building: str | None = None,
        region: str | None = None,
        street_and_building: str | None = None
    ) -> dict[str, Any]:
        """
        Validate a full address, correcting and completing all parts of the address.

        https://developer.postcode.eu/documentation/international/v1/Validate/validate
        """
        url_parts = [
            'international/v1/validate',
            quote(country, safe='')
        ]

        variables = {
            'postcode': postcode,
            'locality': locality,
            'street': street,
            'building': building,
            'region': region,
            'streetAndBuilding': street_and_building,
        }

        parameters = []
        for key, value in variables.items():
            if value is not None:
                parameters.append(f'{key}={quote(value, safe="")}')

        path = '/'.join(url_parts)
        if parameters:
            path += '?' + '&'.join(parameters)

        return self._api_get(path, None)

    def get_country(self, country: str) -> dict[str, Any]:
        """
        Get country information.

        https://developer.postcode.eu/documentation/international/v1/Validate/getCountry
        """
        url_parts = [
            'international/v1/country',
            quote(country, safe=''),
        ]

        return self._api_get('/'.join(url_parts), None)

    def create_client_account(
        self,
        company_name: str,
        country_iso: str,
        vat_number: str,
        contact_email: str,
        subscription_amount: int,
        site_urls: list[str] | str,
        invoice_email: str,
        invoice_reference: str,
        invoice_address_line1: str,
        invoice_address_line2: str,
        invoice_address_postal_code: str,
        invoice_address_locality: str,
        invoice_address_region: str,
        invoice_address_country_iso: str,
        invoice_contact_name: str | None = None,
        is_test: bool = False
    ) -> dict[str, Any]:
        """
        Create an account for your client. The new account will be linked to your reseller account.

        This method is only available to reseller accounts.

        https://developer.postcode.eu/documentation/reseller/v1/Reseller/createClientAccount
        """
        if isinstance(site_urls, str):
            site_urls = [url.strip() for url in site_urls.split(',') if url.strip()]

        post_data = {
            'companyName': company_name,
            'countryIso': country_iso,
            'vatNumber': vat_number,
            'contactEmail': contact_email,
            'subscriptionAmount': subscription_amount,
            'siteUrls': site_urls,
            'invoiceEmail': invoice_email,
            'invoiceReference': invoice_reference,
            'invoiceAddressLine1': invoice_address_line1,
            'invoiceAddressLine2': invoice_address_line2,
            'invoiceAddressPostalCode': invoice_address_postal_code,
            'invoiceAddressLocality': invoice_address_locality,
            'invoiceAddressRegion': invoice_address_region,
            'invoiceAddressCountryIso': invoice_address_country_iso,
        }

        if invoice_contact_name is not None:
            post_data['invoiceContactName'] = invoice_contact_name
        if is_test:
            post_data['isTest'] = True

        return self._api_post('reseller/v1/client', post_data)

    def account_info(self) -> dict[str, Any]:
        """
        Retrieve basic account information for the currently authenticated account.

        https://developer.postcode.eu/documentation/account/v1/Account/getInfo
        """
        return self._api_get('account/v1/info', None)

    def get_api_call_response_headers(self) -> dict[str, list[str]]:
        """Get the response headers from the most recent API call."""
        return self._most_recent_response_headers

    def is_valid_dutch_postcode_format(self, postcode: str) -> bool:
        """
        Validate if string has a correct Dutch postcode format.

        Args:
            postcode: The postcode to validate

        Returns:
            True if valid Dutch postcode format, False otherwise
        """
        return bool(re.match(r'^[1-9]\d{3}\s?[a-zA-Z]{2}$', postcode))

    def _validate_session_header(self, session: str) -> None:
        """Validate session header value format."""
        if not re.match(self.SESSION_HEADER_VALUE_VALIDATION, session, re.IGNORECASE):
            raise InvalidSessionValueException(
                f'Session value `{session}` does not conform to `{self.SESSION_HEADER_VALUE_VALIDATION}`, '
                'please refer to the API documentation for further information.'
            )

    def _api_get(self, path: str, session: str | None) -> dict[str, Any]:
        """Perform a GET call to the API."""
        url = self._SERVER_URL + path
        headers = {}
        if session is not None:
            headers[self.SESSION_HEADER_KEY] = session

        return self._request('GET', url, headers=headers)

    def _api_post(self, path: str, post_data: dict[str, Any]) -> dict[str, Any]:
        """Perform a POST call to the API."""
        url = self._SERVER_URL + path
        return self._request('POST', url, data=post_data)

    def _request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Perform the actual HTTP request."""
        try:
            if method == 'POST':
                response = self._session.post(url, json=data, headers=headers or {}, timeout=(2, 5))
            else:
                response = self._session.get(url, headers=headers or {}, timeout=(2, 5))
        except requests.exceptions.RequestException as e:
            raise CurlException(f'Connection error: {str(e)}')

        # Store response headers
        self._most_recent_response_headers = {}
        for name, value in response.headers.items():
            name_lower = name.lower()
            if name_lower not in self._most_recent_response_headers:
                self._most_recent_response_headers[name_lower] = []
            self._most_recent_response_headers[name_lower].append(value)

        # Handle different response status codes
        status_code = response.status_code

        if status_code == 200:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                raise InvalidJsonResponseException(f'Invalid JSON response from the server for request: {url}')
        elif status_code == 400:
            raise BadRequestException(f'Server response code 400, bad request for `{url}`.')
        elif status_code == 401:
            raise AuthenticationException('Could not authenticate your request, please make sure your API credentials are correct.')
        elif status_code == 403:
            try:
                json_response = response.json()
                exception_msg = json_response.get('exception', 'Unknown error')
            except requests.exceptions.JSONDecodeError:
                exception_msg = 'Unknown error'
            raise ForbiddenException(f'API access not allowed: `{exception_msg}`')
        elif status_code == 404:
            raise NotFoundException('The request was valid, but nothing could be found.')
        elif status_code == 429:
            raise TooManyRequestsException(f'Too many requests made, please slow down: {response.text}')
        elif status_code == 503:
            raise ServerUnavailableException(f'The international API server is currently not available: {response.text}')
        else:
            raise UnexpectedException(f'Unexpected server response code `{status_code}`.')

    def _get_user_agent(self) -> str:
        """Generate the User-Agent string."""
        version = importlib.metadata.version('postcode-eu-api-client')
        agent = f'{self._platform} {self.__class__.__module__}/{version} Python/{sys.version.split()[0]}'
        return agent[:1024]  # Prevent exceeding max allowed header length
