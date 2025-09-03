#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2025 John Mille <john@compose-x.io>

"""
JSON secret processor for handling JSON keys in secrets
"""

import json
import re
from copy import deepcopy
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from compose_x_common.compose_x_common import keyisset

from ecs_composex.common.logging import LOG

from .ecs_secret_builder import EcsSecretBuilder


class JsonSecretProcessor:
    """
    Processes JSON keys within secrets to create multiple ECS secret entries.
    """

    def __init__(self, secret_name: str, logical_name: str, definition: dict):
        """
        Initialize the JSON secret processor.

        :param str secret_name: The original secret name
        :param str logical_name: The logical name for CloudFormation
        :param dict definition: The secret definition
        """
        self.secret_name = secret_name
        self.logical_name = logical_name
        self.definition = definition
        self.x_key = "x-secrets"
        self.json_keys_key = "JsonKeys"
        self.auto_import_key = "AutoImportJsonKeys"
        self.builder = EcsSecretBuilder(secret_name, logical_name)

    def has_json_keys(self) -> bool:
        """
        Check if the secret has JSON keys configuration.

        :return: True if JSON keys exist
        :rtype: bool
        """
        x_config = self.definition.get(self.x_key, {})
        return keyisset(self.json_keys_key, x_config)

    def get_json_keys(self) -> List[dict]:
        """
        Get the filtered JSON keys configuration, removing duplicates.

        :return: List of unique JSON key configurations
        :rtype: List[dict]
        """
        if not self.has_json_keys():
            return []

        x_config = self.definition[self.x_key]
        unfiltered_secrets = x_config[self.json_keys_key]

        # Remove duplicates while preserving order
        filtered_secrets = [
            dict(y) for y in {tuple(x.items()) for x in unfiltered_secrets}
        ]
        return filtered_secrets

    def process_json_keys(self, arn: Any, existing_secrets: List[Any]) -> List[Any]:
        """
        Process JSON keys and create ECS secret objects.

        :param arn: The secret ARN
        :param List[Any] existing_secrets: Existing ECS secrets to fall back to
        :return: List of ECS Secret objects
        :rtype: List[Any]
        """
        if not self.has_json_keys():
            return existing_secrets

        json_keys = self.get_json_keys()
        if not json_keys:
            LOG.warning(
                f"secrets.{self.secret_name} - JSON keys configuration is empty"
            )
            return existing_secrets

        try:
            ecs_secrets = self.builder.build_secrets_from_json_keys(json_keys, arn)
            if not ecs_secrets:
                LOG.warning(
                    f"secrets.{self.secret_name} - No ECS secrets created from JSON keys, "
                    "falling back to existing secrets"
                )
                return existing_secrets
            return ecs_secrets
        except Exception as e:
            LOG.error(
                f"secrets.{self.secret_name} - Error processing JSON keys: {str(e)}"
            )
            return existing_secrets

    def validate_json_keys(self) -> bool:
        """
        Validate JSON keys configuration.

        :return: True if valid, False otherwise
        :rtype: bool
        """
        if not self.has_json_keys():
            return True

        json_keys = self.get_json_keys()
        for i, json_key in enumerate(json_keys):
            if not isinstance(json_key, dict):
                LOG.error(
                    f"secrets.{self.secret_name} - JSON key at index {i} is not a dictionary"
                )
                return False

            if not keyisset("SecretKey", json_key):
                LOG.error(
                    f"secrets.{self.secret_name} - JSON key at index {i} missing required 'SecretKey'"
                )
                return False

            if not isinstance(json_key["SecretKey"], str):
                LOG.error(
                    f"secrets.{self.secret_name} - JSON key at index {i} 'SecretKey' must be a string"
                )
                return False

        return True

    def get_unique_var_names(self) -> List[str]:
        """
        Get list of unique environment variable names from JSON keys.

        :return: List of unique variable names
        :rtype: List[str]
        """
        if not self.has_json_keys():
            return []

        json_keys = self.get_json_keys()
        var_names = []

        for json_key in json_keys:
            var_name = self.builder._get_env_var_name_from_json_key(json_key)
            if var_name not in var_names:
                var_names.append(var_name)

        return var_names

    def has_auto_import(self) -> bool:
        """
        Check if the secret has AutoImportJsonKeys configuration.

        :return: True if auto import is enabled
        :rtype: bool
        """
        x_config = self.definition.get(self.x_key, {})
        return keyisset(self.auto_import_key, x_config)

    def should_auto_import(self) -> bool:
        """
        Check if auto import should be performed.
        Auto import is skipped if manual JsonKeys already exist.

        :return: True if auto import should be performed
        :rtype: bool
        """
        return self.has_auto_import() and not self.has_json_keys()

    def get_auto_import_config(self) -> Dict[str, Any]:
        """
        Get the auto import configuration.

        :return: Auto import configuration
        :rtype: Dict[str, Any]
        """
        if not self.has_auto_import():
            return {}

        x_config = self.definition[self.x_key]
        auto_import_config = x_config[self.auto_import_key]

        if isinstance(auto_import_config, bool):
            return {"enabled": auto_import_config}
        elif isinstance(auto_import_config, dict):
            return auto_import_config
        else:
            LOG.warning(
                f"secrets.{self.secret_name} - Invalid AutoImportJsonKeys configuration"
            )
            return {}

    def auto_import_json_keys(self, session: Any = None) -> None:
        """
        Automatically import JSON keys from AWS Secrets Manager.

        :param session: AWS session to use for API calls
        """
        if not self.should_auto_import():
            return

        try:
            auto_import_config = self.get_auto_import_config()
            if not auto_import_config.get("enabled", True):
                return

            # Get the secret name/ARN
            x_config = self.definition.get(self.x_key, {})
            secret_identifier = None

            if keyisset("Name", x_config):
                secret_identifier = x_config["Name"]
            elif keyisset("Lookup", x_config):
                # For lookup-based secrets, we need to resolve the ARN first
                from ecs_composex.secrets.secrets_aws import lookup_secret_config

                lookup_info = x_config["Lookup"]
                if keyisset("Name", x_config):
                    lookup_info["Name"] = x_config["Name"]

                try:
                    secret_config = lookup_secret_config(
                        self.logical_name, lookup_info, session
                    )
                    secret_identifier = secret_config[self.logical_name]
                except Exception as e:
                    LOG.error(
                        f"secrets.{self.secret_name} - Failed to lookup secret: {str(e)}"
                    )
                    return
            else:
                LOG.error(
                    f"secrets.{self.secret_name} - No Name or Lookup specified for AutoImportJsonKeys"
                )
                return

            # Create AWS client
            client = self._create_secrets_client(session, auto_import_config)
            if not client:
                return

            # Fetch secret value
            secret_data = self._fetch_secret_value(client, secret_identifier)
            if secret_data is None:
                return

            # Parse and create JsonKeys
            json_keys = self._create_json_keys_from_secret(
                secret_data, auto_import_config
            )

            # Add JsonKeys to definition even if empty to indicate auto import was attempted
            if self.x_key not in self.definition:
                self.definition[self.x_key] = {}
            self.definition[self.x_key][self.json_keys_key] = json_keys

            LOG.info(
                f"secrets.{self.secret_name} - Auto-imported {len(json_keys)} JSON keys"
            )

        except Exception as e:
            LOG.error(
                f"secrets.{self.secret_name} - Error during auto import: {str(e)}"
            )

    def _create_secrets_client(
        self, session: Any, config: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Create AWS Secrets Manager client with optional role assumption.

        :param session: AWS session
        :param Dict[str, Any] config: Auto import configuration
        :return: Boto3 Secrets Manager client or None
        :rtype: Optional[Any]
        """
        try:
            if keyisset("RoleArn", config):
                # Assume role for cross-account access
                role_arn = config["RoleArn"]
                LOG.info(
                    f"secrets.{self.secret_name} - Assuming role {role_arn} for secret access"
                )

                if session:
                    sts_client = session.client("sts")
                else:
                    sts_client = boto3.client("sts")

                assumed_role = sts_client.assume_role(
                    RoleArn=role_arn,
                    RoleSessionName=f"ecs-composex-secret-import-{self.logical_name}",
                )

                credentials = assumed_role["Credentials"]
                from boto3 import Session

                assumed_session = Session(
                    aws_access_key_id=credentials["AccessKeyId"],
                    aws_secret_access_key=credentials["SecretAccessKey"],
                    aws_session_token=credentials["SessionToken"],
                )
                return assumed_session.client("secretsmanager")
            else:
                # Use provided session or default credentials
                if session:
                    return session.client("secretsmanager")
                else:
                    return boto3.client("secretsmanager")

        except Exception as e:
            LOG.error(
                f"secrets.{self.secret_name} - Failed to create secrets client: {str(e)}"
            )
            return None

    def _fetch_secret_value(
        self, client: Any, secret_identifier: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch secret value from AWS Secrets Manager.

        :param client: Boto3 Secrets Manager client
        :param str secret_identifier: Secret name or ARN
        :return: Secret data or None
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            response = client.get_secret_value(SecretId=secret_identifier)
            secret_string = response.get("SecretString")

            if not secret_string:
                LOG.error(
                    f"secrets.{self.secret_name} - Secret {secret_identifier} has no SecretString"
                )
                return None

            secret_data = json.loads(secret_string)

            if not isinstance(secret_data, dict):
                LOG.error(
                    f"secrets.{self.secret_name} - Secret {secret_identifier} does not contain a JSON object"
                )
                return None

            return secret_data

        except ClientError as e:
            LOG.error(
                f"secrets.{self.secret_name} - AWS error fetching secret {secret_identifier}: {str(e)}"
            )
            return None
        except json.JSONDecodeError as e:
            LOG.error(
                f"secrets.{self.secret_name} - Invalid JSON in secret {secret_identifier}: {str(e)}"
            )
            return None
        except Exception as e:
            LOG.error(
                f"secrets.{self.secret_name} - Unexpected error fetching secret {secret_identifier}: {str(e)}"
            )
            return None

    def _create_json_keys_from_secret(
        self, secret_data: Dict[str, Any], config: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Create JsonKeys configuration from secret data.

        :param Dict[str, Any] secret_data: Secret data from AWS
        :param Dict[str, Any] config: Auto import configuration
        :return: List of JsonKeys configurations
        :rtype: List[Dict[str, str]]
        """
        json_keys = []
        transform = config.get("Transform")

        for key in secret_data.keys():
            json_key_config = {"SecretKey": key}

            if transform:
                json_key_config["Transform"] = transform

            json_keys.append(json_key_config)

        # Always return JsonKeys list, even if empty - this allows tests to verify
        # that auto import was attempted even with empty secrets
        return json_keys
