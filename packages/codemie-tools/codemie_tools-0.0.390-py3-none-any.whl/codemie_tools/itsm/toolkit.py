from typing import Optional, Dict, Any, List
from pydantic import BaseModel, model_validator

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, Tool, ToolSet
from codemie_tools.utils.common import humanize_error

from .servicenow_tool import ServiceNowTableTool
from .tool_vars import SNOW_TABLE_TOOL

class ServiceNowConfig(BaseModel):
    url: str
    api_key: str

    @classmethod
    @model_validator(mode='before')
    def validate_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['url', 'api_key']
        for field in required_fields:
            if field not in values or not values[field]:
                raise ValueError(f"{field} is a required field and must be provided.")
        return values


class ITSMToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.ITSM
    tools: List[Tool] = [
        Tool.from_metadata(SNOW_TABLE_TOOL, settings_config=True)
    ]
    label: str = ToolSet.ITSM.value


class ITSMToolkit(BaseToolkit):

    servicenow_config: ServiceNowConfig

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return ITSMToolkitUI().model_dump()

    @classmethod
    def snow_integration_healthcheck(cls, servicenow_config: Dict[str, Any]):
        try:
            snow_tool = cls.create_snow_tool(ServiceNowConfig(**servicenow_config))
            snow_tool.execute(
                method="GET",
                table="incident",
                params='{"sysparm_limit": 1}'
            )
        except Exception as e:
            return False, humanize_error(e)

        return True, ""

    @classmethod
    def create_snow_tool(cls, servicenow_config: ServiceNowConfig):
        return ServiceNowTableTool(
            base_url=servicenow_config.url,
            api_key=servicenow_config.api_key
        )

    def get_tools(self):
        """
        Returns a list of tools available in this toolkit.
        """
        return [ITSMToolkit.create_snow_tool(servicenow_config=self.servicenow_config)]


    @classmethod
    def get_toolkit(cls,
        configs: Dict[str, Any],
        chat_model: Optional[Any] = None):

        servicenow_config = ServiceNowConfig(**configs["servicenow"]) if "servicenow" in configs else None
        return ITSMToolkit(servicenow_config=servicenow_config, chat_model=chat_model)
