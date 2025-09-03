import logging
from typing import Optional, Dict, Any

from codemie_tools.access_management.keycloak.models import KeycloakConfig
from codemie_tools.access_management.keycloak.tools import KeycloakTool
from codemie_tools.access_management.keycloak.tools_vars import KEYCLOAK_TOOL
from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool

logger = logging.getLogger(__name__)

class AccessManagementToolkit(BaseToolkit):
    keycloak_config: Optional[KeycloakConfig] = None

    @classmethod
    def get_tools_ui_info(cls):
        return ToolKit(
            toolkit=ToolSet.ACCESS_MANAGEMENT,
            tools=[
                Tool.from_metadata(KEYCLOAK_TOOL, settings_config=True),
            ]
        ).model_dump()

    def get_tools(self) -> list:
        tools = []
        if self.keycloak_config:
            tools.append(KeycloakTool(keycloak_config=self.keycloak_config))
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        keycloak_config = KeycloakConfig(**configs["keycloak"]) if "keycloak" in configs else None
        return AccessManagementToolkit(keycloak_config=keycloak_config)