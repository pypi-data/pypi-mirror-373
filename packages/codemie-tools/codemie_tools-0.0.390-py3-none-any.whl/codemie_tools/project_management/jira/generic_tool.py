import json
import logging
import re
import traceback
from json import JSONDecodeError
from typing import Type, Dict, Any, Optional, Union
import os
import io
import urllib.parse
import mimetypes

from atlassian import Jira
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.project_management.jira.tools_vars import GENERIC_JIRA_TOOL, get_jira_tool_description
from codemie_tools.project_management.jira.utils import validate_jira_creds
from codemie_tools.base.utils import clean_json_string

from codemie_tools.base.file_object import FileObject

logger = logging.getLogger(__name__)


class JiraInput(BaseModel):
    method: str = Field(
        ...,
        description="The HTTP method to use for the request (GET, POST, PUT, DELETE, etc.). Required parameter."
    )
    relative_url: str = Field(
        ...,
        description="""
        Required parameter: The relative URI for JIRA REST API V2.
        URI must start with a forward slash and '/rest/api/2/...'.
        Do not include query parameters in the URL, they must be provided separately in 'params'.
        For search/read operations, you MUST always get "key", "summary", "status", "assignee", "issuetype" and 
        set maxResult, until users ask explicitly for more fields.
        """
    )
    params: Optional[str] = Field(
        default="",
        description="""
        Optional JSON of parameters to be sent in request body or query params. MUST be string with valid JSON. 
        For search/read operations, you MUST always get "key", "summary", "status", "assignee", "issuetype" and 
        set maxResult, until users ask explicitly for more fields.
        """
    )
    file_paths: Optional[list] = Field(
        default=None,
        description="Optional list of file paths to attach to the Jira issue."
    )


def parse_payload_params(params: Optional[str]) -> Dict[str, Any]:
    if params:
        try:
            return json.loads(clean_json_string(params))
        except JSONDecodeError:
            stacktrace = traceback.format_exc()
            logger.error(f"Jira tool: Error parsing payload params: {stacktrace}")
            raise ToolException(f"JIRA tool exception. Passed 'params' string is not valid to transform to vaild JSON. {stacktrace}. Please correct and send again.")
    return {}


def get_issue_field(issue, field, default=None):
    field_value = issue.get("fields", {}).get(field, default)
    # Additional verification. In some cases key is present, but value is None. Need to return default value
    return field_value if field_value else default


def get_additional_fields(issue, additional_fields):
    additional_data = {}
    for field in additional_fields:
        if field not in additional_data:  # Avoid overwriting any main fields
            additional_data[field] = get_issue_field(issue, field)
    return additional_data


def process_issue(jira_base_url, issue, payload_params: Dict[str, Any] = None):
    issue_key = issue.get('key')
    jira_link = f"{jira_base_url}/browse/{issue_key}"

    parsed_issue = {
        "key": issue_key,
        "url": jira_link,
        "summary": get_issue_field(issue, "summary", ""),
        "assignee": get_issue_field(issue, "assignee", {}).get("displayName", "None"),
        "status": get_issue_field(issue, "status", {}).get("name", ""),
        "issuetype": get_issue_field(issue, "issuetype", {}).get("name", "")
    }

    process_payload(issue, payload_params, parsed_issue)
    return parsed_issue


def process_payload(issue, payload_params, parsed_issue):
    fields_list = extract_fields_list(payload_params)

    if fields_list:
        update_parsed_issue_with_additional_data(issue, fields_list, parsed_issue)


def extract_fields_list(payload_params):
    if payload_params and 'fields' in payload_params:
        fields = payload_params['fields']
        if isinstance(fields, str) and fields.strip():
            return [field.strip() for field in fields.split(",")]
        elif isinstance(fields, list) and fields:
            return fields
    return []


def update_parsed_issue_with_additional_data(issue, fields_list, parsed_issue):
    additional_data = get_additional_fields(issue, fields_list)
    for field, value in additional_data.items():
        if field not in parsed_issue and value:
            parsed_issue[field] = value


def process_search_response(jira_url, response, payload_params: Dict[str, Any] = None):
    if response.status_code != 200:
        return response.text

    processed_issues = []
    json_response = response.json()

    for issue in json_response.get('issues', []):
        processed_issues.append(process_issue(jira_url, issue, payload_params))

    return f"Issues: {processed_issues}", f"Total: {json_response.get('total', 0)}"


class GenericJiraIssueTool(CodeMieTool):
    jira: Jira
    name: str = GENERIC_JIRA_TOOL.name
    description: str = GENERIC_JIRA_TOOL.description or ""
    args_schema: Type[BaseModel] = JiraInput
    # Regular expression to match /rest/api/[any number]/search
    issue_search_pattern: str = r'/rest/api/\d+/search'
    file_object: Optional[FileObject] = None


    def execute(self, method: str, relative_url: str, params: Optional[str] = "", file_paths: list | None = None, *args):
        validate_jira_creds(self.jira)
        payload_params = parse_payload_params(params)

        if method == "GET":
            response_text, response = self._handle_get_request(relative_url, payload_params)
        else:
            response_text, response = self._handle_non_get_request(method, relative_url, payload_params, file_paths)

        response_string = f"HTTP: {method} {relative_url} -> {response.status_code} {response.reason} {response_text}"
        logger.debug(response_string)
        return response_string

    def _handle_get_request(self, relative_url, payload_params):
        response = self.jira.request(
            method="GET",
            path=relative_url,
            params=payload_params,
            advanced_mode=True,
            headers={"content-type": "application/json"},
        )
        self.jira.raise_for_status(response)
        if re.match(self.issue_search_pattern, relative_url):
            response_text = process_search_response(self.jira.url, response, payload_params)
        else:
            response_text = response.text
        return response_text, response

    def _handle_attachment_upload(self, method, relative_url, file_paths):
        """
        Handles uploading attachments to a Jira issue.
        """
        match = re.match(r"^/rest/api/\d+/issue/([^/]+)/attachments$", relative_url)
        if not match:
            logger.error(f"Could not extract issue key from URL: {relative_url}")
            raise ToolException("Invalid attachment URL format; cannot extract issue key.")
        issue_key = match.group(1)

        try:
            response_text, response = self._handle_file_attachments(issue_key, file_paths)
            
            response_text = f"Attachment(s) uploaded to {issue_key}"
            logger.info(response_text)
            return response_text, response
        except Exception as e:
            logger.error(f"Failed to upload attachment(s) to {issue_key}: {e}")
            raise ToolException(f"Failed to upload attachment(s) to {issue_key}: {e}")

    def _is_attachment_upload_request(self, method, relative_url, file_paths):
        """
        Returns True if the request is a POST to the Jira attachments endpoint and file_paths are provided.
        """
        return (
            method.upper() == "POST"
            and re.match(r"^/rest/api/\d+/issue/[^/]+/attachments$", relative_url)
            and file_paths
        )

    def _handle_non_get_request(self, method, relative_url, payload_params, file_paths):
        if self._is_attachment_upload_request(method, relative_url, file_paths):
            return self._handle_attachment_upload(method, relative_url, file_paths)

        response = self.jira.request(
            method=method,
            path=relative_url,
            data=payload_params,
            advanced_mode=True
        )
        self.jira.raise_for_status(response)
        response_text = response.text

        issue_key = self._get_issue_key(response_text)
        if issue_key and file_paths:
            self._handle_file_attachments(issue_key, file_paths)
        return response_text, response

    def _get_issue_key(self, response_text):
        try:
            data = json.loads(clean_json_string(response_text))
            return data.get("key") if isinstance(data, dict) else None
        except JSONDecodeError:
            return None

    def _handle_file_attachments(self, issue_key, file_paths):
        
        if not issue_key:
            raise ToolException("Issue key must be provided in params for file attachment.")
        if self.file_object:
            return self.attach_attachment_bytes(issue_key, file_paths)
        return self.attach_files(issue_key, file_paths)

    def post_attachments(self, issue_key: str, file_tuples: list)-> tuple:
        """
        Uploads file attachments to a Jira issue.

        This method sends a POST request to the Jira API to attach files to the specified issue.

        Parameters:
            issue_key (str): The key of the Jira issue to which the files will be attached.
            file_tuples (list): A list of file tuples to be uploaded. Each tuple should be in the format:
                ("file", (filename, file_content, mime_type)).

        Behavior:
            1. Constructs the API endpoint for attaching files using the issue key.
            2. Adds the required header `X-Atlassian-Token: no-check` to bypass CSRF checks.
            3. Sends a POST request with the file data to the Jira server.
            4. Logs a success message if the files are attached successfully.
            5. Logs an error message if the attachment fails.

        Raises:
            None: Errors are logged but not raised.

        Example:
            file_tuples = [
                ("file", ("example.txt", io.BytesIO(b"File content"), "text/plain"))
            ]
            jira_tool.post_attachments("ISSUE-123", file_tuples)
        """
        post_path = f"/rest/api/2/issue/{issue_key}/attachments"
        post_response = self.jira.request(
            method="POST",
            path=post_path,
            headers=self.jira.no_check_headers,
            files=file_tuples
        )
        response_text = f"Successfully attached files to {issue_key}"
        if post_response.status_code not in (200, 201):
            response_text = f"Failed to attach files: {post_response.status_code} - {post_response.text}"

        logger.info(response_text)
        return response_text, post_response    

    def attach_attachment_bytes(self, issue_key: str, file_paths: list) -> tuple:
        """
        Attaches a single file (in bytes) to a Jira issue.

        This method is used to attach a file represented as a byte stream to a Jira issue. It uses the
        `post_attachments` method to upload the file.

        Parameters:
            issue_key (str): The key of the Jira issue to which the file will be attached.
            file_paths (list): A list of file paths. Only the first file path is used to extract the filename.

        Behavior:
            1. Extracts the filename from the first file path in the list (if provided).
            2. Checks if the `file_object` attribute is set. If not, raises a `ValueError`.
            3. Prepares a file tuple with the filename, file content (from `file_object`), and MIME type.
            4. Calls `post_attachments` to upload the file to the Jira issue.

        Raises:
            ValueError: If `file_object` is not set.

        Example:
            jira_tool.file_object = SomeFileObject(content=b"File content")
            jira_tool.attach_attachment_bytes("ISSUE-123", ["example.txt"])
        """
        file_name = "attachment.bin"
        if file_paths and len(file_paths) > 0:
            # Extract the filename from the first file path
            file_name = self.__extract_file_details(file_paths[0])[0]

        if self.file_object is None or self.file_object.content is None:
            # Raise an error if the file content is not provided
            raise ValueError("attachment_bytes cannot be None when attaching files.")
        
        # Prepare the file tuple for attachment
        file_tuple = (
            "file", 
            (file_name, io.BytesIO(self.file_object.content), "application/octet-stream")
        )
        # Upload the file to the Jira issue
        return self.post_attachments(issue_key, [file_tuple])

    

    def prepare_file_attachment(self, file_item: Union[str, dict]) -> tuple:
        """
        Prepares a file for attachment to a Jira issue.

        This method handles both local and remote files. If the file is remote, it fetches the file content
        from the Jira server and prepares it for upload.

        Parameters:
            file_item (Union[str, dict]): The file to be prepared. This can be:
                - A string representing the file URL.
                - A dictionary containing:
                    - "url" (str): The URL of the file.
                    - "name" (optional, str): The name of the file.

        Returns:
            tuple: A tuple containing:
                - filename (str): The name of the file.
                - file_source (io.BytesIO): The file content as a byte stream.
                - mime_type (str): The MIME type of the file, defaulting to 'application/octet-stream'.

        Raises:
            ToolException: If the file details cannot be extracted or the file cannot be fetched.

        Behavior:
            1. Extracts the file name and URL using the `extract_file_details` method.
            2. Logs an informational message if the file is being fetched from a remote URL.
            3. Converts the full file URL into a relative path using the `__get_relative_file_path` method.
            4. Sends a GET request to the Jira server to fetch the file content.
            5. Raises an exception if the request fails.
            6. If the filename is not provided, extracts it from the file URL.
            7. Returns the filename, file content as a byte stream, and the MIME type.

        Example:
            file_item = "https://jira.example.com/secure/attachment/12345/sample.txt"
            filename, file_source, mime_type = jira_tool.prepare_file_attachment(file_item)

            print(f"Filename: {filename}")
            print(f"MIME Type: {mime_type}")
            print(f"File Content: {file_source.read()}")
        """
        filename, file_url = self.__extract_file_details(file_item)

        logger.info(f"Local file not found; trying remote file at: {file_url}")
        relative_file_path = self.__get_relative_file_path(file_url)

        response = self.jira.request(
            method="GET",
            path=relative_file_path,
            headers=self.jira.no_check_headers
        )
        self.jira.raise_for_status(response)
        file_source = io.BytesIO(response.content)
        if not filename:
            filename = os.path.basename(urllib.parse.urlparse(file_url).path)

        return filename, file_source, 'application/octet-stream'

    

    def attach_files(self, issue_key: str, file_paths: list) -> tuple:
        """
        Attaches multiple files to a Jira issue.

        This method processes a list of file paths or file descriptors, prepares them for attachment,
        and uploads them to the specified Jira issue.

        Parameters:
            issue_key (str): The key of the Jira issue to which the files will be attached.
            file_paths (list): A list of file paths or file descriptors to be attached. Each item can be:
                - A string representing the file URL.
                - A dictionary containing:
                    - "url" (str): The URL of the file.
                    - "name" (optional, str): The name of the file.

        Behavior:
            1. Initializes an empty list `file_tuples` to store prepared file data.
            2. Iterates over the `file_paths` list:
                - Calls `prepare_file_attachment` to process each file.
                - Appends the prepared file data (filename, file content, MIME type) to `file_tuples`.
                - Logs an error if an exception occurs during file preparation.
            3. If there are prepared files in `file_tuples`, calls `post_attachments` to upload them to the Jira issue.

        Raises:
            Exception: Logs any exceptions encountered during file preparation but does not raise them further.

        Example:
            file_paths = [
                "https://jira.example.com/secure/attachment/12345/sample.txt",
                {"url": "https://jira.example.com/secure/attachment/67890/image.png", "name": "custom_name.png"}
            ]
            jira_tool.attach_files("ISSUE-123", file_paths)

        Notes:
            - This method relies on `prepare_file_attachment` to handle file preparation.
            - The `post_attachments` method is used to upload the files to Jira.
        """
        file_tuples = []  # List of tuples structured as: ("file", (filename, file_source, mime))
        for file_item in file_paths:
            try:
                # Prepare the file for attachment
                filename, file_source, mime = self.prepare_file_attachment(file_item)
                # Add the prepared file to the list
                file_tuples.append(("file", (filename, file_source, mime)))
            except Exception as e:
                # Log any errors encountered during file preparation
                logger.error(f"Exception while preparing file {file_item}: {e}")
        # If there are files to attach, upload them to the Jira issue
        if file_tuples:
            response_text, response = self.post_attachments(issue_key, file_tuples)
            return response_text, response
        return "No files to attach", None

    def __extract_file_details(self, file_item):
        """
        Extracts the file name and URL from the provided file item.

        This method handles both string and dictionary inputs to retrieve the file details.
        If the input is a dictionary, it expects a "url" key and optionally a "name" key.
        If the input is a string, it is treated as the file URL.

        Parameters:
            file_item (Union[str, dict]): The file item to extract details from. This can be:
                - A string representing the file URL.
                - A dictionary containing:
                    - "url" (str): The URL of the file.
                    - "name" (optional, str): The name of the file.

        Returns:
            tuple: A tuple containing:
                - filename (str): The name of the file.
                - file_url (str): The URL of the file.

        Raises:
            ToolException: If the file item is invalid or missing required keys.

        Example:
            file_item = {"url": "https://example.com/file.txt", "name": "custom_name.txt"}
            filename, file_url = self.__extract_file_details(file_item)
            print(filename)  # Output: custom_name.txt
            print(file_url)  # Output: https://example.com/file.txt
        """
        if isinstance(file_item, dict):
            file_url = file_item.get("url")
            if not file_url:
                raise ToolException("Dict file item missing 'url'.")
            # Use the provided name or extract it from the URL
            filename = file_item.get("name") or os.path.basename(urllib.parse.urlparse(file_url).path)
        elif isinstance(file_item, str):
            # If the input is a string, treat it as the file URL
            file_url = file_item
            filename = os.path.basename(file_url)
        else:
            raise ToolException("Invalid file item type; expected string or dict.")
        return filename, file_url


    def __get_relative_file_path(self, file_url: str) -> str:
        """
        Converts a full file URL into a relative path for Jira API requests.

        This method checks if the file URL starts with the Jira base URL. If it does,
        the base URL is stripped to create a relative path. If not, the original URL
        is returned as the relative path.

        Parameters:
            file_url (str): The full URL of the file.

        Returns:
            str: The relative file path to be used in Jira API requests.

        Example:
            jira_url = "https://jira.example.com"
            file_url = "https://jira.example.com/secure/attachment/12345/file.txt"
            relative_path = self.__get_relative_file_path(file_url)
            print(relative_path)  # Output: /secure/attachment/12345/file.txt
        """
        if file_url.startswith(self.jira.url):
            # Strip the Jira base URL to create a relative path
            relative_file_path = file_url[len(self.jira.url):]
            # Ensure the relative path starts with a forward slash
            if not relative_file_path.startswith("/"):
                relative_file_path = "/" + relative_file_path
        else:
            # If the URL does not start with the Jira base URL, return it as is
            relative_file_path = file_url
        return relative_file_path
    

class GenericJiraCloudIssueTool(GenericJiraIssueTool):
    issue_search_pattern: str = r'/rest/api/3/search/jql'
    description: str = get_jira_tool_description(api_version=3) or ""
