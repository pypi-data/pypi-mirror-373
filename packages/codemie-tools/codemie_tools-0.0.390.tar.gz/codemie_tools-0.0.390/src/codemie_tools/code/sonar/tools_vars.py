from codemie_tools.base.models import ToolMetadata

SONAR_TOOL = ToolMetadata(
    name="Sonar",
    description="""
    SonarQube Tool for interacting with the SonarQube REST API
    You must provide the following args: relative_url, params
    1. 'relative_url': Required parameter. The relative URI for SONAR REST API
    URI must start with a forward slash and '/api/issues/search..'
    DO NOT include query parameters in the URL, they must be provided in 'params'
    2. 'params': Optional JSON string of parameters to be sent in query params
    Must be a valid JSON string.
    For search/read operations, include the following fields in your params:
    - "cleanCodeAttributeCategories" (consistent, intentional, adaptable, responsible)
    - "severities" (MINOR, MAJOR, INFO etc)
    - "issueStatuses" (OPEN , ACCEPTED, FIXED etc)
    - "types" (CODE_SMELL, VULNERABILITY, BUG)
    - "ps" (page size, to set maxResults)
    Do not include additional fields if they not requested by the user
    If some information is not provided by the user, attempt to use default values or ask the user for clarification
    """,
    label="Sonar",
    user_description="""The purpose of the Sonar tool is to retrieve data using the SonarQube API.
    Before using it, it is necessary to add a new integration for the tool by providing:

    1. SonarQube Server URL
    2. SonarQube user token for authentication
    3. Project name of the desired repository

    Example user query: "Show me first 10 open major code smells"
    """
)
