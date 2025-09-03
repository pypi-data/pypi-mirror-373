#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2025 John Mille <john@compose-x.io>

"""
Refactored ComposeSecret class using smaller, focused components
"""

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from troposphere.ecs import Secret as EcsSecret

from ecs_composex.common.logging import LOG

if TYPE_CHECKING:
    from ecs_composex.common.settings import ComposeXSettings

from .base_secret import BaseSecret
from .ecs_secret_builder import EcsSecretBuilder
from .json_processor import JsonSecretProcessor
from .name_resolver import SecretNameResolver


class ComposeSecret(BaseSecret):
    """
    Main class to represent a Compose secret, orchestrating smaller components.
    """

    def __init__(self, name: str, definition: dict, settings: "ComposeXSettings"):
        """
        Initialize ComposeSecret using component-based architecture.

        :param str name: The secret name
        :param dict definition: The secret definition from compose file
        :param ComposeXSettings settings: The compose settings
        """
        super().__init__(name, definition, settings)

        # Initialize components
        self.name_resolver = SecretNameResolver(
            self.name, self.logical_name, self.definition
        )
        self.ecs_builder = EcsSecretBuilder(self.name, self.logical_name)
        self.json_processor = JsonSecretProcessor(
            self.name, self.logical_name, self.definition
        )

        # Process the secret
        self._auto_import_json_keys()
        self._resolve_names()
        self._define_links()
        self._process_json_keys()
        self._update_settings()

    def _resolve_names(self) -> None:
        """
        Resolve secret names and ARNs using the name resolver.
        """
        try:
            if self.has_lookup_config():
                result = self.name_resolver.resolve_from_lookup(self.settings.session)
                self.kms_key = result.get("kms_key")
            else:
                result = self.name_resolver.resolve_from_import()

            # Update properties from resolver result
            self.aws_name = result["aws_name"]
            self.arn = result["arn"]
            self.iam_arn = result["iam_arn"]
            self.mapping = result["mapping"]
            self.kms_key_arn = result.get("kms_key_arn")

            # Create initial ECS secret if no JSON keys
            if not self.has_json_keys():
                self.ecs_secret = [self.ecs_builder.build_simple_secret(self.arn)]

        except Exception as e:
            LOG.error(f"secrets.{self.name} - Error resolving names: {str(e)}")
            raise

    def _define_links(self) -> None:
        """
        Define which IAM roles to assign the secrets access policy to.
        """
        self.links = self.get_links_config()

    def _process_json_keys(self) -> None:
        """
        Process JSON keys if they exist and create corresponding ECS secrets.
        """
        if not self.has_json_keys():
            return

        # Validate JSON keys configuration
        if not self.json_processor.validate_json_keys():
            LOG.error(f"secrets.{self.name} - Invalid JSON keys configuration")
            return

        # Store existing secrets as fallback
        old_secrets = deepcopy(self.ecs_secret)

        # Process JSON keys
        self.ecs_secret = self.json_processor.process_json_keys(self.arn, old_secrets)

    def _update_settings(self) -> None:
        """
        Update the settings with the secret mapping.
        """
        self.update_settings_mappings()

    def _auto_import_json_keys(self) -> None:
        """
        Automatically import JSON keys from AWS Secrets Manager if configured.
        """
        try:
            # Update the processor's definition to match ours, then call auto import
            self.json_processor.definition = self.definition
            self.json_processor.auto_import_json_keys(self.settings.session)
        except Exception as e:
            LOG.error(f"secrets.{self.name} - Error during auto import: {str(e)}")

    def define_secret(self, secret_name: str, json_key: str) -> EcsSecret:
        """
        Define an ECS secret for backward compatibility.

        :param str secret_name: The secret environment variable name
        :param str json_key: The JSON key within the secret
        :return: ECS Secret object
        :rtype: EcsSecret
        """
        return self.ecs_builder.build_secret(secret_name, json_key, self.arn)

    def add_json_keys(self) -> None:
        """
        Legacy method for backward compatibility - now handled in _process_json_keys.
        """
        LOG.warning(
            f"secrets.{self.name} - add_json_keys() is deprecated, "
            "JSON keys are now processed automatically during initialization"
        )
        self._process_json_keys()

    def define_names_from_import(self) -> None:
        """
        Legacy method for backward compatibility.
        """
        LOG.warning(
            f"secrets.{self.name} - define_names_from_import() is deprecated, "
            "name resolution is now handled automatically"
        )

    def define_names_from_lookup(self, session: Any) -> None:
        """
        Legacy method for backward compatibility.

        :param session: AWS session
        """
        LOG.warning(
            f"secrets.{self.name} - define_names_from_lookup() is deprecated, "
            "name resolution is now handled automatically"
        )

    def define_links(self) -> None:
        """
        Legacy method for backward compatibility.
        """
        LOG.warning(
            f"secrets.{self.name} - define_links() is deprecated, "
            "links are now defined automatically"
        )

    def get_json_key_variables(self) -> list:
        """
        Get list of environment variable names from JSON keys.

        :return: List of variable names
        :rtype: list
        """
        return self.json_processor.get_unique_var_names()

    def validate(self) -> bool:
        """
        Validate the secret configuration.

        :return: True if valid, False otherwise
        :rtype: bool
        """
        try:
            # Validate JSON keys if present
            if not self.json_processor.validate_json_keys():
                return False

            # Validate required properties
            if not self.name or not self.logical_name:
                LOG.error(f"secrets.{self.name} - Missing required name properties")
                return False

            # Validate ARN exists
            if not self.arn:
                LOG.error(f"secrets.{self.name} - Missing ARN")
                return False

            return True

        except Exception as e:
            LOG.error(f"secrets.{self.name} - Validation error: {str(e)}")
            return False
