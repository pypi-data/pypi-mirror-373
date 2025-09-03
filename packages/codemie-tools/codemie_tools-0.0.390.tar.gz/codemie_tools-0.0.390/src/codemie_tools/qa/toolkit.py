from typing import Optional, List, Tuple, Dict, Any
from requests.exceptions import HTTPError

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.qa.tools_vars import ZEPHYR_TOOL, ZEPHYR_SQUAD_TOOL
from codemie_tools.qa.zephyr.generic_tool import ZephyrConfig, ZephyrGenericTool
from codemie_tools.qa.zephyr_squad.generic_tool import ZephyrSquadGenericTool, ZephyrSquadConfig
from langchain_core.tools import BaseTool

from codemie_tools.utils.common import humanize_error

# Entity and method that is used for integration healthcheck
ZEPHYR_HEALTHCHECK_ENTITY = "healthcheck"
ZEPHYR_HEALTHCHECK_METHOD = "get_health"
ZEPHYR_SQUAD_HEALTHCHECK_URL = "/serverinfo"

class QualityAssuranceToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.QUALITY_ASSURANCE
    tools: List[Tool] = [
        Tool.from_metadata(ZEPHYR_TOOL, settings_config=True),
        Tool.from_metadata(ZEPHYR_SQUAD_TOOL, settings_config=True),
    ]
    label: str = ToolSet.QUALITY_ASSURANCE.value


class QualityAssuranceToolkit(BaseToolkit):
    zephyr_config: Optional[ZephyrConfig] = None
    zephyr_squad_config: Optional[ZephyrSquadConfig] = None

    @classmethod
    def get_tools_ui_info(cls):
        return QualityAssuranceToolkitUI().model_dump()

    def get_tools(self, **kwargs) -> List[BaseTool]:
        tools = [
            ZephyrGenericTool(zephyr_config=self.zephyr_config),
            ZephyrSquadGenericTool(config=self.zephyr_squad_config),
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any] = None):
        zephyr_config = ZephyrConfig(**configs["zephyr"]) if "zephyr" in configs else None
        zephyr_squad_config = ZephyrSquadConfig(**configs["zephyr_squad"]) if "zephyr_squad" in configs else None
        return cls(zephyr_config=zephyr_config, zephyr_squad_config=zephyr_squad_config)

    @classmethod
    def zephyr_integration_healthcheck(cls, zephyr_config: Dict[str, Any] = None) -> Tuple[bool, str]:
        try:
            tool = ZephyrGenericTool(zephyr_config=ZephyrConfig(**zephyr_config))
            tool.execute(entity_str=ZEPHYR_HEALTHCHECK_ENTITY, method_str=ZEPHYR_HEALTHCHECK_METHOD)
        except Exception as e:
            return False, humanize_error(e)

        return True, ""

    @classmethod
    def zehpyr_squad_integration_healthcheck(cls, zephyr_squad_config: Dict[str, Any] = None) -> Tuple[bool, str]:
        try:
            tool = ZephyrSquadGenericTool(config=ZephyrSquadConfig(**zephyr_squad_config))
            tool.execute(relative_path=ZEPHYR_SQUAD_HEALTHCHECK_URL, method="GET")
        except Exception as e:
            return False, humanize_error(e)

        return True, ""
        
