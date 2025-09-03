from codemie_tools.base.models import ToolMetadata

SEARCH_WORK_ITEMS_TOOL = ToolMetadata(
    name="search_work_items",
    description="""
        Search for work items using a WIQL query and dynamically fetch fields based on the query.
        
        Arguments:
        - query (str): WIQL query for searching Azure DevOps work items
        - limit (int, optional): Number of items to return. If -1, all items are returned. If not provided, uses default limit.
        - fields (list[str], optional): List of requested fields
        """,
    label="Search Work Items",
    user_description="""
        Searches for work items in Azure DevOps using a WIQL (Work Item Query Language) query.
        Returns work items matching the query criteria with specified fields.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

CREATE_WORK_ITEM_TOOL = ToolMetadata(
    name="create_work_item",
    description="""
        Create a work item in Azure DevOps.
        
        Arguments:
        - work_item_json (str): JSON of the work item fields to create in Azure DevOps, i.e.
                                {
                                   "fields":{
                                      "System.Title":"Implement Registration Form Validation",
                                      "field2":"Value 2",
                                   }
                                }
        - wi_type (str, optional): Work item type, e.g. 'Task', 'Issue' or 'EPIC'. Default is "Task"
        """,
    label="Create Work Item",
    user_description="""
        Creates a new work item in Azure DevOps with the specified fields and work item type.
        The tool returns a confirmation message with the ID and URL of the created work item.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

UPDATE_WORK_ITEM_TOOL = ToolMetadata(
    name="update_work_item",
    description="""
        Updates existing work item per defined data
        
        Arguments:
        - id (str): ID of work item required to be updated
        - work_item_json (str): JSON of the work item fields to update in Azure DevOps, i.e.
                                {
                                   "fields":{
                                      "System.Title":"Updated Title",
                                      "field2":"Updated Value",
                                   }
                                }
        """,
    label="Update Work Item",
    user_description="""
        Updates an existing work item in Azure DevOps with the specified fields.
        The tool returns a confirmation message with the ID of the updated work item.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

GET_WORK_ITEM_TOOL = ToolMetadata(
    name="get_work_item",
    description="""
        Get a single work item by ID.
        
        Arguments:
        - id (int): The work item ID
        - fields (list[str], optional): List of requested fields
        - as_of (str, optional): AsOf UTC date time string
        - expand (str, optional): The expand parameters for work item attributes. 
                                  Possible options are { None, Relations, Fields, Links, All }.
        """,
    label="Get Work Item",
    user_description="""
        Retrieves a single work item from Azure DevOps by its ID.
        Returns the work item details including requested fields and relations if specified.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

LINK_WORK_ITEMS_TOOL = ToolMetadata(
    name="link_work_items",
    description="""
        Add the relation to the source work item with an appropriate attributes if any.
        
        Arguments:
        - source_id (int): ID of the work item you plan to add link to
        - target_id (int): ID of the work item linked to source one
        - link_type (str): Link type: System.LinkTypes.Dependency-forward, etc.
        - attributes (dict, optional): Dict with attributes used for work items linking. 
                                       Example: 'comment': 'Some linking comment'
        """,
    label="Link Work Items",
    user_description="""
        Creates a link between two work items in Azure DevOps.
        The tool establishes a relationship between a source and target work item with the specified link type.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

GET_RELATION_TYPES_TOOL = ToolMetadata(
    name="get_relation_types",
    description="""
        Returns dict of possible relation types per syntax: 'relation name': 'relation reference name'.
        NOTE: reference name is used for adding links to the work item
        """,
    label="Get Relation Types",
    user_description="""
        Retrieves all available relation types that can be used to link work items in Azure DevOps.
        Returns a dictionary mapping relation names to their reference names.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

GET_COMMENTS_TOOL = ToolMetadata(
    name="get_comments",
    description="""
        Get comments for work item by ID.
        
        Arguments:
        - work_item_id (int): The work item ID
        - limit_total (int, optional): Max number of total comments to return
        - include_deleted (bool, optional): Specify if the deleted comments should be retrieved
        - expand (str, optional): The expand parameters for comments. 
                                  Possible options are { all, none, reactions, renderedText, renderedTextOnly }.
        - order (str, optional): Order in which the comments should be returned. Possible options are { asc, desc }
        """,
    label="Get Comments",
    user_description="""
        Retrieves comments for a specific work item in Azure DevOps.
        Returns a list of comments with their details based on the specified parameters.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)
