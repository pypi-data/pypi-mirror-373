import json
import re
import traceback
import urllib.parse
import requests
from json import JSONDecodeError
from typing import Optional, Type, Any, Dict

from codemie_tools.base.codemie_tool import CodeMieTool
from langchain_core.tools import ToolException

from pydantic import BaseModel, Field

from .tool_vars import SNOW_TABLE_TOOL


class ServiceNowInput(BaseModel):
    method: str = Field(
        ...,
        description="""
        Required parameter: The HTTP method to use for the request (GET, POST, PUT, DELETE, etc.). Required parameter.
        """
    )
    table: str = Field(
        ...,
        description="""
        Required parameter: The table name to use in API.
        This parameter will be used to form request url, e.g. /api/now/table/{table}
        """
    )
    sys_id: Optional[str] = Field(
        default="",
        description="""
        Optional parameter: Sys_id of the record to use in API. Should only be supplied when working with individual record.
        This parameter will be used to form request url, e.g. /api/now/table/{table}/{sys_id}
        """
    )
    params: Optional[str] = Field(
        default="",
        description="""
        Optional parameter: **JSON of parameters** to be sent in request body or query params. MUST be string with valid JSON. 
        For search/read operations, you MUST always get "key", "summary", "status", "assignee", "issuetype" and 
        set maxResult, until users ask explicitly for more fields.
        """
    )
    body: Optional[str] = Field(
        default="",
        description="""
        Optional parameter: Body of JSON request to use with POST/PUT/PATCH methods.
        """
    )


def clean_json_string(json_string):
    """
    Extract JSON object from a string, removing extra characters before '{' and after '}'.

    Args:
    json_string (str): Input string containing a JSON object.

    Returns:
    str: Cleaned JSON string or original string if no JSON object found.
    """
    pattern = r'^[^{]*({.*})[^}]*$'
    match = re.search(pattern, json_string, re.DOTALL)
    if match:
        return match.group(1)
    return json_string


def normalize_query_params(params: Optional[str]) -> Dict[str, Any]:
    if params:
        try:
            return json.loads(clean_json_string(params))
        except JSONDecodeError:
            stacktrace = traceback.format_exc()
            raise ToolException(f"ServiceNow tool exception. Passed params are not valid JSON. {stacktrace}")
    return {}


def normalize_string(table: str) -> str:
    return table \
        .replace("\"", "") \
        .replace("'", "") \
        .replace("`", "") \
        .strip() \
        .lower()


class ServiceNowTableTool(CodeMieTool):

    args_schema: Type[BaseModel] = ServiceNowInput
    name: str = SNOW_TABLE_TOOL.name
    description: str = SNOW_TABLE_TOOL.description

    base_url: str
    api_key: str

    def execute(self, method: str, table: str, sys_id: Optional[str] = "", params: Optional[str] = "", body: Optional[str] = "") -> Any:
        query_params = normalize_query_params(params)
        method = normalize_string(method).upper()
        headers = {
            "x-sn-apikey": self.api_key
        }

        url = urllib.parse.urljoin(self.base_url, '/api/now/table/')
        url += normalize_string(table)

        if sys_id:
            url += f"/{normalize_string(sys_id)}"

        request_args = {
            "method": method,
            "url": url,
            "headers": headers
        }

        if query_params:
            request_args["params"] = query_params

        if body:
            request_args["json"] = json.loads(body)
        response = requests.request(**request_args)

        if response.status_code >= 300:
            raise ToolException(f"ServiceNow tool exception. Status: {response.status_code}. Response: {response.text}")

        return response.text