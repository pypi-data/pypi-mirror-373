from codemie_tools.base.models import ToolMetadata


KEYCLOAK_TOOL = ToolMetadata(
    name="keycloak",
    description="""
    Keycloak Tool for Latest Keycloak Admin API. 
    Useful for working with Keycloak: e.g. getting, creating, updating, deleting users, etc.
    You must provide the following args: 
    1. Required relative URL of the Keycloak Admin API to call, e.g. '/users';
    2. The HTTP method, e.g. 'GET', 'POST', 'PUT', 'DELETE' etc;
    3. Optional dictionary of parameters to be sent in the request body.
    4. In case of GET method, you MUST include query parameters in the URL.
    """.strip(),
    label="Keycloak",
    user_description="""
    Provides access to the Keycloak Admin API, enabling management and interaction with Keycloak identity and access management services. This tool allows the AI assistant to perform various operations related to user management, authentication, and authorization within Keycloak.
    Before using it, it is necessary to add a new integration for the tool by providing:
    1. Alias (A friendly name for the Keycloak integration)
    2. Keycloak Server URL
    3. Keycloak Realm
    4. Keycloak Client ID
    5. Keycloak Client Secret
    Usage Note:
    Use this tool when you need to manage users, roles, clients, or perform other identity and access management tasks within Keycloak.
    """.strip(),
)
