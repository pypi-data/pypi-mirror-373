#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2025 John Mille <john@compose-x.io>

"""
Secret name resolver for handling import and lookup operations
"""

from typing import Any, Dict

from compose_x_common.aws.kms import KMS_KEY_ARN_RE
from compose_x_common.aws.secrets_manager import get_secret_name_from_arn
from compose_x_common.compose_x_common import keyisset
from troposphere import AWS_ACCOUNT_ID, AWS_PARTITION, AWS_REGION, FindInMap, Sub

from ecs_composex.common.logging import LOG
from ecs_composex.secrets.secrets_aws import lookup_secret_config


class SecretNameResolver:
    """
    Handles resolving secret names from either import or lookup configurations.
    """

    def __init__(self, secret_name: str, logical_name: str, definition: dict):
        """
        Initialize the name resolver.

        :param str secret_name: The original secret name
        :param str logical_name: The logical name for CloudFormation
        :param dict definition: The secret definition
        """
        self.secret_name = secret_name
        self.logical_name = logical_name
        self.definition = definition
        self.x_key = "x-secrets"
        self.map_name = "SecretsMapping"
        self.map_arn_name = "Arn"
        self.map_name_name = "Name"
        self.map_kms_name = "KmsKeyId"

    def resolve_from_import(self) -> Dict[str, Any]:
        """
        Resolve secret names and ARNs from import configuration.

        :return: Dictionary containing resolved names, ARNs, and mapping
        :rtype: Dict[str, Any]
        :raises KeyError: If required Name field is missing
        """
        x_config = self.definition.get(self.x_key, {})

        if not keyisset(self.map_name_name, x_config):
            raise KeyError(
                f"Missing {self.map_name_name} when doing non-lookup import for {self.secret_name}"
            )

        name_input = x_config[self.map_name_name]
        result = {
            "aws_name": None,
            "arn": None,
            "iam_arn": None,
            "mapping": {},
            "kms_key_arn": None,
        }

        if name_input.startswith("arn:"):
            # Handle ARN input
            result["aws_name"] = get_secret_name_from_arn(name_input)
            result["arn"] = name_input
            result["iam_arn"] = name_input
            result["mapping"] = {
                self.map_arn_name: name_input,
                self.map_name_name: result["aws_name"],
            }
        else:
            # Handle name input
            result["aws_name"] = name_input
            result["mapping"] = {self.map_name_name: result["aws_name"]}

            # Create Sub expressions for ARNs
            result["arn"] = Sub(
                f"arn:${{{AWS_PARTITION}}}:secretsmanager:${{{AWS_REGION}}}:${{{AWS_ACCOUNT_ID}}}:"
                "secret:${SecretName}",
                SecretName=FindInMap(
                    self.map_name, self.logical_name, self.map_name_name
                ),
            )
            result["iam_arn"] = Sub(
                f"arn:${{{AWS_PARTITION}}}:secretsmanager:${{{AWS_REGION}}}:${{{AWS_ACCOUNT_ID}}}:"
                "secret:${SecretName}*",
                SecretName=FindInMap(
                    self.map_name, self.logical_name, self.map_name_name
                ),
            )

        # Handle KMS key configuration
        kms_key_arn = self._resolve_kms_key(x_config, result["mapping"])
        if kms_key_arn:
            result["kms_key_arn"] = kms_key_arn

        return result

    def resolve_from_lookup(self, session: Any) -> Dict[str, Any]:
        """
        Resolve secret names and ARNs from lookup configuration.

        :param session: AWS session for lookup operations
        :return: Dictionary containing resolved names, ARNs, and mapping
        :rtype: Dict[str, Any]
        """
        x_config = self.definition[self.x_key]
        lookup_info = x_config["Lookup"]

        # Add Name to lookup if specified in x-secrets
        if keyisset("Name", x_config):
            lookup_info["Name"] = x_config["Name"]

        secret_config = lookup_secret_config(self.logical_name, lookup_info, session)

        result = {
            "aws_name": get_secret_name_from_arn(secret_config[self.logical_name]),
            "arn": FindInMap(self.map_name, self.logical_name, self.map_arn_name),
            "iam_arn": secret_config[self.logical_name],
            "mapping": {
                self.map_arn_name: secret_config[self.logical_name],
                self.map_name_name: secret_config[self.map_name_name],
            },
            "kms_key": None,
            "kms_key_arn": None,
        }

        # Handle KMS key from lookup results
        if keyisset("KmsKeyId", secret_config):
            if not secret_config["KmsKeyId"].startswith("alias"):
                result["kms_key"] = secret_config["KmsKeyId"]
                result["mapping"][self.map_kms_name] = result["kms_key"]
                result["kms_key_arn"] = FindInMap(
                    self.map_name, self.logical_name, self.map_kms_name
                )
            else:
                LOG.warning(
                    f"secrets.{self.secret_name} - The KMS Key retrieved is a KMS Key Alias, not importing."
                )

        return result

    def _resolve_kms_key(self, x_config: dict, mapping: dict) -> Any:
        """
        Resolve KMS key configuration from import settings.

        :param dict x_config: The x-secrets configuration
        :param dict mapping: The mapping dictionary to update
        :return: KMS key ARN reference or None
        :rtype: Any
        """
        if not keyisset(self.map_kms_name, x_config):
            return None

        kms_key_input = x_config[self.map_kms_name]

        if not kms_key_input.startswith("arn:") or not KMS_KEY_ARN_RE.match(
            kms_key_input
        ):
            LOG.error(
                f"secrets.{self.secret_name} - When specifying {self.map_kms_name} "
                "you must specify the full ARN"
            )
            return None

        mapping[self.map_kms_name] = kms_key_input
        return FindInMap(self.map_name, self.logical_name, self.map_kms_name)
