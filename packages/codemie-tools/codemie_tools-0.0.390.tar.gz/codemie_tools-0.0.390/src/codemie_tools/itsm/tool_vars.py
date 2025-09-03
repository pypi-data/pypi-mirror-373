from codemie_tools.base.models import ToolMetadata

SNOW_TABLE_TOOL = ToolMetadata(
    name="servicenow_table_tool",
    description="""
    ServiceNow Tool for Official ServiceNow Table REST API call, searching, creating, updating table, etc. 
    You must provide the following args: relative_url, method, params. 
    1. 'method': The HTTP method, e.g. 'GET', 'POST', 'PUT', 'DELETE' etc. Some of them might be turned off in configuration.
    2. 'table': The name of the table to work with
    3. 'sys_id': Optional, used when working with a specific record, rather than entire table. In this case the api in use
    will be /api/now/table/{tableName}/{sys_id}
    4. 'query': Optional set of query parameters to be used if supported by API. f.ex: `sysparm_query`, `sysparm_offset`, `sysparm_limit`, etc. In a form of JSON.
    """,
    label="ServiceNow Table API",
    user_description="""
    Provides access to the ServiceNow Table API.
    """.strip()
)
