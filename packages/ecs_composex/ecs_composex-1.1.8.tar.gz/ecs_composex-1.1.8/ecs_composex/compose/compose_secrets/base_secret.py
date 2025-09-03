#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2025 John Mille <john@compose-x.io>

"""
Base secret class with core properties and functionality
"""

import re
from copy import deepcopy
from typing import TYPE_CHECKING, Any, List, Optional

from compose_x_common.compose_x_common import keyisset
from troposphere.ecs import Environment as EcsEnvVar

from ecs_composex.common import NONALPHANUM
from ecs_composex.ecs.ecs_params import EXEC_ROLE_T, TASK_ROLE_T
from ecs_composex.secrets.secrets_params import RES_KEY, XRES_KEY

if TYPE_CHECKING:
    from ecs_composex.common.settings import ComposeXSettings


class BaseSecret:
    """
    Base class for compose secrets with core properties and functionality.
    """

    x_key = XRES_KEY
    main_key = "secrets"
    map_kms_name = "KmsKeyId"
    map_arn_name = "Arn"
    map_name_name = "Name"
    json_keys_key = "JsonKeys"
    links_key = "LinksTo"
    map_name = "SecretsMapping"

    def __init__(self, name: str, definition: dict, settings: "ComposeXSettings"):
        """
        Initialize base secret with core properties.

        :param str name: The secret name
        :param dict definition: The secret definition from compose file
        :param ComposeXSettings settings: The compose settings
        """
        self.name = name
        self.logical_name = NONALPHANUM.sub("", self.name)
        self.definition = deepcopy(definition)
        self.settings = settings
        self.services: List[Any] = []
        self.links = [EXEC_ROLE_T, TASK_ROLE_T]

        # AWS-related properties
        self.arn: Optional[Any] = None
        self.iam_arn: Optional[Any] = None
        self.aws_name: Optional[str] = None
        self.kms_key: Optional[str] = None
        self.kms_key_arn: Optional[Any] = None

        # ECS and mapping properties
        self.ecs_secret: List[Any] = []
        self.mapping: dict = {}

    @property
    def env_var(self) -> EcsEnvVar:
        """
        Create an environment variable for the secret.

        :return: ECS environment variable
        :rtype: EcsEnvVar
        """
        env_var_name = self._get_env_var_name()
        return EcsEnvVar(Name=env_var_name, Value=self.arn)

    def _get_env_var_name(self) -> str:
        """
        Get the environment variable name for the secret.

        :return: Environment variable name
        :rtype: str
        """
        x_secrets_config = self.definition.get("x-secrets", {})
        if keyisset("VarName", x_secrets_config):
            return x_secrets_config["VarName"]
        return re.sub(r"\W+", "", self.name.replace("-", "_").upper())

    def has_lookup_config(self) -> bool:
        """
        Check if the secret has lookup configuration.

        :return: True if lookup config exists
        :rtype: bool
        """
        return keyisset("Lookup", self.definition.get(self.x_key, {}))

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
        Get the filtered JSON keys configuration.

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

    def get_links_config(self) -> List[str]:
        """
        Get the IAM role links configuration.

        :return: List of IAM roles to link to
        :rtype: List[str]
        """
        x_config = self.definition.get(self.x_key, {})
        if keyisset(self.links_key, x_config):
            return x_config[self.links_key]
        return [EXEC_ROLE_T, TASK_ROLE_T]

    def update_settings_mappings(self) -> None:
        """
        Update the settings with the secret mapping if it exists.
        """
        if self.mapping:
            self.settings.secrets_mappings.update({self.logical_name: self.mapping})
