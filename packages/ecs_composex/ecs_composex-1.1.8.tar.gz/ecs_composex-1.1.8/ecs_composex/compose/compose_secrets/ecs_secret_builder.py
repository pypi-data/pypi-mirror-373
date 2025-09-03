#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2025 John Mille <john@compose-x.io>

"""
ECS secret builder for creating ECS-specific secret objects
"""

from typing import Any, Dict, List

from troposphere import AWS_ACCOUNT_ID, AWS_PARTITION, AWS_REGION, FindInMap, Sub
from troposphere.ecs import Secret as EcsSecret

from ecs_composex.common.logging import LOG


class EcsSecretBuilder:
    """
    Builds ECS Secret objects from secret configurations.
    """

    def __init__(self, secret_name: str, logical_name: str):
        """
        Initialize the ECS secret builder.

        :param str secret_name: The original secret name
        :param str logical_name: The logical name for CloudFormation
        """
        self.secret_name = secret_name
        self.logical_name = logical_name
        self.map_name = "SecretsMapping"
        self.map_arn_name = "Arn"
        self.map_name_name = "Name"

    def build_secret(self, secret_var_name: str, json_key: str, arn: Any) -> EcsSecret:
        """
        Build an ECS Secret object for a specific JSON key.

        :param str secret_var_name: The environment variable name for the secret
        :param str json_key: The JSON key within the secret
        :param arn: The secret ARN (can be str, Sub, or FindInMap)
        :return: ECS Secret object
        :rtype: EcsSecret
        :raises TypeError: If ARN type is not supported
        """
        if isinstance(arn, str):
            return EcsSecret(Name=secret_var_name, ValueFrom=f"{arn}:{json_key}::")
        elif isinstance(arn, Sub):
            return EcsSecret(
                Name=secret_var_name,
                ValueFrom=Sub(
                    f"arn:${{{AWS_PARTITION}}}:secretsmanager:${{{AWS_REGION}}}:${{{AWS_ACCOUNT_ID}}}:"
                    f"secret:${{SecretName}}:{json_key}::",
                    SecretName=FindInMap(
                        self.map_name,
                        self.logical_name,
                        self.map_name_name,
                    ),
                ),
            )
        elif isinstance(arn, FindInMap):
            return EcsSecret(
                Name=secret_var_name,
                ValueFrom=Sub(
                    f"${{SecretArn}}:{json_key}::",
                    SecretArn=FindInMap(
                        self.map_name,
                        self.logical_name,
                        self.map_arn_name,
                    ),
                ),
            )
        else:
            raise TypeError(
                f"secrets.{self.secret_name} - ARN is {type(arn)}, "
                f"must be one of: {str}, {Sub}, {FindInMap}"
            )

    def build_simple_secret(self, arn: Any) -> EcsSecret:
        """
        Build a simple ECS Secret object without JSON keys.

        :param arn: The secret ARN (can be str, Sub, or FindInMap)
        :return: ECS Secret object
        :rtype: EcsSecret
        """
        return EcsSecret(Name=self.secret_name, ValueFrom=arn)

    def build_secrets_from_json_keys(
        self, json_keys: List[Dict], arn: Any
    ) -> List[EcsSecret]:
        """
        Build multiple ECS Secret objects from JSON keys configuration.

        :param List[Dict] json_keys: List of JSON key configurations
        :param arn: The secret ARN
        :return: List of ECS Secret objects
        :rtype: List[EcsSecret]
        """
        secrets_to_map = {}

        for secret_json_key in json_keys:
            secret_key = secret_json_key["SecretKey"]
            secret_var_name = self._get_env_var_name_from_json_key(secret_json_key)

            if secret_var_name not in secrets_to_map:
                secrets_to_map[secret_var_name] = self.build_secret(
                    secret_var_name, secret_key, arn
                )
            else:
                LOG.warning(
                    f"secrets.{self.secret_name} - Secret VarName {secret_var_name} "
                    "already defined. Overriding value"
                )
                secrets_to_map[secret_var_name] = self.build_secret(
                    secret_var_name, secret_key, arn
                )

        return list(secrets_to_map.values())

    def _get_env_var_name_from_json_key(self, secret_json_key: Dict) -> str:
        """
        Get environment variable name from JSON key configuration.

        :param Dict secret_json_key: JSON key configuration
        :return: Environment variable name
        :rtype: str
        """
        from .helpers import define_env_var_name

        return define_env_var_name(secret_json_key)
