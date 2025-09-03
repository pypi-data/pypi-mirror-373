"""Azure DevOps Toolkit."""

from typing import List, Optional, Dict, Any

from pydantic import ConfigDict

from langchain_core.tools import BaseTool

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.git.azure_devops.tools import (
    AzureDevOpsCredentials,
    ListBranchesTool,
    SetActiveBranchTool,
    ListFilesTool,
    ListOpenPullRequestsTool,
    GetPullRequestTool,
    ListPullRequestFilesTool,
    CreateBranchTool,
    ReadFileTool,
    CreateFileTool,
    UpdateFileTool,
    DeleteFileTool,
    GetWorkItemsTool,
    CommentOnPullRequestTool,
    CreatePullRequestTool,
    AzureDevOpsClient,
)


class AzureDevOpsToolkit(BaseToolkit):
    """Toolkit for Azure DevOps operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    credentials: AzureDevOpsCredentials
    client: Optional[AzureDevOpsClient] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        # no need this function at this moment
        pass

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        """
        Initialize toolkit with Azure DevOps credentials.

        Args:
            configs (Dict[str, Any]): Configuration containing Azure DevOps credentials

        Returns:
            AzureDevOpsToolkit: Initialized toolkit
        """
        credentials = AzureDevOpsClient.init_credentials(configs=configs)
        client = AzureDevOpsClient(credentials)

        return AzureDevOpsToolkit(credentials=credentials, client=client)

    def get_tools(self) -> List[BaseTool]:
        """
        Get list of available Azure DevOps tools.

        Returns:
            List[BaseTool]: List of Azure DevOps tools
        """
        tools = [
            ListBranchesTool(client=self.client, credentials=self.credentials),
            SetActiveBranchTool(client=self.client, credentials=self.credentials),
            ListFilesTool(client=self.client, credentials=self.credentials),
            ListOpenPullRequestsTool(client=self.client, credentials=self.credentials),
            GetPullRequestTool(client=self.client, credentials=self.credentials),
            ListPullRequestFilesTool(client=self.client, credentials=self.credentials),
            CreateBranchTool(client=self.client, credentials=self.credentials),
            ReadFileTool(client=self.client, credentials=self.credentials),
            CreateFileTool(client=self.client, credentials=self.credentials),
            UpdateFileTool(client=self.client, credentials=self.credentials),
            DeleteFileTool(client=self.client, credentials=self.credentials),
            GetWorkItemsTool(client=self.client, credentials=self.credentials),
            CommentOnPullRequestTool(client=self.client, credentials=self.credentials),
            CreatePullRequestTool(client=self.client, credentials=self.credentials),
        ]

        return tools
