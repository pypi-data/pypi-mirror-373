from codemie_tools.base.models import ToolMetadata

GENERIC_CONFLUENCE_TOOL = ToolMetadata(
    name="generic_confluence_tool",
    description="""
    Confluence Tool for Official Atlassian Confluence REST API to call, searching, creating, updating pages, etc. 
    You must provide the following args: relative_url, method, params. 
    1. 'method': The HTTP method, e.g. 'GET', 'POST', 'PUT', 'DELETE' etc.
    2. 'relative_url': Required relative URI of the CONFLUENCE API to call. URI must start with a forward slash and '/rest/api/content/...'.
    Do not include query parameters in the URL, they must be provided separately in 'params'.
    3. 'params': Optional of parameters to be sent in request body or query params.
    For search/read operations, you MUST get minimum required fields only, until users ask explicitly for more fields.
    If some required information is not provided by user, try find by querying API, if not found ask user.
    For updating status for issues you MUST get available statuses for issue first, compare with user input and after 
    that proceed if you can.
    """,
    label="Generic Confluence",
    user_description="""
    Provides access to the Confluence API, enabling interaction with Confluence spaces, pages, and content. This tool allows the AI assistant to perform various operations related to creating, updating, and retrieving information from Confluence, supporting both Confluence Server and Confluence Cloud environments.
    Before using it, it is necessary to add a new integration for the tool by providing:
    1. Alias (A friendly name for the Confluence integration)
    2. URL (Confluence instance URL)
    3. Username/email for Confluence (Required for Confluence Cloud)
    4. Token/ApiKey (Personal Access Token or API Key)
    Usage Note:
    Use this tool when you need to manage Confluence spaces, create or update pages, retrieve content, or perform other documentation-related tasks within Confluence.
    """.strip()
)
