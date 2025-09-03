"""The main GraphQL client for SlipperPy energy management."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import ValidationError

from slipperpy.exceptions import (
    AuthenticationError,
    GraphQLError,
    NetworkError,
    SlipperError,
    TimeoutError,
)
from slipperpy.models import (
    GraphQLRequest,
    GraphQLResponse,
    HomeType,
    ConsumptionType,
    ElectricityPriceType,
    PlanType,
    ProviderType,
    UserType,
    DeviceType,
)


class SlipperClient:
    """A GraphQL client for Slipper Energy Management systems."""

    def __init__(
        self,
        endpoint: str = "https://api.slipper.no/graphql/",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the SlipperClient.

        Args:
            endpoint: The GraphQL endpoint URL
            headers: Optional headers to include with requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Set default headers
        self._headers = {
          #  "Content-Type": "application/json",
          #  "Accept": "application/json",
            "User-Agent": "SlipperPy/0.1.0",
        }
        
        if headers:
            self._headers.update(headers)

        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl,
            headers=self._headers,
        )

    async def __aenter__(self) -> "SlipperClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def set_auth_token(self, token: str) -> None:
        """Set the authorization token.

        Args:
            token: The bearer token to use for authentication
        """
        self._headers["Authorization"] = f"Bearer {token}"
        self._client.headers.update(self._headers)

    def set_header(self, key: str, value: str) -> None:
        """Set a custom header.

        Args:
            key: The header name
            value: The header value
        """
        self._headers[key] = value
        self._client.headers.update({key: value})

    async def execute(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> GraphQLResponse:
        """Execute a GraphQL query or mutation.

        Args:
            query: The GraphQL query or mutation string
            variables: Optional variables for the query
            operation_name: Optional operation name

        Returns:
            GraphQLResponse: The response from the GraphQL server

        Raises:
            NetworkError: If there's a network-related error
            GraphQLError: If the GraphQL server returns errors
            ValidationError: If the response cannot be parsed
        """
        request = GraphQLRequest(
            query=query,
            variables=variables,
            operation_name=operation_name,
        )

        try:
            response = await self._client.post(
                self.endpoint,
                json=request.dict(exclude_none=True, by_alias=True),
            )
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            print("Raw response:", response)
            raise NetworkError(f"Network error: {e}") from e
        except Exception as e:
            raise SlipperError(f"Unexpected error: {e}") from e

        # Handle HTTP errors
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed")
        elif response.status_code == 403:
            raise AuthenticationError("Access forbidden")
        elif response.status_code >= 400:
            print("Raw response:", response.text)
            raise NetworkError(
                f"HTTP {response.status_code}: {response.reason_phrase}",
                status_code=response.status_code,
                response_text=response.text,
            )

        # Parse response
        try:
            print("Raw response:", response)
            print("Endpoint:", self.endpoint)
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise NetworkError(f"Invalid JSON response: {e}") from e

        # Validate response structure
        try:
            graphql_response = GraphQLResponse(**response_data)
        except ValidationError as e:
            raise SlipperError(f"Invalid GraphQL response format: {e}") from e

        # Check for GraphQL errors
        if graphql_response.has_errors:
            error_messages = [error.message for error in graphql_response.errors or []]
            raise GraphQLError(f"GraphQL errors: {', '.join(error_messages)}")

        return graphql_response

    async def execute_raw(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a GraphQL query and return raw response data.

        Args:
            query: The GraphQL query or mutation string
            variables: Optional variables for the query
            operation_name: Optional operation name

        Returns:
            Dict[str, Any]: The raw response data

        Raises:
            NetworkError: If there's a network-related error
            GraphQLError: If the GraphQL server returns errors
        """
        response = await self.execute(query, variables, operation_name)
        return response.data or {}

    # Authentication methods
    async def request_sms_code(
        self, 
        phone_number: str,
        android: bool = False,
        language: str = "en",
        referred_by_code: Optional[str] = None
    ) -> bool:
        """Request SMS verification code for login.

        Args:
            phone_number: The user's phone number
            android: Whether this is an Android device
            language: Language preference
            referred_by_code: Optional referral code

        Returns:
            bool: True if SMS was sent successfully

        Raises:
            AuthenticationError: If SMS request fails
        """
        mutation = """
        mutation SMSLogin(
            $number: String!,
            $android: Boolean,
            $lang: String,
            $referredByCode: String
        ) {
            smsLogin(
                number: $number,
                android: $android,
                lang: $lang,
                referredByCode: $referredByCode
            ) {
                token
            }
        }
        """

        print("Preparing to request SMS code...")
        variables = {
            "number": phone_number,
            "android": android,
            "lang": language,
        }
        if referred_by_code:
            variables["referredByCode"] = referred_by_code

        try:
            response = await self.execute(mutation, variables)
            print("SMS request response:", response)
            print("Parsed response:", response.data)
            result = response.data.get("smsLogin", {}) if response.data else {}
            return result.get("token", True)
        except GraphQLError as e:
            print("GraphQL error during SMS request:", e)
            raise AuthenticationError(f"SMS request failed: {e.message}") from e

    async def login_with_sms_code(
        self, 
        phone_number: str, 
        sms_code: int,
        android: bool = False,
        language: str = "en"
    ) -> str:
        """Complete login with SMS verification code.

        Args:
            phone_number: The user's phone number
            sms_code: The SMS verification code received
            android: Whether this is an Android device
            language: Language preference

        Returns:
            str: The JWT token

        Raises:
            AuthenticationError: If authentication fails
        """
        mutation = """
        mutation SMSLogin(
            $number: String!,
            $code: Int!,
            $android: Boolean,
            $lang: String
        ) {
            smsLogin(
                number: $number,
                code: $code,
                android: $android,
                lang: $lang
            ) {
        token
        found
        hasUser
            }
        }
        """
        try:
            response = await self.execute(mutation, {
                "number": phone_number,
                "code": sms_code,
                "android": android,
                "lang": language
            })
            result = response.data.get("smsLogin", {}) if response.data else {}
            
            if not result.get("token"):
                raise AuthenticationError("SMS verification failed")
            
            return result.get("token")

        except GraphQLError as e:
            raise AuthenticationError(f"SMS verification failed: {e.message}") from e

    async def login_with_phone_and_password(self, phone_number: str, password: str) -> str:
        """Login with phone number and password (if supported).

        Args:
            phone_number: The user's phone number
            password: The user's password

        Returns:
            str: The JWT token

        Raises:
            AuthenticationError: If authentication fails
        """
        mutation = """
        mutation TokenAuth($phoneNumber: String!, $password: String!) {
            tokenAuth(phoneNumber: $phoneNumber, password: $password) {
                token
                payload
                refreshExpiresIn
            }
        }
        """
        try:
            response = await self.execute(mutation, {
                "phoneNumber": phone_number,
                "password": password
            })
            token_data = response.data.get("tokenAuth") if response.data else None
            if not token_data or not token_data.get("token"):
                raise AuthenticationError("No token returned from authentication")
            
            token = token_data["token"]
            self.set_auth_token(token)
            return token
        except GraphQLError as e:
            raise AuthenticationError(f"Authentication failed: {e.message}") from e

    async def login_with_sms(
        self, 
        phone_number: str, 
        code: Optional[int] = None,
        android: bool = False,
        language: str = "en",
        referred_by_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Login with SMS verification - backwards compatibility method.

        Args:
            phone_number: The user's phone number
            code: Optional SMS verification code
            android: Whether this is an Android device
            language: Language preference
            referred_by_code: Optional referral code

        Returns:
            Dict[str, Any]: The response data
        """
        if code is None:
            # Request SMS code
            success = await self.request_sms_code(phone_number, android, language, referred_by_code)
            return {"success": success, "message": "SMS code requested"}
        else:
            # Verify SMS code
            token = await self.login_with_sms_code(phone_number, code, android, language)
            return {"success": True, "token": token}

    # User methods
    async def get_current_user(self) -> Optional[UserType]:
        """Get the current authenticated user.

        Returns:
            Optional[UserType]: The current user or None
        """
        query = """
        query CurrentUser {
            user {
                id
                firstName
                lastName
                email
                isActive
                isStaff
                isSuperuser
                lastLogin
                phoneNumber
                birthDate
            }
        }
        """
        response = await self.execute(query)
        user_data = response.data.get("user") if response.data else None
        return UserType(**user_data) if user_data else None

    async def update_user(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        birth_date: Optional[str] = None,
        firebase_token: Optional[str] = None,
        rc_id: Optional[str] = None,
    ) -> bool:
        """Update user information.

        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email
            birth_date: User's birth date (YYYY-MM-DD format)
            firebase_token: Firebase registration token
            rc_id: RC ID

        Returns:
            bool: True if successful
        """
        mutation = """
        mutation UserUpdate(
            $firstName: String,
            $lastName: String,
            $email: String,
            $birthDate: Date,
            $firebaseToken: String,
            $rcId: String
        ) {
            userUpdate(
                firstName: $firstName,
                lastName: $lastName,
                email: $email,
                birthDate: $birthDate,
                firebaseToken: $firebaseToken,
                rcId: $rcId
            ) {
                success
            }
        }
        """
        variables = {}
        if first_name is not None:
            variables["firstName"] = first_name
        if last_name is not None:
            variables["lastName"] = last_name
        if email is not None:
            variables["email"] = email
        if birth_date is not None:
            variables["birthDate"] = birth_date
        if firebase_token is not None:
            variables["firebaseToken"] = firebase_token
        if rc_id is not None:
            variables["rcId"] = rc_id

        response = await self.execute(mutation, variables)
        return response.data.get("userUpdate", {}).get("success", False) if response.data else False

    # Home methods
    async def get_homes(
        self, 
        all_homes: bool = False, 
        archived: bool = False,
        first: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[HomeType]:
        """Get all homes for the current user.

        Args:
            all_homes: Whether to get all homes
            archived: Whether to include archived homes
            first: Limit number of results
            skip: Skip number of results

        Returns:
            List[HomeType]: List of homes
        """
        query = """
        query GetHomes($all: Boolean, $archived: Boolean, $first: Int, $skip: Int) {
            homes(all: $all, archived: $archived, first: $first, skip: $skip) {
                id
                createdAt
                updatedAt
                meterId
                meterIdentification
                name
                street
                streetNumber
                postalCode
                city
                country
                estimatedYearlyConsumption
                area
                blocked
                isPlus
                isAutomatic
                maxKwh
                type
                user {
                    id
                    firstName
                    lastName
                    email
                    isActive
                    isStaff
                    isSuperuser
                }
                grid {
                    id
                    name
                }
                currentPlan {
                    id
                }
            }
        }
        """
        variables = {
            "all": all_homes,
            "archived": archived,
        }
        if first is not None:
            variables["first"] = first
        if skip is not None:
            variables["skip"] = skip

        response = await self.execute(query, variables)
        homes_data = response.data.get("homes", []) if response.data else []
        return [HomeType(**home) for home in homes_data]

    async def get_home(self, home_id: str) -> Optional[HomeType]:
        """Get a specific home by ID.

        Args:
            home_id: The home ID

        Returns:
            Optional[HomeType]: The home or None if not found
        """
        query = """
        query GetHome($id: ID!) {
            home(id: $id) {
                id
                createdAt
                updatedAt
                meterId
                meterIdentification
                name
                street
                streetNumber
                postalCode
                city
                country
                estimatedYearlyConsumption
                area
                blocked
                isPlus
                isAutomatic
                maxKwh
                type
                user {
                    id
                    firstName
                    lastName
                    email
                }
                grid {
                    id
                    name
                    area
                }
                currentPlan {
                    id
                    name
                    provider
                    pricePerKwh
                    fixedFee
                }
            }
        }
        """
        response = await self.execute(query, {"id": home_id})
        home_data = response.data.get("home") if response.data else None
        return HomeType(**home_data) if home_data else None

    # Consumption methods
    async def get_consumptions(
        self,
        home_id: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        granularity: Optional[str] = None,
    ) -> List[ConsumptionType]:
        """Get consumption data.

        Args:
            home_id: The home ID
            start: Start datetime
            end: End datetime
            granularity: Data granularity (e.g., "HOUR", "DAY", "MONTH")

        Returns:
            List[ConsumptionType]: List of consumption data
        """
        query = """
        query GetConsumptions(
            $homeId: ID,
            $start: DateTime,
            $end: DateTime,
            $granularity: String
        ) {
            consumptions(
                homeId: $homeId,
                start: $start,
                end: $end,
                granularity: $granularity
            ) {
                id
                createdAt
                updatedAt
                meterId
                date
                kwh
                granularity
                meteringType
                cost
                tax
                handout
                tariff
                tariffTax
                enova
                tariffAddition
                planAddition
            }
        }
        """
        variables = {}
        if home_id:
            variables["homeId"] = home_id
        if start:
            variables["start"] = start.isoformat()
        if end:
            variables["end"] = end.isoformat()
        if granularity:
            variables["granularity"] = granularity

        response = await self.execute(query, variables)
        consumptions_data = response.data.get("consumptions", []) if response.data else []
        return [ConsumptionType(**consumption) for consumption in consumptions_data]

    # Electricity price methods
    async def get_electricity_prices(
        self,
        start: datetime,
        end: datetime,
        granularity: str = "HOUR",
        area: str = "NO1",
        forecast: bool = False,
    ) -> List[ElectricityPriceType]:
        """Get electricity price data.

        Args:
            start: Start datetime
            end: End datetime
            granularity: Data granularity
            area: Price area
            forecast: Whether to include forecast data

        Returns:
            List[ElectricityPriceType]: List of electricity prices
        """
        query = """
        query GetElectricityPrices(
            $start: DateTime!,
            $end: DateTime!,
            $granularity: String!,
            $area: String!,
            $forcast: Boolean
        ) {
            electricityPrices(
                start: $start,
                end: $end,
                granularity: $granularity,
                area: $area,
                forcast: $forcast
            ) {
                date
                area
                priceKwh
                granularity
            }
        }
        """
        response = await self.execute(query, {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "granularity": granularity,
            "area": area,
            "forcast": forecast,
        })
        prices_data = response.data.get("electricityPrices", []) if response.data else []
        return [ElectricityPriceType(**price) for price in prices_data]

    # Plan methods
    async def get_plans(
        self,
        provider_id: Optional[str] = None,
        active: Optional[bool] = None,
        show_all: bool = False,
    ) -> List[PlanType]:
        """Get electricity plans.

        Args:
            provider_id: Filter by provider ID
            active: Filter by active status
            show_all: Show all plans

        Returns:
            List[PlanType]: List of plans
        """
        query = """
        query GetPlans($providerId: ID, $active: Boolean, $showAll: Boolean) {
            plans(providerId: $providerId, active: $active, showAll: $showAll) {
                id
                name
                provider {
                    id
                    name
                }
                pricePerKwh
                fixedFee
                offerType
            }
        }
        """
        variables = {"showAll": show_all}
        if provider_id:
            variables["providerId"] = provider_id
        if active is not None:
            variables["active"] = active

        response = await self.execute(query, variables)
        plans_data = response.data.get("plans", []) if response.data else []
        return [PlanType(**plan) for plan in plans_data]

    # Provider methods
    async def get_providers(self) -> List[ProviderType]:
        """Get all electricity providers.

        Returns:
            List[ProviderType]: List of providers
        """
        query = """
        query GetProviders {
            providers {
                id
                name
                website
                phone
                email
            }
        }
        """
        response = await self.execute(query)
        providers_data = response.data.get("providers", []) if response.data else []
        return [ProviderType(**provider) for provider in providers_data]
    
    # Get devices
    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices.

        Returns:
            List[Dict[str, Any]]: List of devices
        """
        query = """
        query GetDevices {
            user {
                devices {
                    id
                    name
                    firebaseRegistrationToken
                    fingerprint
                    type
                }
            }
        }
        """
        response = await self.execute(query)
        devices_data = response.data.get("user", {}).get("devices", []) if response.data else []
        return [DeviceType(**device) for device in devices_data]
