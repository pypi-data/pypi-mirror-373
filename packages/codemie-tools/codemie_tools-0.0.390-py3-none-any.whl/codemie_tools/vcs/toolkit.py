from typing import Optional, Dict, Any, List

from pydantic import BaseModel

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.vcs.tools import GithubTool, GitlabTool
from codemie_tools.vcs.tools_vars import GITHUB_TOOL, GITLAB_TOOL


class GitConfig(BaseModel):
    base_url: Optional[str] = None
    access_token: Optional[str] = None


class VcsToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.VCS
    tools: List[Tool] = [
        Tool.from_metadata(GITHUB_TOOL, settings_config=True),
        Tool.from_metadata(GITLAB_TOOL, settings_config=True),
    ]


class VcsToolkit(BaseToolkit):
    git_config: GitConfig

    @classmethod
    def get_tools_ui_info(cls):
        return ToolKit(
            toolkit=ToolSet.VCS,
            tools=[
                Tool.from_metadata(GITHUB_TOOL, settings_config=True),
                Tool.from_metadata(GITLAB_TOOL, settings_config=True),
            ]
        ).model_dump()

    def get_tools(self) -> list:
        tools = []
        if not self.git_config.base_url or "github" in self.git_config.base_url:
            tools.append(GithubTool(access_token=self.git_config.access_token))
        else:
            tools.append(GitlabTool(
                base_url=self.git_config.base_url,
                access_token=self.git_config.access_token
            ))
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        git_config = GitConfig(**configs)
        return VcsToolkit(git_config=git_config)
