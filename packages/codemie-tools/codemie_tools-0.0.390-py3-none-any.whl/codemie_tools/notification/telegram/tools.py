import json
from typing import Optional, Dict, Any, Type

import requests
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.notification.tools_vars import TELEGRAM_TOOL


class TelegramConfig(BaseModel):
    bot_token: str


class TelegramToolInput(BaseModel):
    method: str = Field(
        ...,
        description="The HTTP method to use for the request (GET, POST). Required parameter."
    )
    relative_url: str = Field(
        ...,
        description="""
        The relative URL of the Telegram Bot API to call, e.g. 'sendMessage'. Required parameter.
        In case of GET method, you MUST include query parameters in the URL.
        """
    )
    params: Optional[str] = Field(
        ...,
        description="""
        Optional JSON of parameters to be sent in request body or query params. MUST be string with valid JSON. 
        Important: to send message, you MUST get "chat_id" parameter first.
        """
    )


class TelegramTool(CodeMieTool):
    telegram_config: Optional[TelegramConfig] = Field(exclude=True, default=None)
    name: str = TELEGRAM_TOOL.name
    description: str = TELEGRAM_TOOL.description
    args_schema: Type[BaseModel] = TelegramToolInput

    def execute(self, method: str, relative_url: str, params: Optional[str] = ""):
        if not self.telegram_config:
            raise ValueError("Telegram config is provided set. Please set it before using the tool.")
        if not relative_url.startswith('/'):
            relative_url = f'/{relative_url}'

        base_url = f"https://api.telegram.org/bot{self.telegram_config.bot_token}"
        full_url = f"{base_url}{relative_url}"
        headers = {
            'Content-Type': 'application/json'
        }
        payload_params = self.parse_payload_params(params)
        response = requests.request(method, full_url, headers=headers, json=payload_params)
        response.raise_for_status()
        return response.text

    def parse_payload_params(self, params: Optional[str]) -> Dict[str, Any]:
        if params:
            json_acceptable_string = params.replace("'", "\"")
            return json.loads(json_acceptable_string)
        return {}
