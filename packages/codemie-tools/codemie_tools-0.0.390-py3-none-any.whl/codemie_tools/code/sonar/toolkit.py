from typing import List, Optional, Any, Dict, Tuple 
from requests import RequestException

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.code.sonar.config import SonarToolConfig
from codemie_tools.code.sonar.tools import SonarTool
from codemie_tools.code.sonar.tools_vars import SONAR_TOOL
from codemie_tools.utils.common import humanize_error


class SonarToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.CODEBASE_TOOLS
    tools: List[Tool] = [
        Tool.from_metadata(SONAR_TOOL, settings_config=True),
    ]


class SonarToolkit(BaseToolkit):
    sonar_creds: Optional[SonarToolConfig] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return ToolKit(
            toolkit=ToolSet.CODEBASE_TOOLS,
            tools=[
                Tool.from_metadata(SONAR_TOOL),
            ]
        ).model_dump()

    def get_tools(self):
        tools = [
            SonarTool(conf=self.sonar_creds)
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        sonar_creds = SonarToolConfig(**configs)
        return SonarToolkit(
            sonar_creds=sonar_creds
        )

    @classmethod
    def sonar_integration_healthcheck(cls, url: Optional[str], sonar_token: Optional[str], sonar_project_name: Optional[str]) -> Tuple[bool, str]:
        """
        Performs a check for the integration with SonarQube. It validates the provided token
        and verifies that the specified project is accessible in SonarQube.
        Args:
            url (Optional[str]): The base URL of the SonarQube instance.
            sonar_token (Optional[str]): The authentication token for SonarQube.
            sonar_project_name (Optional[str]): The key for SonarQube project.

        Returns:
            Tuple[bool, str]: A tuple where the first element indicates success (`True`) or failure (`False`),
            and the second element contains a message describing the the reason for failure.
        """        
        try:

            tool = SonarTool(
                SonarToolConfig(url=url, sonar_token=sonar_token, sonar_project_name=sonar_project_name)
            )

            response = tool.execute("api/authentication/validate", "")

            if not response.get('valid', False):
                return False, "Invalid token"

            if not sonar_project_name:
                return False, "Project name not provided"

            response = tool.execute("api/components/show", f'{{"component": "{sonar_project_name}"}}')

            if 'component' not in response: 
                errors = response.get("errors", [{"msg": "Error occured when trying to get project inforamtion"}])
                return False, (" | ").join([error.get('msg', "") for error in errors])

            component = response.get("component", {})

            if component.get('key', "") == sonar_project_name and component.get('qualifier', "") == "TRK":
                return True, ""

        except Exception as e:
            return False, humanize_error(e)
