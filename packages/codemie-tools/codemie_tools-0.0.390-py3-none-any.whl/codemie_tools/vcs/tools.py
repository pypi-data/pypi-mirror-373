import json
import logging
import base64
import functools
import math
from typing import Type, Optional, Any, Union

import requests
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.vcs.tools_vars import GITHUB_TOOL, GITLAB_TOOL

logger = logging.getLogger(__name__)

# VCS Tool Constants
PROTECTED_HEADERS = frozenset({'authorization'})

# Default headers for different VCS providers
GITHUB_DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json"
}

GITLAB_DEFAULT_HEADERS = {
    "Accept": "application/json"
}


def _merge_custom_headers(custom_headers: dict[str, str]) -> dict[str, str]:
    """
    Merge custom headers while protecting critical authentication headers.

    Args:
        custom_headers: Dictionary of custom headers to merge

    Returns:
        Dictionary of validated custom headers

    Raises:
        None - Protected headers are silently ignored with warning
    """
    if not custom_headers:
        return {}

    merged_headers = {}

    for header_name, header_value in custom_headers.items():
        if header_name.lower() in PROTECTED_HEADERS:
            logger.warning(f"Attempted to override protected header '{header_name}' - ignoring")
            continue

        merged_headers[header_name] = header_value
        logger.debug(f"Added custom header: {header_name}")

    return merged_headers


def _validate_custom_headers(custom_headers: Optional[dict[str, str]]) -> None:
    """
    Validate custom headers for security compliance.

    Args:
        custom_headers: Dictionary of headers to validate

    Raises:
        ValueError: If protected headers are attempted to be overridden
    """
    if not custom_headers:
        return

    for header_name in custom_headers.keys():
        if header_name.lower() in PROTECTED_HEADERS:
            raise ValueError(f"Cannot override protected header: {header_name}")


def _build_headers(default_headers: dict[str, str], access_token: str,
                   custom_headers: Optional[dict[str, str]] = None) -> dict[str, str]:
    """
    Build request headers with optional custom headers.

    Args:
        custom_headers: Optional custom headers to merge

    Returns:
        Complete headers dictionary for the request
    """
    headers = default_headers.copy()
    headers["Authorization"] = f"Bearer {access_token}"

    if custom_headers:
        headers.update(_merge_custom_headers(custom_headers))

    return headers


class VcsInput(BaseModel):
    query: Union[str, dict[str, Any]] = Field(description="""
        JSON containing the GitHub API request specification. Must be valid JSON with no comments allowed.

        Required JSON structure:
        {
            "method": "GET|POST|PUT|DELETE|PATCH",
            "url": "https://api.github.com/...",
            "method_arguments": {request_parameters_or_body_data}
        }

        Optional with custom headers:
        {
            "method": "GET|POST|PUT|DELETE|PATCH",
            "url": "https://api.github.com/...", 
            "method_arguments": {request_parameters_or_body_data},
            "custom_headers": {additional_http_headers}
        }

        Field Requirements:
        - method: HTTP method (GET, POST, PUT, DELETE, PATCH) - REQUIRED
        - url: Complete GitHub API URL starting with "https://api.github.com" - REQUIRED
        - method_arguments: Object with request data (query params, body data, etc.) - REQUIRED (can be empty {})
        - custom_headers: Optional dictionary of additional HTTP headers - OPTIONAL

        Important Notes:
        - GitHub Personal Access Token is automatically added to Authorization header
        - custom_headers cannot override authorization headers (protected for security)
        - All request data goes in method_arguments regardless of HTTP method
        - Response will be raw JSON from GitHub API with automatic Base64 file decoding
        - The entire query must pass json.loads() validation

        Examples:
        Get user: {"method": "GET", "url": "https://api.github.com/user", "method_arguments": {}}
        Get repo file: {"method": "GET", "url": "https://api.github.com/repos/owner/repo/contents/file.py", "method_arguments": {}}
        Create issue: {"method": "POST", "url": "https://api.github.com/repos/owner/repo/issues", "method_arguments": {"title": "Bug", "body": "Description"}}
        """
                       )


def file_response_handler(execute_method):
    """
    Decorator to handle responses and only decode Base64-encoded file content.
    Why Calculate Size as `original_size * 1/4`:
    -------------------------------------------
    After decoding Base64, the original content is processed for tokenization. Base64 inflates
    file size by 4/3 (33% larger), so decoding reduces it back to 3/4 of the encoded size.
    To estimate the tokenization size, further adjustments on calculation is required 1/3 and depends on the
    encoding logic (e.g., tiktoken). This calculation ensures efficient handling of large files
    while respecting tokenization limits.

    """

    @functools.wraps(execute_method)
    def wrapper(*args, **kwargs):
        tool_instance = args[0]
        # Execute the original execute method
        response = execute_method(*args, **kwargs)

        if not isinstance(response, dict) or response.get("type") != "file":
            return response  # Return the original response if not a file

        original_size = response.get("size", 0)
        encoding = response.get("encoding", None)

        if encoding != "base64":
            logger.info("File encoding is not Base64. No decoding performed.")
            return response

        # Estimate Base64-encoded size and check against the limit
        estimated_encoded_size = math.floor(original_size * 1 / 4)
        if estimated_encoded_size > tool_instance.tokens_size_limit:
            msg = ("File too large for Base64 decoding. "
                   f"Estimated Base64 size: {estimated_encoded_size} tokens, limit: {tool_instance.tokens_size_limit}.")
            logger.warning(msg)
            response["error"] = msg

            return response

        # Attempt to decode the Base64 content
        try:
            if response.get("content"):
                decoded_content = base64.b64decode(response["content"]).decode("utf-8")
                response["content"] = decoded_content  # Replace encoded content with decoded content
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode Base64 content: {e}")
            response["error"] = "Failed to decode Base64 content: Invalid UTF-8 encoding"
        except Exception as e:
            logger.error(f"Failed to decode Base64 content: {e}")
            response["error"] = "Failed to decode Base64 content: Incorrect padding"

        return response

    return wrapper


class GithubTool(CodeMieTool):
    name: str = GITHUB_TOOL.name
    description: str = GITHUB_TOOL.description
    args_schema: Type[BaseModel] = VcsInput
    access_token: Optional[str] = None

    # High value to support large source files.
    tokens_size_limit: int = 70_000

    @file_response_handler
    def execute(self, query: Union[str, dict[str, Any]], *args):
        """
        Execute GitHub API request with optional custom headers.

        Args:
            query: JSON containing request details

        Returns:
            JSON response from GitHub API

        Raises:
            ToolException: If credentials are missing or request fails
        """
        if not self.access_token:
            logger.error("No Git credentials found for this repository")
            raise ToolException("No Git credentials found for repository. Provide Git credentials in 'User Settings'")

        try:
            if isinstance(query, str):
                query = json.loads(query)
        except json.JSONDecodeError as e:
            raise ValueError(f"Query must be a JSON string: {e}")

        custom_headers = query.get('custom_headers')
        headers = _build_headers(GITHUB_DEFAULT_HEADERS, self.access_token, custom_headers)

        return requests.request(
            method=query.get('method'),
            url=query.get('url'),
            headers=headers,
            data=json.dumps(query.get('method_arguments'))
        ).json()


class GitlabInput(VcsInput):
    query: Union[str, dict[str, Any]] = Field(description="""
        JSON containing the GitLab API request specification. Must be valid JSON with no comments allowed.

        Required JSON structure:
        {
            "method": "GET|POST|PUT|DELETE|PATCH",
            "url": "/api/v4/...",
            "method_arguments": {request_parameters_or_body_data}
        }

        Optional with custom headers:
        {
            "method": "GET|POST|PUT|DELETE|PATCH",
            "url": "/api/v4/...", 
            "method_arguments": {request_parameters_or_body_data},
            "custom_headers": {additional_http_headers}
        }

        Field Requirements:
        - method: HTTP method (GET, POST, PUT, DELETE, PATCH) - REQUIRED
        - url: GitLab API endpoint starting with "/api/v4/" (relative to GitLab server) - REQUIRED
        - method_arguments: Object with request data - REQUIRED (can be empty {})
        - custom_headers: Optional dictionary of additional HTTP headers - OPTIONAL

        Important Notes:
        - GitLab Personal Access Token is automatically added to Authorization header
        - custom_headers cannot override authorization headers (protected for security)
        - GET requests: method_arguments sent as query parameters
        - POST/PUT/DELETE/PATCH requests: method_arguments sent as request body data
        - Response is formatted string: "HTTP: {method} {url} -> {status} {reason} {body}"
        - The entire query must pass json.loads() validation

        Examples:
        Get user: {"method": "GET", "url": "/api/v4/user", "method_arguments": {}}
        List issues: {"method": "GET", "url": "/api/v4/projects/123/issues", "method_arguments": {"state": "opened"}}
        Create MR: {"method": "POST", "url": "/api/v4/projects/123/merge_requests", "method_arguments": {"source_branch": "feature", "target_branch": "main", "title": "New feature"}}
        """
                       )


class GitlabTool(CodeMieTool):
    name: str = GITLAB_TOOL.name
    args_schema: Type[BaseModel] = GitlabInput
    base_url: Optional[str] = None
    access_token: Optional[str] = None
    description: str = GITLAB_TOOL.description

    def _make_request(self, method: str, url: str, headers: dict[str, str],
                      method_arguments: dict) -> requests.Response:
        """
        Make HTTP request with appropriate parameters based on method.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            method_arguments: Request parameters/data

        Returns:
            Response object
        """
        if method == "GET":
            return requests.request(method=method, url=url, headers=headers, params=method_arguments)
        else:
            return requests.request(method=method, url=url, headers=headers, data=method_arguments)

    def execute(self, query: Union[str, dict[str, Any]], *args) -> str:
        """
        Execute GitLab API request with optional custom headers.

        Args:
            query: JSON containing request details
            *args: Additional arguments

        Returns:
            String response from GitLab API

        Raises:
            ToolException: If credentials are missing or request fails
        """
        if not self.access_token:
            logger.error("No Git credentials found for this repository")
            raise ToolException("No Git credentials found for repository. Provide Git credentials in 'User Settings'")

        try:
            if isinstance(query, str):
                query = json.loads(query)
        except json.JSONDecodeError as e:
            raise ValueError(f"Query must be a JSON string: {e}")

        try:
            method = query.get('method')
            url = f"{self.base_url}/{query.get('url')}"
            method_arguments = query.get("method_arguments", {})

            custom_headers = query.get('custom_headers')
            headers = _build_headers(GITLAB_DEFAULT_HEADERS, self.access_token, custom_headers)
            response = self._make_request(method, url, headers, method_arguments)

            response_string = f"HTTP: {method} {url} -> {response.status_code} {response.reason} {response.text}"
            logger.debug(response_string)
            return response_string

        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse GitLab response: {e}")
            raise ToolException(f"Failed to parse GitLab response: {e}")