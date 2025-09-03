import json
from typing import Optional, Dict, Any, Type

import requests
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.access_management.keycloak.models import KeycloakConfig
from codemie_tools.access_management.keycloak.tools_vars import KEYCLOAK_TOOL
from codemie_tools.access_management.keycloak.utils import get_keycloak_admin_token


class KeycloakToolInput(BaseModel):
    method: str = Field(
        ...,
        description="The HTTP method to use for the request (GET, POST, PUT, DELETE, etc.). Required parameter."
    )
    relative_url: str = Field(
        ...,
        description="""
        The relative URL of the Keycloak Admin API to call, e.g. '/users'. Required parameter.
        In case of GET method, you MUST include query parameters in the URL.
        """
    )
    params: Optional[str] = Field(
        ...,
        description="Optional string dictionary of parameters to be sent in the query string or request body."
    )


class KeycloakTool(CodeMieTool):
    keycloak_config: KeycloakConfig
    name: str = KEYCLOAK_TOOL.name
    description: str = KEYCLOAK_TOOL.description
    args_schema: Type[BaseModel] = KeycloakToolInput

    def execute(self, method: str, relative_url: str, params: Optional[str] = "", *args):
        if not relative_url.startswith('/'):
            raise ValueError("The 'relative_url' must start with '/'.")

        base_url = self.keycloak_config.base_url
        realm = self.keycloak_config.realm
        access_token = get_keycloak_admin_token(self.keycloak_config)
        full_url = f"{base_url}/admin/realms/{realm}{relative_url}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        payload_params = self.parse_payload_params(params)
        response = requests.request(method, full_url, headers=headers, json=payload_params)
        response.raise_for_status()
        return response.text

    def parse_payload_params(self, params: Optional[str]) -> Dict[str, Any]:
        if params:
            json_acceptable_string = params.replace("'", "\"")
            return json.loads(json_acceptable_string)
        return {}
