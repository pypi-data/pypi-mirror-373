from typing import List, Optional, Any, Dict

from atlassian import Jira, Confluence
from pydantic import BaseModel, model_validator

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.project_management.confluence.generic_confluence_tool import GenericConfluenceTool
from codemie_tools.project_management.confluence.tools_vars import GENERIC_CONFLUENCE_TOOL
from codemie_tools.project_management.jira.generic_tool import GenericJiraIssueTool, GenericJiraCloudIssueTool
from codemie_tools.project_management.jira.tools_vars import GENERIC_JIRA_TOOL
from codemie_tools.utils.common import humanize_error

from codemie_tools.base.file_object import FileObject

# Url that is used for testing jira integration
JIRA_TEST_URL: str = "/rest/api/2/myself"
# Url and expected response that are used for testing confluence integration
CONFLUENCE_TEST_URL: str = "/rest/api/user/current"
CONFLUENCE_TEST_RESPONSE: str = 'HTTP: GET/rest/api/user/current -> 200OK'
CONFLUENCE_ERROR_MSG: str = 'Access denied'

class JiraConfig(BaseModel):
    url: str
    username: Optional[str] = None
    token: str
    cloud: Optional[bool] = False

    @classmethod
    @model_validator(mode='before')
    def validate_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['url', 'token']
        for field in required_fields:
            if field not in values or not values[field]:
                raise ValueError(f"{field} is a required field and must be provided.")
        return values


class ConfluenceConfig(BaseModel):
    url: str
    username: Optional[str] = None
    token: str
    cloud: Optional[bool] = False

    @classmethod
    @model_validator(mode='before')
    def validate_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['url', 'token']
        for field in required_fields:
            if field not in values or not values[field]:
                raise ValueError(f"{field} is a required field and must be provided.")
        return values


class ProjectManagementToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.PROJECT_MANAGEMENT
    tools: List[Tool] = [
        Tool.from_metadata(GENERIC_JIRA_TOOL, settings_config=True),
        Tool.from_metadata(GENERIC_CONFLUENCE_TOOL, settings_config=True)
    ]
    label: str = ToolSet.PROJECT_MANAGEMENT.value


class ProjectManagementToolkit(BaseToolkit):
    jira_config: Optional[JiraConfig] = None
    confluence_config: Optional[ConfluenceConfig] = None
    file_object: Optional[FileObject] = None

    @classmethod
    def get_tools_ui_info(cls):
        return ProjectManagementToolkitUI().model_dump()

    def get_tools(self) -> list:
        tools = []
        if self.jira_config:
            jira_tool = ProjectManagementToolkit.create_jira_tool(self.jira_config, self.file_object)
            tools.append(jira_tool)
        if self.confluence_config:
            confluence_tool = ProjectManagementToolkit.create_confluence_tool(self.confluence_config)
            tools.append(confluence_tool)
        return tools

    @classmethod
    def create_jira_tool(cls, jira_config: JiraConfig, file_object: Optional[FileObject] = None) -> GenericJiraIssueTool:
        jira = Jira(
            url=jira_config.url,
            username=jira_config.username if jira_config.username else None,
            token=jira_config.token if not jira_config.cloud else None,
            password=jira_config.token if jira_config.cloud else None,
            cloud=jira_config.cloud
        )
        jira_tool = (
            GenericJiraIssueTool if not jira_config.cloud else GenericJiraCloudIssueTool
        )
        return jira_tool(jira=jira, file_object=file_object)

    @classmethod
    def create_confluence_tool(cls, confluence_config: ConfluenceConfig) -> GenericConfluenceTool:
        confluence = Confluence(
            url=confluence_config.url,
            username=confluence_config.username if confluence_config.username else None,
            password=confluence_config.token if confluence_config.cloud else None,
            token=confluence_config.token if not confluence_config.cloud else None,
            cloud=confluence_config.cloud
        )
        return GenericConfluenceTool(confluence=confluence)

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        jira_config = JiraConfig(**configs["jira"]) if "jira" in configs else None
        confluence_config = ConfluenceConfig(**configs["confluence"]) if "confluence" in configs else None
        file_object = configs.get("file_object", None)

        if file_object and not isinstance(file_object, dict):
            file_object = file_object.__dict__
        file_object = FileObject(**file_object) if file_object else None

        return cls(jira_config=jira_config, confluence_config=confluence_config, file_object=file_object)

    @classmethod
    def jira_integration_healthcheck(cls, jira_config: Dict[str, Any]):
        try:
            jira_tool = cls.create_jira_tool(JiraConfig(**jira_config))
            jira_tool.execute("GET", JIRA_TEST_URL)
        except Exception as e:
            return False, humanize_error(e)

        return True, ""

    @classmethod
    def confluence_integration_healthcheck(cls, confluence_config: Dict[str, Any]):
        try:
            confluence_tool = cls.create_confluence_tool(ConfluenceConfig(**confluence_config))
            response = confluence_tool.execute("GET", CONFLUENCE_TEST_URL)
            assert response.startswith(CONFLUENCE_TEST_RESPONSE), CONFLUENCE_ERROR_MSG
        except Exception as e:
            return False, humanize_error(e)

        return True, ""
