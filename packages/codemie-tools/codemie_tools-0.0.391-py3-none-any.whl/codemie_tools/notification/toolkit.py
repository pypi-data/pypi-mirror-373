from typing import List, Optional, Any, Dict, Tuple

from langchain_core.tools import BaseTool

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, Tool, ToolSet
from codemie_tools.notification.email.models import EmailToolConfig
from codemie_tools.notification.email.tools import EmailTool
from codemie_tools.notification.telegram.tools import TelegramTool, TelegramConfig
from codemie_tools.notification.tools_vars import EMAIL_TOOL, TELEGRAM_TOOL
from codemie_tools.utils.common import humanize_error

class NotificationToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.NOTIFICATION
    tools: List[Tool] = [
        Tool.from_metadata(EMAIL_TOOL, settings_config=True),
        Tool.from_metadata(TELEGRAM_TOOL, settings_config=True),
    ]


class NotificationToolkit(BaseToolkit):
    email_creds: Optional[EmailToolConfig] = None
    telegram_config: Optional[TelegramConfig] = None

    @classmethod
    def get_tools_ui_info(cls):
        return NotificationToolkitUI().model_dump()

    def get_tools(self, **kwargs) -> List[BaseTool]:
        tools = [
            EmailTool(email_creds=self.email_creds),
            TelegramTool(telegram_config=self.telegram_config),
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any] = None):
        email_config = EmailToolConfig(**configs["email"]) if "email" in configs else None
        telegram_config = TelegramConfig(**configs["telegram"]) if "telegram" in configs else None
        return NotificationToolkit(email_creds=email_config, telegram_config=telegram_config)

    @classmethod
    def email_integration_healthcheck(cls, email_config: Dict[str, Any] = None) -> Tuple[bool, str]:
        try:
            email_tool_config = EmailToolConfig(**email_config)
            email_tool = EmailTool(email_creds=email_tool_config)

            return email_tool.integration_healthcheck()
        except Exception as e:
            return False, humanize_error(e)
