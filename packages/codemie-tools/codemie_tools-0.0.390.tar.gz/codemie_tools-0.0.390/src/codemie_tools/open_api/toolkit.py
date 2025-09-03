from typing import Any, Dict

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import Tool, ToolKit, ToolSet
from codemie_tools.open_api.models import OpenApiConfig
from codemie_tools.open_api.tools import InvokeRestApiBySpec, GetOpenApiSpec
from codemie_tools.open_api.tools_vars import OPEN_API_TOOL, OPEN_API_SPEC_TOOL


class OpenApiToolkit(BaseToolkit):
    openapi_config: OpenApiConfig

    @classmethod
    def get_tools_ui_info(cls):
        tools = [
            Tool.from_metadata(OPEN_API_TOOL),
            Tool.from_metadata(OPEN_API_SPEC_TOOL),
        ]
        return ToolKit(
            toolkit=ToolSet.OPEN_API,
            tools=tools,
            label=ToolSet.OPEN_API_LABEL.value,
            settings_config=True,
        ).model_dump()

    def get_tools(self) -> list:
        tools = [
            InvokeRestApiBySpec(openapi_config=self.openapi_config),
            GetOpenApiSpec(openapi_config=self.openapi_config),
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any] = None):
        open_api = OpenApiConfig(**configs)
        return OpenApiToolkit(openapi_config=open_api)
