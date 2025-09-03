import json
import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any
from typing import ClassVar
from typing import Literal
from typing import Optional

import yaml
from pydantic import BaseModel
from pydantic import Field

logger = logging.getLogger(__name__)


class TransactionData(BaseModel):
    transaction_name: str
    input_params: dict[str, Any] = Field(default_factory=dict)
    expected_response: Any = None


class ApiCheckConfig(BaseModel):
    # Class variable to store the config file path
    _config_file: ClassVar[Optional[Path]] = None

    items_per_list: tuple[int, int, int] = (5, 5, 5)
    headers: dict[str, str] = Field(default_factory=dict)
    auth_headers: dict[str, str] = Field(default_factory=dict)
    request_timeout: int = 600
    extend_output: bool = True

    # Authentication
    email: Optional[str] = None
    password: Optional[str] = None

    @property
    def token(self) -> Optional[str]:
        """
        Get the token from auth_headers.

        Returns:
            Optional[str]: The token or None if not set
        """
        if not self.auth_headers or 'Authorization' not in self.auth_headers:
            return None

        return self.auth_headers['Authorization']

    @token.setter
    def token(self, value: Optional[str]) -> None:
        """
        Set the token in auth_headers.

        Args:
            value: The token value
        """
        if value is None:
            if 'Authorization' in self.auth_headers:
                del self.auth_headers['Authorization']
        else:
            self.auth_headers['Authorization'] = value

    @property
    def token_expiry(self) -> Optional[int]:
        """
        Get the token expiry from the token.

        Returns:
            Optional[int]: The token expiry timestamp, or None if not available
        """
        if not self.token:
            return None

        try:
            import jwt

            decoded = jwt.decode(self.token, options={'verify_signature': False})
            return decoded.get('exp')
        except Exception as e:
            logger.warning(f'Failed to decode token: {e}')
            return None

    @property
    def env_authorization(self) -> Optional[str]:
        """Get authorization token from environment variable."""
        return os.environ.get('AMSDAL_API_CHECK_AUTHORIZATION')

    @property
    def env_email(self) -> Optional[str]:
        """Get email from environment variable."""
        return os.environ.get('AMSDAL_API_CHECK_EMAIL')

    @property
    def env_password(self) -> Optional[str]:
        """Get password from environment variable."""
        return os.environ.get('AMSDAL_API_CHECK_PASSWORD')

    @classmethod
    def load_from_file(cls, config_file: str | Path) -> 'ApiCheckConfig':
        """
        Load configuration from a file.

        Args:
            config_file: Path to the configuration file (YAML or JSON)

        Returns:
            ApiCheckConfig: The loaded configuration
        """
        config_path = Path(config_file)

        try:
            with open(config_path) as f:
                # Determine file format based on extension
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_raw = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_raw = json.load(f)
                else:
                    # Default to YAML if extension is not recognized
                    config_raw = yaml.safe_load(f)

            # Create config instance
            config = cls(**config_raw)
            # Store the config file path
            cls._config_file = config_path

            logger.info(f'Configuration loaded from {config_path}')
            return config
        except Exception as e:
            logger.error(f'Failed to load configuration from {config_path}: {e}')
            raise

    def save(self, config_file: Optional[str | Path] = None) -> None:
        """
        Save the current configuration to a file.

        Email and password values provided through environment variables
        (AMSDAL_API_CHECK_EMAIL, AMSDAL_API_CHECK_PASSWORD) will not be saved to the file.
        Only the token and other configuration values will be persisted.

        Args:
            config_file: Path to save the configuration to. If not provided,
                         uses the path from which the config was loaded.
        """
        # Use provided path or fall back to the stored path
        save_path = Path(config_file) if config_file else self.__class__._config_file

        if not save_path:
            logger.warning('No config file specified, cannot save configuration')
            return

        try:
            # Convert config to dict
            config_dict = self.model_dump()

            # Don't save email and password if they were provided through environment variables
            if self.env_email and self.email == self.env_email:
                config_dict.pop('email', None)

            if self.env_password and self.password == self.env_password:
                config_dict.pop('password', None)

            # No need to handle token and token_expiry as they are now properties
            # and not included in the model_dump()

            # Write to file
            with open(save_path, 'w') as f:
                json.dump(config_dict, f, indent=2)

            logger.info(f'Configuration saved to {save_path}')
        except Exception as e:
            logger.error(f'Failed to save configuration: {e}')

    # classes
    exclude_classes: list[str] | Literal['ALL'] = Field(default_factory=list)

    # objects
    exclude_objects_for_classes: list[str] = Field(default_factory=list)
    objects_list_params_options: list[dict[str, Any]] = Field(default_factory=list)
    object_detail_params_options: list[dict[str, Any]] = Field(default_factory=list)
    object_write_operations_enabled: bool = Field(default=False)
    exclude_object_write_operations_for_classes: list[str] = Field(default_factory=list)
    pre_object_create_hook: Callable[[dict[str, Any]], dict[str, Any]] | dict[str, Any] = Field(default_factory=dict)
    pre_object_update_hook: Callable[[dict[str, Any]], dict[str, Any]] | dict[str, Any] = Field(default_factory=dict)

    # transactions
    ignore_transaction_execution_errors: bool = Field(default=True)
    exclude_transactions: list[str] | Literal['ALL'] = Field(default_factory=list)
    exclude_execute_transactions: list[str] | Literal['ALL'] = Field(default_factory=list)
    transactions_data: list[TransactionData] = Field(default_factory=list)
