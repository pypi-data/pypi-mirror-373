from codemie_tools.base.models import ToolMetadata

ZEPHYR_TOOL = ToolMetadata(
    name="ZephyrScale",
    description=
    """
    Zephyr Tool that provides access to the zephyr-python-api package, enabling interaction with Zephyr test cases, 
    cycles or executions etc.
    You mist provide the following args: entity_str, method_str and body.
    1. 'entity_str': ZephyrScale entity requested by user. It must be accessible from ZephyrScale().api
    2. 'method_str': Zephyr method that is accessible from that entity. E.g. method 'get_test_cases' is accessible from ZephyrScale().api.test_cases.
        It can be equal to 'dir' so that you can list all available methods in requested entity.
    3. 'body': (Optional) Valid JSON object with parameters that must be passed to method.
    If some required information is not provided by user, try find by querying API, if not found ask user.
    If method you requested is not exists, try to execute tool with method 'dir' to get list of available methods.
    """.strip(),
    label="Zephyr Scale",
    user_description="""
    Provides access to the zephyr-python-api package, enabling interaction with Zephyr test cases, cycles or executions.
    Before using it, it is necessary to add a new integration for the tool by providing:
    1. Alias (A friendly name for the Zephyr Scale integration)
    2. Url (base url of the Zephyr Scale)
    3. Token (API access token)
    Usage Note:
    Use this tool when you need to manage Zephyr test cases, cycles or executions.
    """.strip()
)

ZEPHYR_SQUAD_TOOL = ToolMetadata(
    name="ZephyrSquad",
    description=
    """
    Zephyr SquatTool that provides access to Zephyr Squad API, enabling interaction with Zephyr test cases, 
    cycles or executions etc.
    You mist provide the following args: method, relative_path.
    1. 'method': HTTP method to be used in an API call
    2. 'relative_path': Relative path excluding base url and /public/rest/api/1.0/config/, e.x.:
    - /cycle?expand=123&cloned123CycleId=123
    - /executions/search?executionId=123
    - ...
    3. 'body': an optional JSON parameter. Must be a valid JSON
    """.strip(),
    label="Zephyr Squad",
    user_description="""
    Provides access to the Zephyr Squad Cloud API.

    Before using it, the following credentials must be obtained:
    1. Jira Account ID.

    The easiest way to retrieve the AccountID is to click on the icon on the left-hand menu and then click the Profile link.
    Within the URL, you can find your AccountID after the last “/”.
    Example: https://********.atlassian.net/people/5bb7ad0ccc53fd0760103780
    Or get from https://*****.atlassian.net/rest/api/3/myself

    2. Zephyr API Access and Secret keys, obtained via Zephyr UI in Jira
    """.strip()
)
