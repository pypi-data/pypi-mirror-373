import logging
from typing import List, Optional, Any, Dict

from langchain_core.language_models import BaseChatModel

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.data_management.file_system.code_executor import CodeExecutor
from codemie_tools.data_management.file_system.generate_image_tool import GenerateImageTool, AzureDalleAIConfig
from codemie_tools.data_management.file_system.run_python_tool import PythonRunCodeTool
from codemie_tools.data_management.file_system.tools import (
    ListDirectoryTool, ReadFileTool, WriteFileTool,
    CommandLineTool, DiffUpdateFileTool, ReplaceStringTool
)
from codemie_tools.data_management.file_system.tools_vars import READ_FILE_TOOL, WRITE_FILE_TOOL, LIST_DIRECTORY_TOOL, \
    COMMAND_LINE_TOOL, GENERATE_IMAGE_TOOL, PYTHON_RUN_CODE_TOOL, DIFF_UPDATE_FILE_TOOL, REPLACE_STRING_TOOL

logger = logging.getLogger(__name__)


class FileSystemToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.FILE_SYSTEM
    settings_config: bool = True
    tools: List[Tool] = [
        Tool.from_metadata(READ_FILE_TOOL),
        Tool.from_metadata(WRITE_FILE_TOOL),
        Tool.from_metadata(LIST_DIRECTORY_TOOL),
        Tool.from_metadata(COMMAND_LINE_TOOL),
        Tool.from_metadata(PYTHON_RUN_CODE_TOOL),
        Tool.from_metadata(GENERATE_IMAGE_TOOL),
        Tool.from_metadata(DIFF_UPDATE_FILE_TOOL),
        Tool.from_metadata(REPLACE_STRING_TOOL)
    ]
    label: str = ToolSet.FILE_MANAGEMENT_LABEL.value


class FileSystemToolkit(BaseToolkit):
    root_directory: Optional[str] = "."
    activate_command : Optional[str] = ""
    user_id: Optional[str] = ""
    file_repository: Optional[Any] = None
    azure_dalle_config: Optional[AzureDalleAIConfig] = None
    chat_model: Optional[Any] = None

    @classmethod
    def get_tools_ui_info(cls, is_admin: bool = False):
        if is_admin:
            return FileSystemToolkitUI().model_dump()
        return ToolKit(
            toolkit=ToolSet.FILE_SYSTEM,
            tools=[
                Tool.from_metadata(PYTHON_RUN_CODE_TOOL),
                Tool.from_metadata(GENERATE_IMAGE_TOOL),
            ]
        ).model_dump()

    def get_tools(self) -> list:
        tools = [
            ReadFileTool(root_dir=self.root_directory),
            ListDirectoryTool(root_dir=self.root_directory),
            WriteFileTool(root_dir=self.root_directory),
            CommandLineTool(root_dir=self.root_directory, activate_command=self.activate_command),
            DiffUpdateFileTool(root_dir=self.root_directory, llm_model=self.chat_model),
            PythonRunCodeTool(user_id=self.user_id, code_executor=CodeExecutor(file_repository=self.file_repository)),
            GenerateImageTool(azure_dalle_config=self.azure_dalle_config),
            ReplaceStringTool(root_dir=self.root_directory)
        ]
        return tools

    @classmethod
    def get_toolkit(cls,
                    configs: Dict[str, Any],
                    file_repository: Optional[Any] = None,
                    chat_model: Optional[BaseChatModel] = None):
        dalle_config = AzureDalleAIConfig(**configs["azure_dalle_config"]) if "azure_dalle_config" in configs else None
        root_directory = configs["root_directory"] if "root_directory" in configs else "."
        activate_command = configs["activate_command"] if "activate_command" in configs else ""
        user_id = configs["user_id"] if "user_id" in configs else ""
        return FileSystemToolkit(root_directory=root_directory,
                   activate_command=activate_command,
                   file_repository=file_repository,
                   user_id=user_id,
                   azure_dalle_config=dalle_config,
                   chat_model=chat_model)
