import json
import traceback
from json import JSONDecodeError
from typing import Any, Dict, Type, Optional

import requests
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.code.sonar.config import SonarToolConfig
from codemie_tools.code.sonar.tools_vars import SONAR_TOOL


class SonarToolInput(BaseModel):
    relative_url: str = Field(
        ...,
        description="""
        Required parameter: The relative URI for SONAR REST API.
        URI must start with a forward slash and '/api/issues/search..'.
        Do not include query parameters in the URL, they must be provided separately in 'params'.
        For search/read operations, you MUST always get "cleanCodeAttributeCategories", 
        "severity", "issueStatuses", "types" and set maxResult,
        until users ask explicitly for more fields.
        """
    )
    params: Optional[str] = Field(
        default="",
        description="""
        Optional JSON of parameters to be sent in request body or query params. MUST be string with 
        valid JSON. For search/read operations, you MUST always get "cleanCodeAttributeCategories", 
        "severity", "issueStatuses", "types" and set maxResult,
        until users ask explicitly for more fields.
        """
    )


def parse_payload_params(params: Optional[str]) -> Dict[str, Any]:
    if params:
        try:
            return json.loads(params)
        except JSONDecodeError:
            stacktrace = traceback.format_exc()
            raise ToolException(f"Sonar tool exception. Passed params are not valid JSON. {stacktrace}")
    return {}


class SonarTool(CodeMieTool):
    name: str = SONAR_TOOL.name
    config: Optional[SonarToolConfig] = Field(exclude=True, default=None)
    args_schema: Type[BaseModel] = SonarToolInput
    description: str = SONAR_TOOL.description

    def __init__(self, conf: SonarToolConfig = None):
        super().__init__()
        self.config = conf

    def execute(self, relative_url: str, params: str, *args) -> str:
        self.validate_config()
        payload_params = parse_payload_params(params)
        payload_params['componentKeys'] = self.config.sonar_project_name
        return requests.get(
            url=f"{self.config.url}/{relative_url}",
            auth=(self.config.sonar_token, ''),
            params=payload_params
        ).json()

    def validate_config(self):
        if not self.config:
            raise ValueError(
                f"{self.name} integration enabled but credentials are not provided in "
                f"Please provide credentials or disable {self.name} integration "
                f"in the assistant's properties."
            )
