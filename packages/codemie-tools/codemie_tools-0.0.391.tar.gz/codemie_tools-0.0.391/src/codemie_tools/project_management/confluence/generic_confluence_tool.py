import json
import logging
import re
import traceback
from json import JSONDecodeError
from typing import Type, Dict, Any, Optional
from atlassian import Confluence
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException
from markdownify import markdownify

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.project_management.confluence.tools_vars import GENERIC_CONFLUENCE_TOOL
from codemie_tools.project_management.confluence.utils import validate_creds, prepare_page_payload
from codemie_tools.base.utils import clean_json_string

logger = logging.getLogger(__name__)


class ConfluenceInput(BaseModel):
    method: str = Field(
        ...,
        description="The HTTP method to use for the request (GET, POST, PUT, DELETE, etc.). Required parameter."
    )
    relative_url: str = Field(
        ...,
        description="""
        Required parameter: The relative URI for Confluence API.
        URI must start with a forward slash and '/rest/...'.
        Do not include query parameters in the URL, they must be provided separately in 'params'.
        For search/read operations, you MUST always get minimum fields and set max results, until users ask explicitly for more fields.
        """.strip()
    )
    params: Optional[str] = Field(
        default="",
        description="""
        Optional JSON of parameters to be sent in request body or query params. MUST be string with valid JSON. 
        For search/read operations, you MUST always get minimum fields and set max results, until users ask explicitly for more fields.
        For search/read operations you must generate CQL query string and pass it as params.
        """.strip()
    )
    is_markdown: bool = Field(
        default=False,
        description="""
        Optional boolean to indicate if the payload main content is in Markdown format. 
        If true, the payload will be converted to HTML before sending to Confluence.
        """.strip()
    )


def parse_payload_params(params: Optional[str]) -> Dict[str, Any]:
    if params:
        try:
            return json.loads(clean_json_string(params))
        except JSONDecodeError:
            stacktrace = traceback.format_exc()
            raise ToolException(f"Confluence tool exception. Passed params are not valid JSON. {stacktrace}")
    return {}


class GenericConfluenceTool(CodeMieTool):
    confluence: Confluence
    name: str = GENERIC_CONFLUENCE_TOOL.name
    description: str = GENERIC_CONFLUENCE_TOOL.description
    args_schema: Type[BaseModel] = ConfluenceInput
    page_search_pattern: str = r'/rest/api/content/\d+'
    throw_truncated_error: bool = False
    page_action_prefix: str = "/rest/api/content"

    def execute(self, method: str, relative_url: str, params: Optional[str] = "", is_markdown: bool = False, *args):
        validate_creds(self.confluence)
        payload_params = parse_payload_params(params)
        if method == "GET":
            response = self.confluence.request(
                method=method,
                path=relative_url,
                params=payload_params,
                advanced_mode=True
            )
            response_text = self.process_search_response(relative_url, response)
        else:
            if relative_url.startswith(self.page_action_prefix) and is_markdown:
                payload_params = prepare_page_payload(payload_params)
            response = self.confluence.request(
                method=method,
                path=relative_url,
                data=payload_params,
                advanced_mode=True,
            )
            response_text = response.text
        response_string = f"HTTP: {method}{relative_url} -> {response.status_code}{response.reason}{response_text}"
        logger.debug(response_string)
        return response_string

    def process_search_response(self, relative_url: str, response) -> str:
        if re.match(self.page_search_pattern, relative_url):
            self.tokens_size_limit = 20000
            body = markdownify(response.text, heading_style="ATX")
            return body
        return response.text
