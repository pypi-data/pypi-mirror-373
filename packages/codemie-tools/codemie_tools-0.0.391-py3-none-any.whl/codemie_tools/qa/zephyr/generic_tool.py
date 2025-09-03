import json
from types import GeneratorType
from typing import Optional, Type
from pydantic import BaseModel, Field
from zephyr import ZephyrScale

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.qa.tools_vars import ZEPHYR_TOOL

class ZephyrConfig(BaseModel):
    url: str
    token: str

class ZephyrToolInput(BaseModel):
    entity_str: str = Field(
        ...,
        description="""
        The Zephyr entity name. 
        Can be one of the (test_cases, test_cycles, test_plans, test_executions,
        folders, statuses, priorities, environments, projects, links, issue_links, 
        automations, healthcheck). Required parameter.
        """.strip()
    )
    method_str: str = Field(
        ...,
        description="""
        Required parameter: The method that should be executed on the entity.
        Always use "dir" as value before you run the real method to get the list of available methods.
        **Important:** If you receive an error that object has no attribute then use "dir".
        """
    )
    body: Optional[str] = Field(
        ...,
        description="""
        Optional JSON of input parameters of the method. MUST be string with valid JSON.
        """
    )

class ZephyrGenericTool(CodeMieTool):
    zephyr_config: Optional[ZephyrConfig] = Field(exclude=True, default=None)
    name: str = ZEPHYR_TOOL.name
    description: str = ZEPHYR_TOOL.description
    args_schema: Type[BaseModel] = ZephyrToolInput

    def execute(self, entity_str: str, method_str: str, body: Optional[str] = None):
        if not self.zephyr_config:
            raise ValueError("Zephyr Scale config is not provided. Please set it before using the tool.")
        zephyr_base_url = self.zephyr_config.url
        if not zephyr_base_url.endswith("/"):
            zephyr_base_url += "/"

        zephyr_api = ZephyrScale(base_url=zephyr_base_url, token=self.zephyr_config.token).api
        entity = getattr(zephyr_api, entity_str)

        if method_str == "dir":
            return dir(entity)

        method = getattr(entity, method_str)
        params = json.loads(body) if body else {}
        result = method(**params)

        if isinstance(result, GeneratorType):
            result_array = []
            for item in result:
                result_array.append(item)
            return result_array
        else:
            return method(**params)
