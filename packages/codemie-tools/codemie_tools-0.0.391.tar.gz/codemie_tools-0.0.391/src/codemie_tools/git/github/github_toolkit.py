from typing import List, Any, Optional, Dict

from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.git.github.github_openai_tools import (
    CreateFileTool, DeleteFileTool, CreatePRTool,
    ListBranchesTool, CreateGithubBranchTool, OpenAIUpdateFileWholeTool, OpenAIUpdateFileDiffTool, SetActiveBranchTool
)
from codemie_tools.git.github.tools_vars import (
    SET_ACTIVE_BRANCH_TOOL, CREATE_FILE_TOOL, UPDATE_FILE_TOOL, UPDATE_FILE_DIFF_TOOL,
    DELETE_FILE_TOOL, CREATE_PULL_REQUEST_TOOL, CREATE_GIT_BRANCH_TOOL, LIST_BRANCHES_TOOL,
    GET_PR_CHANGES, CREATE_PR_CHANGE_COMMENT
)
from codemie_tools.git.utils import init_github_api_wrapper, GitCredentials

class GitHubToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.GIT
    settings_config: bool = True
    tools: List[Tool] = [
        Tool.from_metadata(SET_ACTIVE_BRANCH_TOOL),
        Tool.from_metadata(CREATE_FILE_TOOL),
        Tool.from_metadata(UPDATE_FILE_TOOL),
        Tool.from_metadata(UPDATE_FILE_DIFF_TOOL),
        Tool.from_metadata(DELETE_FILE_TOOL),
        Tool.from_metadata(CREATE_PULL_REQUEST_TOOL),
        Tool.from_metadata(CREATE_GIT_BRANCH_TOOL),
        Tool.from_metadata(LIST_BRANCHES_TOOL),
        Tool.from_metadata(GET_PR_CHANGES),
        Tool.from_metadata(CREATE_PR_CHANGE_COMMENT),
    ]

class CustomGitHubToolkit(BaseToolkit):
    git_creds: GitCredentials
    api_wrapper: Optional[Any] = None
    llm_model: Optional[Any] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return GitHubToolkitUI().model_dump()

    @classmethod
    def get_toolkit(cls,
                    configs: Dict[str, Any],
                    llm_model: Optional[BaseChatModel] = None):
        git_creds = GitCredentials(**configs)
        api_wrapper = init_github_api_wrapper(git_creds)
        return CustomGitHubToolkit(git_creds=git_creds,
                                   api_wrapper=api_wrapper,
                                   llm_model=llm_model)

    def get_tools(self) -> List[BaseTool]:
        tools = [
            CreateFileTool(api_wrapper=self.api_wrapper, credentials=self.git_creds),
            DeleteFileTool(api_wrapper=self.api_wrapper, credentials=self.git_creds),
            CreatePRTool(api_wrapper=self.api_wrapper, credentials=self.git_creds),
            ListBranchesTool(api_wrapper=self.api_wrapper, credentials=self.git_creds),
            SetActiveBranchTool(api_wrapper=self.api_wrapper, credentials=self.git_creds),
            CreateGithubBranchTool(api_wrapper=self.api_wrapper, credentials=self.git_creds),
            OpenAIUpdateFileWholeTool(api_wrapper=self.api_wrapper, credentials=self.git_creds,
                                      llm_model=self.llm_model),
            OpenAIUpdateFileDiffTool(api_wrapper=self.api_wrapper, credentials=self.git_creds,
                                     llm_model=self.llm_model)
        ]
        return tools
