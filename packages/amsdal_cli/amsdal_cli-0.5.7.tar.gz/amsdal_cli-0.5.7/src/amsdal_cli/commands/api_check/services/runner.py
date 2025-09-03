import logging
import time
from collections.abc import Iterator
from typing import Any

import httpx
import jwt
import typer
from rich import print as rprint
from starlette import status

from amsdal_cli.commands.api_check.config import ApiCheckConfig
from amsdal_cli.commands.api_check.data_classes import ClassItem
from amsdal_cli.commands.api_check.data_classes import Transaction
from amsdal_cli.commands.api_check.operation_log import OperationLog
from amsdal_cli.commands.api_check.services.data_factory import DataFactory

logger = logging.getLogger(__name__)


class ApiRunner:
    def __init__(self, base_url: str, config: ApiCheckConfig) -> None:
        self.base_url = base_url
        self.config = config
        self.logs: list[OperationLog] = []

    def authenticate(self) -> None:
        """
        Authenticate using login credentials and store the token in the config.
        Uses credentials from environment variables if available, otherwise from config.
        """
        # Get email and password from environment variables or config
        email = self.config.env_email or self.config.email
        password = self.config.env_password or self.config.password

        if not email or not password:
            return

        rprint(f'[blue]Authenticating with login credentials on {self.base_url}[/blue]')
        payload = {'email': email, 'password': password}

        try:
            response = httpx.post(
                f"{self.base_url.rstrip('/')}/objects/",
                params={'class_name': 'LoginSession', 'load_references': 'false'},
                json=payload,
                timeout=self.config.request_timeout,
                headers=self.config.headers,
            )
            response.raise_for_status()
            data = response.json()

            if 'token' in data:
                self.config.token = data['token']
                # Token expiry is automatically extracted from the token
                try:
                    # Decode token just to verify it's valid
                    jwt.decode(data['token'], options={'verify_signature': False})
                    # Use the token_expiry property to get the expiry time
                    rprint(
                        f'[green]Authentication successful. '
                        f'Token expires at: {time.ctime(self.config.token_expiry)}[/green]'
                    )
                    # Save the token to the config file using the config's save method
                    self.config.save()
                except Exception as e:
                    logger.warning(f'Failed to decode token: {e}')
            else:
                rprint('[red]Authentication failed: No token in response[/red]')
                # Exit with error code if authentication failed
                raise typer.Exit(code=1)
        except httpx.HTTPStatusError as e:
            rprint(f'[red]Authentication failed: HTTP error {e.response.status_code} - {e}[/red]')
            # Exit with error code for HTTP errors
            raise typer.Exit(code=1) from e
        except Exception as e:
            rprint(f'[red]Authentication failed: {e}[/red]')
            # Exit with error code for other exceptions
            raise typer.Exit(code=1) from e

    def is_token_valid(self) -> bool:
        """
        Check if the stored token is valid (not expired).
        """
        if not self.config.token or not self.config.token_expiry:
            return False

        current_time = int(time.time())
        # Add a 30-second buffer to ensure we don't use a token that's about to expire
        return current_time < (self.config.token_expiry - 30)

    def run(self) -> list[OperationLog]:
        self.logs.clear()
        rprint('[blue]Running API checks[/blue]', end='\n' if self.config.extend_output else '')

        # Check if token is valid
        if not self.is_token_valid():
            # Get email and password from environment variables or config
            email = self.config.env_email or self.config.email
            password = self.config.env_password or self.config.password

            # If credentials are available, authenticate
            if email and password:
                self.authenticate()
            # If token is invalid and no credentials are available, but we need authentication
            elif self.config.env_authorization or self.config.auth_headers:
                # Only raise error if we were trying to use authentication
                rprint(
                    '[red]Error: Token is invalid and no credentials (email/password) '
                    'are available for authentication.[/red]'
                )
                rprint(
                    '[red]Please provide valid credentials via environment variables '
                    '(AMSDAL_API_CHECK_EMAIL, AMSDAL_API_CHECK_PASSWORD) or config file.[/red]'
                )
                import typer

                raise typer.Exit(code=1)

        classes = list(self.get_class_list(with_auth=False))
        _classes = list(self.get_class_list(with_auth=True))

        if _classes:
            classes = _classes

        cls: ClassItem

        for cls in self._iterate_items_per_list(classes):
            self.get_class_detail(cls, with_auth=False)
            self.get_class_detail(cls, with_auth=True)

            objects = list(self.get_object_list(cls))

            for obj in self._iterate_items_per_list(objects):
                self.get_object_detail(obj)
                self.get_object_detail(obj, with_auth=True)

            if self.config.object_write_operations_enabled:
                self.check_write_operations(cls)
                self.check_write_operations(cls, with_auth=True)

        # Get transactions without auth
        transactions = self.get_transaction_list()

        # Get transactions with auth if auth headers are available
        if self.config.auth_headers:
            transactions_with_auth = self.get_transaction_list(with_auth=True)
            # Combine the lists, avoiding duplicates
            for transaction in transactions_with_auth:
                if transaction not in transactions:
                    transactions.append(transaction)

        for transaction in self._iterate_transactions(transactions):
            # Get transaction details without auth
            self.get_transaction_detail(transaction, ignore_status_code=True)
            self.check_transaction_execute(transaction, ignore_status_code=True)

            # Get transaction details with auth if auth headers are available
            if self.config.auth_headers:
                self.get_transaction_detail(transaction, with_auth=True, ignore_status_code=False)
                self.check_transaction_execute(transaction, with_auth=True)

        return self.logs

    def get_class_list(self, *, with_auth: bool = False) -> Iterator[ClassItem]:
        if isinstance(self.config.exclude_classes, str) and self.config.exclude_classes == 'ALL':
            return

        data = self._request('GET', 'classes/', with_auth=with_auth)

        for item in data['rows']:
            cls_item = ClassItem(**item)

            if cls_item.class_name in self.config.exclude_classes:
                continue

            yield cls_item

    def get_class_detail(self, class_item: ClassItem, *, with_auth: bool = False) -> None:
        self._request('GET', f'classes/{class_item.class_name}/', with_auth=with_auth)

    def get_object_list(self, class_item: ClassItem) -> Iterator[dict[str, Any]]:
        if class_item.class_name in self.config.exclude_objects_for_classes:
            return

        if self.config.objects_list_params_options:
            _params_options = self.config.objects_list_params_options
        else:
            _params_options = [
                {
                    'include_metadata': False,
                    'include_subclasses': False,
                    'load_references': False,
                    'all_versions': False,
                    'file_optimized': False,
                    'page_size': 15,
                },
                {
                    'include_metadata': True,
                    'include_subclasses': True,
                    'load_references': False,
                    'file_optimized': True,
                    'page_size': 15,
                },
            ]

        for params in _params_options:
            # without auth
            self._request(
                'GET',
                'objects/',
                params={
                    'class_name': class_item.class_name,
                    **params,
                },
            )

            # with auth
            data = self._request(
                'GET',
                'objects/',
                with_auth=True,
                params={
                    'class_name': class_item.class_name,
                    **params,
                },
            )

        yield from data['rows']

    def get_object_detail(self, object_item: dict[str, Any], *, with_auth: bool = False) -> None:
        if self.config.object_detail_params_options:
            _params_options = self.config.object_detail_params_options
        else:
            _params_options = [
                {
                    'all_versions': False,
                    'include_metadata': False,
                    'file_optimized': False,
                },
                {
                    'all_versions': False,
                    'include_metadata': False,
                    'file_optimized': True,
                },
            ]
        address = object_item.get('_metadata', {}).get('lakehouse_address')

        if not address:
            logger.warning(f'No lakehouse address for object: {object_item}')

        for params in _params_options:
            self._request('GET', f'objects/{address}/', params=params, with_auth=with_auth)

    def check_write_operations(self, class_item: ClassItem, *, with_auth: bool = False) -> None:
        if class_item.class_name in self.config.exclude_object_write_operations_for_classes:
            return

        # Create a sample object for testing
        sample_data = DataFactory.build_data(class_item)

        create_response = self._request('POST', 'objects/', json=sample_data, with_auth=with_auth)

        if create_response.status_code != httpx.codes.OK:
            return

        # Get the address of the created object
        address = create_response.get('_metadata', {}).get('lakehouse_address')

        if not address:
            logger.warning(f'Failed to create object for class: {class_item.class_name}')
            return

        response = self._request('GET', f'objects/{address}/', with_auth=with_auth)

        if response.status_code != httpx.codes.OK:
            return

        data = response['rows'][0]
        update_data = DataFactory.build_update_data(class_item, data)

        response = self._request('PUT', f'objects/{address}/', json=update_data, with_auth=with_auth)

        if response.status_code != httpx.codes.OK:
            return

        self._request('DELETE', f'objects/{address}/', with_auth=with_auth)

    def _iterate_items_per_list(self, items: list[Any]) -> Iterator[Any]:
        if not items:
            return

        start, middle, end = self.config.items_per_list
        total_items = len(items)
        requested_items = start + middle + end

        # If list is shorter than or equal to requested items, yield all
        if total_items <= requested_items:
            yield from items
            return

        # Yield start items
        yield from items[:start]

        # Calculate middle section
        remaining_items = total_items - start - end
        if remaining_items > 0 and middle > 0:
            middle_start = start + (remaining_items - middle) // 2
            middle_end = middle_start + middle
            yield from items[middle_start:middle_end]

        # Yield end items
        if end > 0:
            yield from items[-end:]

    def get_transaction_list(self, *, with_auth: bool = False) -> list[Transaction]:
        """
        Get the list of transactions.

        Args:
            with_auth: Whether to include authentication headers in the request

        Returns:
            A list of Transaction objects
        """
        transactions = []

        data = self._request('GET', 'transactions/', with_auth=with_auth)

        # Only process data if we got a valid response with rows
        if isinstance(data, dict) and 'rows' in data:
            for item in data['rows']:
                transactions.append(Transaction(**item))

        return transactions

    def _iterate_transactions(self, transactions: list[Transaction]) -> Iterator[Transaction]:
        if not transactions:
            return

        if isinstance(self.config.exclude_transactions, str):
            if self.config.exclude_transactions == 'ALL':
                return
            else:
                msg = 'Unknown exclude_transactions value. Expected "ALL" or list of transaction names.'
                raise ValueError(msg)

        for transaction in transactions:
            if transaction.title in self.config.exclude_transactions:
                continue

            yield transaction

    def get_transaction_detail(
        self,
        transaction: Transaction,
        *,
        with_auth: bool = False,
        ignore_status_code: bool = False,
    ) -> None:
        """
        Get details for a transaction.

        Args:
            transaction: The transaction to get details for
            with_auth: Whether to include authentication headers in the request
            ignore_status_code: Whether to ignore status codes other than 200 and 201 when checking
        """
        # Make a request to get transaction details
        self._request(
            'GET',
            f'transactions/{transaction.title}/',
            with_auth=with_auth,
            ignore_status_code=ignore_status_code,
        )

    def check_transaction_execute(
        self,
        transaction: Transaction,
        *,
        with_auth: bool = False,
        ignore_status_code: bool = False,
    ) -> None:
        """
        Execute a transaction.

        Args:
            transaction: The transaction to execute
            with_auth: Whether to include authentication headers in the request
            ignore_status_code: Whether to ignore status codes other than 200 and 201 when checking
            transaction execution.
        """
        # Check if transaction should be excluded
        if isinstance(self.config.exclude_execute_transactions, str):
            if self.config.exclude_execute_transactions == 'ALL':
                return
            else:
                msg = 'Unknown exclude_execute_transactions value. Expected "ALL" or list of transaction names.'
                raise ValueError(msg)

        if transaction.title in self.config.exclude_execute_transactions:
            return

        # Find transaction data in config or generate it
        transaction_data_list = [td for td in self.config.transactions_data if td.transaction_name == transaction.title]

        # If no data found in config, generate a set of parameters using DataFactory
        if not transaction_data_list:
            # Generate parameters based on transaction properties
            params = {}
            for key, prop in transaction.properties.items():
                # Use DataFactory to generate appropriate values based on property type
                if isinstance(prop, dict) and 'type' in prop:
                    params[key] = DataFactory.generate_value_for_type(prop['type'], prop)
                else:
                    # If type is not specified, use a simple string
                    params[key] = f'test_{key}'

            # Execute the transaction with generated parameters
            self._request(
                'POST',
                f'transactions/{transaction.title}/',
                json=params,
                with_auth=with_auth,
                ignore_status_code=ignore_status_code,
            )
        else:
            # Execute the transaction with each set of parameters from config
            for td in transaction_data_list:
                self._request(
                    'POST',
                    f'transactions/{transaction.title}/',
                    json=td.input_params,
                    with_auth=with_auth,
                    ignore_status_code=self.config.ignore_transaction_execution_errors,
                )

    def _request(
        self,
        method: str,
        path: str,
        *,
        with_auth: bool = True,
        ignore_status_code: bool = False,
        **kwargs: Any,
    ) -> Any:
        base_url = self.base_url.rstrip('/')
        path = path.lstrip('/')
        url = f'{base_url}/{path}'
        params: dict[str, Any] = {
            'timeout': self.config.request_timeout,
        }
        params.update(kwargs)
        _headers: dict[str, Any] = {**self.config.headers}

        if with_auth:
            # Priority order for authentication:
            # 1. Environment variable
            # 2. Token from login
            # 3. Auth headers from config

            if self.config.env_authorization:
                # Use token from environment variable
                _headers['Authorization'] = self.config.env_authorization
            elif self.config.token:
                # Use token from login
                _headers['Authorization'] = self.config.token
            else:
                # Fall back to auth_headers from config
                _headers.update(self.config.auth_headers)

        _headers.update(kwargs.get('headers', {}))
        params['headers'] = _headers
        response = httpx.request(method, url, **params)

        if not ignore_status_code:
            response.raise_for_status()

        log = OperationLog.from_response(
            response,
            auth_headers=self.config.auth_headers,
            ignore_class_version=True,
            ignore_object_version=True,
        )
        self.logs.append(log)

        if self.config.extend_output:
            color = 'green' if response.status_code < status.HTTP_400_BAD_REQUEST else 'yellow'
            color = color if response.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR else 'red'
            rprint(f'[{color}]{response.status_code} {method} {path}[/{color}]')
        else:
            rprint('.', end='')

        try:
            data = response.json()
        except Exception:
            data = response.text

        return data
