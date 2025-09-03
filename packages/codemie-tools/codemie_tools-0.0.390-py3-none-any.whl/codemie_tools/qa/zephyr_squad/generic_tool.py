import json
from typing import Optional, Type

from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.qa.tools_vars import ZEPHYR_SQUAD_TOOL
from codemie_tools.qa.zephyr_squad.api_wrapper import ZephyrRestAPI


class ZephyrSquadConfig(BaseModel):
    account_id: str
    access_key: str
    secret_key: str


class ZephyrSquadToolInput(BaseModel):
    method: str = Field(
        ...,
        description="""
        HTTP method to be used in an API call, e.x. GET or POST
        """.strip()
    )
    relative_path: str = Field(
        ...,
        description="""
        Relative path excluding base url and /public/rest/api/1.0/config/, e.x.:
        - /cycle?expand=123&cloned123CycleId=123
        - /executions/search?executionId=123
        - ...
        """.strip()
    )
    body: Optional[str] = Field(
        ...,
        description="""
        Optional JSON of input parameters of the method. MUST be string with valid JSON.
        """
    )
    content_type: Optional[str] = Field(
        default="application/json",
        description="""
        Content type to pass in the header of the HTTP request. For ex. application/json, application/text, etc.
        """
    )

class ZephyrSquadGenericTool(CodeMieTool):
    config: Optional[ZephyrSquadConfig] = Field(exclude=True, default=None)
    name: str = ZEPHYR_SQUAD_TOOL.name
    description: str = ZEPHYR_SQUAD_TOOL.description
    args_schema: Type[BaseModel] = ZephyrSquadToolInput

    def execute(
            self,
            method: str,
            relative_path: str,
            body: Optional[str] = None,
            content_type: str = 'application/json'
    ):
        if not self.config:
            raise ValueError("Zephyr Squad config is not provided. Please set it before using the tool.")

        api = ZephyrRestAPI(
            account_id=self.config.account_id,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
        )

        data = json.loads(body) if body else {}

        return api.request(
            path=relative_path,
            method=method,
            json=data,
            headers={'Content-Type': content_type},
        ).content
