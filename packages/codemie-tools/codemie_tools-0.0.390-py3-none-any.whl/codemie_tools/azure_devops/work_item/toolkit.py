from typing import Optional, Dict, Any, List

from pydantic import BaseModel

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.azure_devops.work_item.tools import (
    SearchWorkItemsTool,
    CreateWorkItemTool,
    UpdateWorkItemTool,
    GetWorkItemTool,
    LinkWorkItemsTool,
    GetRelationTypesTool,
    GetCommentsTool
)
from codemie_tools.azure_devops.work_item.tools_vars import (
    SEARCH_WORK_ITEMS_TOOL,
    CREATE_WORK_ITEM_TOOL,
    UPDATE_WORK_ITEM_TOOL,
    GET_WORK_ITEM_TOOL,
    LINK_WORK_ITEMS_TOOL,
    GET_RELATION_TYPES_TOOL,
    GET_COMMENTS_TOOL
)


class AzureDevOpsWorkItemConfig(BaseModel):
    organization_url: Optional[str] = None
    project: Optional[str] = None
    token: Optional[str] = None
    limit: Optional[int] = 5


class AzureDevOpsWorkItemToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.AZURE_DEVOPS_WORK_ITEM
    tools: List[Tool] = [
        Tool.from_metadata(SEARCH_WORK_ITEMS_TOOL),
        Tool.from_metadata(CREATE_WORK_ITEM_TOOL),
        Tool.from_metadata(UPDATE_WORK_ITEM_TOOL),
        Tool.from_metadata(GET_WORK_ITEM_TOOL),
        Tool.from_metadata(LINK_WORK_ITEMS_TOOL),
        Tool.from_metadata(GET_RELATION_TYPES_TOOL),
        Tool.from_metadata(GET_COMMENTS_TOOL),
    ]


class AzureDevOpsWorkItemToolkit(BaseToolkit):
    ado_config: AzureDevOpsWorkItemConfig

    @classmethod
    def get_tools_ui_info(cls):
        return ToolKit(
            toolkit=ToolSet.AZURE_DEVOPS_WORK_ITEM,
            tools=[
                Tool.from_metadata(SEARCH_WORK_ITEMS_TOOL),
                Tool.from_metadata(CREATE_WORK_ITEM_TOOL),
                Tool.from_metadata(UPDATE_WORK_ITEM_TOOL),
                Tool.from_metadata(GET_WORK_ITEM_TOOL),
                Tool.from_metadata(LINK_WORK_ITEMS_TOOL),
                Tool.from_metadata(GET_RELATION_TYPES_TOOL),
                Tool.from_metadata(GET_COMMENTS_TOOL),
            ],
            settings_config=True
        ).model_dump()

    def get_tools(self) -> list:
        tools = [
            SearchWorkItemsTool(
                organization_url=self.ado_config.organization_url,
                project=self.ado_config.project,
                token=self.ado_config.token,
                limit=self.ado_config.limit
            ),
            CreateWorkItemTool(
                organization_url=self.ado_config.organization_url,
                project=self.ado_config.project,
                token=self.ado_config.token,
                limit=self.ado_config.limit
            ),
            UpdateWorkItemTool(
                organization_url=self.ado_config.organization_url,
                project=self.ado_config.project,
                token=self.ado_config.token,
                limit=self.ado_config.limit
            ),
            GetWorkItemTool(
                organization_url=self.ado_config.organization_url,
                project=self.ado_config.project,
                token=self.ado_config.token,
                limit=self.ado_config.limit
            ),
            LinkWorkItemsTool(
                organization_url=self.ado_config.organization_url,
                project=self.ado_config.project,
                token=self.ado_config.token,
                limit=self.ado_config.limit
            ),
            GetRelationTypesTool(
                organization_url=self.ado_config.organization_url,
                project=self.ado_config.project,
                token=self.ado_config.token,
                limit=self.ado_config.limit
            ),
            GetCommentsTool(
                organization_url=self.ado_config.organization_url,
                project=self.ado_config.project,
                token=self.ado_config.token,
                limit=self.ado_config.limit
            )
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        ado_config = AzureDevOpsWorkItemConfig(**configs)
        return AzureDevOpsWorkItemToolkit(ado_config=ado_config)
