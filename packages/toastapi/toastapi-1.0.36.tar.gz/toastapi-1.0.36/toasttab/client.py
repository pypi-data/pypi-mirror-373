"""
Toast API Client

A simplified wrapper around the generated OpenAPI client.
"""

import asyncio
import time
from typing import Optional, Callable, Awaitable
from toastapi.api_client import ApiClient
from toastapi.configuration import Configuration
from toastapi.api import (
    AlternatePaymentTypesApi,
    AuthenticationApi,
    BreakTypesApi,
    CashDrawersApi,
    DiningOptionsApi,
    DiscountsApi,
    EmployeesApi,
    JobsApi,
    MenuGroupsApi,
    MenuItemsApi,
    MenusV2Api,
    MenusV3Api,
    NoSaleReasonsApi,
    OrdersApi,
    PaymentsApi,
    PayoutReasonsApi,
    PreModifierGroupsApi,
    PreModifiersApi,
    PriceGroupsApi,
    PrintersApi,
    RestaurantServicesApi,
    RestaurantsApi,
    RevenueCentersApi,
    ServiceAreasApi,
    ServiceChargesApi,
    ShiftsApi,
    TablesApi,
    TaxRatesApi,
    TimeEntriesApi,
    TipWithholdingApi,
    VoidReasonsApi,
)
from toastapi.models.authentication_request import AuthenticationRequest


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        retry_on_exceptions: tuple = (Exception,),
        retry_condition: Optional[Callable[[Exception], bool]] = None,
    ):
        """
        Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Multiplier for delay after each retry
            retry_on_exceptions: Tuple of exceptions to retry on
            retry_condition: Optional function to determine if retry should occur
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retry_on_exceptions = retry_on_exceptions
        self.retry_condition = retry_condition


class Toast:
    """
    A simplified async client for the Toast Platform API.

    This client handles authentication automatically and provides
    easy access to all API endpoints with built-in retry logic.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        environment: str = "sandbox",
        host: Optional[str] = None,
        token: Optional[str] = None,
        token_expires_at: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
        token_refresh_callback: Optional[
            Callable[[str, float], Awaitable[None]]
        ] = None,
    ):
        """
        Initialize the Toast client.

        Args:
            client_id: Your Toast API client ID
            client_secret: Your Toast API client secret
            environment: The environment to use ('sandbox' or 'production')
            host: Optional custom host URL (overrides environment).
                 Must be one of the valid Toast base URLs:
                 - https://ws-sandbox-api.eng.toasttab.com (sandbox)
                 - https://ws-api.toasttab.com (production)
            token: Optional pre-existing auth token
            token_expires_at: Optional token expiration timestamp
            retry_config: Optional retry configuration (defaults to 3 retries, 1s delay)
            token_refresh_callback: Optional callback(token, expires_at) to execute after token refresh
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment
        self.retry_config = retry_config or RetryConfig()
        self._token_refresh_callback = token_refresh_callback

        # Determine the host URL
        if host:
            # Validate that the host is one of the valid base URLs
            valid_base_hosts = [
                "https://ws-sandbox-api.eng.toasttab.com",
                "https://ws-api.toasttab.com",
            ]
            if host not in valid_base_hosts:
                raise ValueError(
                    f"Invalid host URL. Must be one of: {', '.join(valid_base_hosts)}"
                )
            self.host = host
        elif environment.lower() == "production":
            self.host = "https://ws-api.toasttab.com"
        elif environment.lower() == "sandbox":
            self.host = "https://ws-sandbox-api.eng.toasttab.com"
        else:
            raise ValueError("Environment must be 'sandbox' or 'production'")

        self._token = token
        self._token_expires_at = token_expires_at

        # Initialize the API client
        self._config = Configuration(host=self.host)
        if environment.lower() == "sandbox":
            self._config.verify_ssl = False  # Ignore SSL verification for sandbox

        # Set token in configuration if provided
        if token:
            self._config.access_token = token

        self._api_client = ApiClient(configuration=self._config)

        # Initialize API classes with retry wrappers
        self.auth: AuthenticationApi = self._create_retry_wrapper(AuthenticationApi)
        self.orders: OrdersApi = self._create_retry_wrapper(OrdersApi)
        self.employees: EmployeesApi = self._create_retry_wrapper(EmployeesApi)
        self.jobs: JobsApi = self._create_retry_wrapper(JobsApi)
        self.shifts: ShiftsApi = self._create_retry_wrapper(ShiftsApi)
        self.time_entries: TimeEntriesApi = self._create_retry_wrapper(TimeEntriesApi)
        self.payments: PaymentsApi = self._create_retry_wrapper(PaymentsApi)
        self.discounts: DiscountsApi = self._create_retry_wrapper(DiscountsApi)
        self.restaurants: RestaurantsApi = self._create_retry_wrapper(RestaurantsApi)
        self.break_types: BreakTypesApi = self._create_retry_wrapper(BreakTypesApi)
        self.alternate_payment_types: AlternatePaymentTypesApi = (
            self._create_retry_wrapper(AlternatePaymentTypesApi)
        )
        self.cash_drawers: CashDrawersApi = self._create_retry_wrapper(CashDrawersApi)
        self.dining_options: DiningOptionsApi = self._create_retry_wrapper(
            DiningOptionsApi
        )
        self.menus_v2: MenusV2Api = self._create_retry_wrapper(MenusV2Api)
        self.menus_v3: MenusV3Api = self._create_retry_wrapper(MenusV3Api)
        self.menu_groups: MenuGroupsApi = self._create_retry_wrapper(MenuGroupsApi)
        self.menu_items: MenuItemsApi = self._create_retry_wrapper(MenuItemsApi)
        self.printers: PrintersApi = self._create_retry_wrapper(PrintersApi)
        self.tables: TablesApi = self._create_retry_wrapper(TablesApi)
        self.no_sale_reasons: NoSaleReasonsApi = self._create_retry_wrapper(
            NoSaleReasonsApi
        )
        self.payout_reasons: PayoutReasonsApi = self._create_retry_wrapper(
            PayoutReasonsApi
        )
        self.pre_modifier_groups: PreModifierGroupsApi = self._create_retry_wrapper(
            PreModifierGroupsApi
        )
        self.pre_modifiers: PreModifiersApi = self._create_retry_wrapper(
            PreModifiersApi
        )
        self.price_groups: PriceGroupsApi = self._create_retry_wrapper(PriceGroupsApi)
        self.restaurant_services: RestaurantServicesApi = self._create_retry_wrapper(
            RestaurantServicesApi
        )
        self.revenue_centers: RevenueCentersApi = self._create_retry_wrapper(
            RevenueCentersApi
        )
        self.service_areas: ServiceAreasApi = self._create_retry_wrapper(
            ServiceAreasApi
        )
        self.service_charges: ServiceChargesApi = self._create_retry_wrapper(
            ServiceChargesApi
        )
        self.tax_rates: TaxRatesApi = self._create_retry_wrapper(TaxRatesApi)
        self.tip_withholding: TipWithholdingApi = self._create_retry_wrapper(
            TipWithholdingApi
        )
        self.void_reasons: VoidReasonsApi = self._create_retry_wrapper(VoidReasonsApi)

    def _create_retry_wrapper(self, api_class):
        """Create a wrapper class that automatically applies retry logic to all methods."""

        class RetryWrappedApi(api_class):
            def __init__(self, api_client, toast_client):
                super().__init__(api_client)
                self._toast_client = toast_client

            def __getattribute__(self, name):
                """Override to wrap async methods with retry logic."""
                # Use object.__getattribute__ to avoid recursion
                attr = object.__getattribute__(self, name)

                # Only wrap async methods that are callable and not private
                # Exclude authentication methods to prevent infinite recursion
                if (
                    asyncio.iscoroutinefunction(attr)
                    and callable(attr)
                    and not name.startswith("_")
                    and not name.startswith(
                        "authentication_login"
                    )  # Exclude auth methods
                ):
                    # Create a wrapped version that preserves the method binding
                    async def retry_wrapper(*args, **kwargs):
                        return await self._toast_client._call_with_retry(
                            attr, *args, **kwargs
                        )

                    # Preserve the method name for better debugging and IDE discovery
                    retry_wrapper.__name__ = attr.__name__
                    retry_wrapper.__qualname__ = attr.__qualname__

                    return retry_wrapper

                return attr

        return RetryWrappedApi(self._api_client, self)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the underlying API client."""
        await self._api_client.close()

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token."""
        return self._token

    @property
    def token_expires_at(self) -> Optional[float]:
        """Get the token expiration timestamp."""
        return self._token_expires_at

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self._token or not self._token_expires_at:
            return False
        return time.time() < self._token_expires_at

    async def authenticate(self) -> str:
        """
        Authenticate with the Toast API and get a token.

        Returns:
            The authentication token

        Raises:
            Exception: If authentication fails
        """
        try:
            # Create authentication request
            auth_request = AuthenticationRequest(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_access_type="TOAST_MACHINE_CLIENT",
            )

            # Request authentication token
            response = await self.auth.authentication_login_post(auth_request)

            # Extract the token from the response
            if response.token and response.token.access_token:
                self._token = response.token.access_token
            else:
                raise Exception("No authentication token received from the API")

            # Set token expiration (default to 1 hour if not provided)
            if response.token and response.token.expires_in:
                self._token_expires_at = time.time() + response.token.expires_in
            else:
                raise Exception("No token expiration received from the API")

            # Update the API client configuration with the token
            self._config.access_token = self._token

            return self._token

        except Exception as e:
            raise Exception(f"Authentication failed: {e}")

    async def _call_with_retry(self, api_method, *args, **kwargs):
        """
        Call an API method with automatic authentication and retry logic.

        Args:
            api_method: The async API method to call
            *args: Arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            The API response
        """
        # Ensure we're authenticated
        if not self.is_token_valid():
            await self.authenticate()
            if self._token_refresh_callback:
                await self._token_refresh_callback(self._token, self._token_expires_at)

        # Apply retry logic
        last_exception = None
        delay = self.retry_config.base_delay

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return await api_method(*args, **kwargs)
            except self.retry_config.retry_on_exceptions as e:
                last_exception = e

                # Check if we should retry based on custom condition
                if (
                    self.retry_config.retry_condition
                    and not self.retry_config.retry_condition(e)
                ):
                    raise e

                # If this was the last attempt, raise the exception
                if attempt == self.retry_config.max_retries:
                    break

                # Wait before retrying
                await asyncio.sleep(delay)
                delay = min(
                    delay * self.retry_config.backoff_factor,
                    self.retry_config.max_delay,
                )

        # If we get here, all retries failed
        raise last_exception
