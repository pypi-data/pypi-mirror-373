import json
import os
from typing import Type, Optional, List, Dict, Any

from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking import TeamContext, Wiql, WorkItemTrackingClient
from msrest.authentication import BasicAuthentication
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool, logger
from codemie_tools.base.errors import InvalidCredentialsError
from codemie_tools.azure_devops.work_item.tools_vars import (
    SEARCH_WORK_ITEMS_TOOL,
    CREATE_WORK_ITEM_TOOL,
    UPDATE_WORK_ITEM_TOOL,
    GET_WORK_ITEM_TOOL,
    LINK_WORK_ITEMS_TOOL,
    GET_RELATION_TYPES_TOOL,
    GET_COMMENTS_TOOL
)

CLIENT_IS_NOT_INITIALIZED = """Azure DevOps client initialisation failed: 
Please check your Azure DevOps credentials are provided in 'Integrations'"""

# Ensure Azure DevOps cache directory is set
if not os.environ.get('AZURE_DEVOPS_CACHE_DIR', None):
    os.environ['AZURE_DEVOPS_CACHE_DIR'] = ""


# Input models for Azure DevOps work item operations
class SearchWorkItemsInput(BaseModel):
    query: str = Field(description="WIQL query for searching Azure DevOps work items")
    limit: Optional[int] = Field(
        description="Number of items to return. IMPORTANT: Tool returns all items if limit=-1. "
                    "If parameter is not provided then the value will be taken from tool configuration.",
        default=None
    )
    fields: Optional[List[str]] = Field(description="List of requested fields", default=None)


class CreateWorkItemInput(BaseModel):
    work_item_json: str = Field(description="""JSON of the work item fields to create in Azure DevOps, i.e.
                    {
                       "fields":{
                          "System.Title":"Implement Registration Form Validation",
                          "field2":"Value 2",
                       }
                    }
                    """)
    wi_type: Optional[str] = Field(
        description="Work item type, e.g. 'Task', 'Issue' or 'EPIC'",
        default="Task"
    )


class UpdateWorkItemInput(BaseModel):
    id: int = Field(description="ID of work item required to be updated")
    work_item_json: str = Field(description="""JSON of the work item fields to update in Azure DevOps, i.e.
                    {
                       "fields":{
                          "System.Title":"Updated Title",
                          "field2":"Updated Value",
                       }
                    }
                    """)


class GetWorkItemInput(BaseModel):
    id: int = Field(description="The work item id")
    fields: Optional[List[str]] = Field(description="List of requested fields", default=None)
    as_of: Optional[str] = Field(description="AsOf UTC date time string", default=None)
    expand: Optional[str] = Field(
        description="The expand parameters for work item attributes. "
                    "Possible options are { None, Relations, Fields, Links, All }.",
        default=None
    )


class LinkWorkItemsInput(BaseModel):
    source_id: int = Field(description="ID of the work item you plan to add link to")
    target_id: int = Field(description="ID of the work item linked to source one")
    link_type: str = Field(description="Link type: System.LinkTypes.Dependency-forward, etc.")
    attributes: Optional[Dict[str, Any]] = Field(
        description="Dict with attributes used for work items linking. "
                    "Example: `comment`, etc. and syntax 'comment': 'Some linking comment'",
        default=None
    )


class GetRelationTypesInput(BaseModel):
    pass


class GetCommentsInput(BaseModel):
    work_item_id: int = Field(description="The work item id")
    limit_total: Optional[int] = Field(description="Max number of total comments to return", default=None)
    include_deleted: Optional[bool] = Field(description="Specify if the deleted comments should be retrieved",
                                            default=False)
    expand: Optional[str] = Field(
        description="The expand parameters for comments. "
                    "Possible options are { all, none, reactions, renderedText, renderedTextOnly }.",
        default="none"
    )
    order: Optional[str] = Field(
        description="Order in which the comments should be returned. Possible options are { asc, desc }",
        default=None
    )


class BaseAzureDevOpsWorkItemTool(CodeMieTool):
    """Base class for Azure DevOps Work Item tools."""
    organization_url: Optional[str] = None
    project: Optional[str] = None
    token: Optional[str] = None
    limit: Optional[int] = 5
    _client: Optional[WorkItemTrackingClient] = None
    _relation_types: Dict = {}  # Track actual relation types for instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_clients()

    def _setup_clients(self):
        """Set up Azure DevOps clients."""
        if not self.organization_url or not self.token:
            logger.error("Missing required configuration for Azure DevOps: organization_url or token")
            return

        try:
            # Set up connection to Azure DevOps using Personal Access Token (PAT)
            credentials = BasicAuthentication('', self.token)
            connection = Connection(base_url=self.organization_url, creds=credentials)

            # Retrieve the work item tracking client
            self._client = connection.clients_v7_1.get_work_item_tracking_client()
        except Exception as e:
            logger.error(f"Failed to connect to Azure DevOps: {e}")
            return

    def _parse_work_items(self, work_items, fields=None):
        """Parse work items dynamically based on the fields requested."""
        parsed_items = []

        # If no specific fields are provided, default to the basic ones
        if fields is None:
            fields = ["System.Title", "System.State", "System.AssignedTo", "System.WorkItemType", "System.CreatedDate",
                      "System.ChangedDate"]

        fields = [field for field in fields if "System.Id" not in field]
        fields = [field for field in fields if "System.WorkItemType" not in field]
        for item in work_items:
            # Fetch full details of the work item, including the requested fields
            full_item = self._client.get_work_item(id=item.id, project=self.project, fields=fields)
            fields_data = full_item.fields

            # Parse the fields dynamically
            parsed_item = {"id": full_item.id, "url": f"{self.organization_url}/_workitems/edit/{full_item.id}"}

            # Iterate through the requested fields and add them to the parsed result
            for field in fields:
                parsed_item[field] = fields_data.get(field, "N/A")

            parsed_items.append(parsed_item)

        return parsed_items

    def _transform_work_item(self, work_item_json: str):
        try:
            # Convert the input JSON to a Python dictionary
            params = json.loads(work_item_json)
        except ValueError as e:
            return f"Issues during attempt to parse work_item_json: {str(e)}"

        if 'fields' not in params:
            return "The 'fields' property is missing from the work_item_json."

            # Transform the dictionary into a list of JsonPatchOperation objects
        patch_document = [
            {
                "op": "add",
                "path": f"/fields/{field}",
                "value": value
            }
            for field, value in params["fields"].items()
        ]
        return patch_document


class SearchWorkItemsTool(BaseAzureDevOpsWorkItemTool):
    """Tool to search work items in Azure DevOps using WIQL queries."""
    name: str = SEARCH_WORK_ITEMS_TOOL.name
    description: str = SEARCH_WORK_ITEMS_TOOL.description
    args_schema: Type[BaseModel] = SearchWorkItemsInput

    def execute(self, query: str, limit: Optional[int] = None, fields: Optional[List[str]] = None):
        """Search for work items using a WIQL query and dynamically fetch fields based on the query."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)

        try:
            # Create a Wiql object with the query
            wiql = Wiql(query=query)

            logger.info(f"Search for work items using {query}")
            # Execute the WIQL query
            if not limit:
                limit = self.limit
            work_items = self._client.query_by_wiql(
                wiql,
                top=None if limit and limit < 0 else limit,
                team_context=TeamContext(project=self.project)
            ).work_items

            if not work_items:
                return "No work items found."

            # Parse the work items and fetch the fields dynamically
            parsed_work_items = self._parse_work_items(work_items, fields)

            # Return the parsed work items
            return parsed_work_items
        except ValueError as ve:
            logger.error(f"Invalid WIQL query: {ve}")
            return f"Invalid WIQL query: {ve}"
        except Exception as e:
            logger.error(f"Error searching work items: {e}")
            return f"Error searching work items: {str(e)}"


class CreateWorkItemTool(BaseAzureDevOpsWorkItemTool):
    """Tool to create a work item in Azure DevOps."""
    name: str = CREATE_WORK_ITEM_TOOL.name
    description: str = CREATE_WORK_ITEM_TOOL.description
    args_schema: Type[BaseModel] = CreateWorkItemInput

    def execute(self, work_item_json: str, wi_type: str = "Task"):
        """Create a work item in Azure DevOps."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)

        try:
            patch_document = self._transform_work_item(work_item_json)
        except Exception as e:
            return f"Issues during attempt to parse work_item_json: {str(e)}"

        try:
            # Use the transformed patch_document to create the work item
            work_item = self._client.create_work_item(
                document=patch_document,
                project=self.project,
                type=wi_type
            )
            return f"Work item {work_item.id} created successfully. View it at {work_item.url}."
        except Exception as e:
            if "unknown value" in str(e):
                logger.error(f"Unable to create work item due to incorrect assignee: {e}")
                raise InvalidCredentialsError(f"Unable to create work item due to incorrect assignee: {e}")
            logger.error(f"Error creating work item: {e}")
            return f"Error creating work item: {str(e)}"


class UpdateWorkItemTool(BaseAzureDevOpsWorkItemTool):
    """Tool to update an existing work item in Azure DevOps."""
    name: str = UPDATE_WORK_ITEM_TOOL.name
    description: str = UPDATE_WORK_ITEM_TOOL.description
    args_schema: Type[BaseModel] = UpdateWorkItemInput

    def execute(self, id: int, work_item_json: str):
        """Updates existing work item per defined data"""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)

        try:
            patch_document = self._transform_work_item(work_item_json)
            work_item = self._client.update_work_item(id=id, document=patch_document, project=self.project)
        except Exception as e:
            raise InvalidCredentialsError(f"Issues during attempt to update work item: {str(e)}")
        return f"Work item ({work_item.id}) was updated."


class GetWorkItemTool(BaseAzureDevOpsWorkItemTool):
    """Tool to get a single work item by ID from Azure DevOps."""
    name: str = GET_WORK_ITEM_TOOL.name
    description: str = GET_WORK_ITEM_TOOL.description
    args_schema: Type[BaseModel] = GetWorkItemInput

    def execute(self, id: int, fields: Optional[List[str]] = None, as_of: Optional[str] = None,
                expand: Optional[str] = None):
        """Get a single work item by ID."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)

        try:
            # Fetch the work item
            work_item = self._client.get_work_item(
                id=id,
                project=self.project,
                fields=fields,
                as_of=as_of,
                expand=expand
            )

            # Parse the fields dynamically
            fields_data = work_item.fields
            parsed_item = {"id": work_item.id, "url": f"{self.organization_url}/_workitems/edit/{work_item.id}"}

            # Iterate through the requested fields and add them to the parsed result
            if fields:
                for field in fields:
                    parsed_item[field] = fields_data.get(field, "N/A")
            else:
                parsed_item.update(fields_data)

            # extract relations if any
            relations_data = work_item.relations
            if relations_data:
                parsed_item['relations'] = []
                for relation in relations_data:
                    parsed_item['relations'].append(relation.as_dict())

            return parsed_item
        except Exception as e:
            logger.error(f"Error getting work item: {e}")
            return f"Error getting work item: {str(e)}"


class LinkWorkItemsTool(BaseAzureDevOpsWorkItemTool):
    """Tool to link two work items in Azure DevOps with a specified relationship type."""
    name: str = LINK_WORK_ITEMS_TOOL.name
    description: str = LINK_WORK_ITEMS_TOOL.description
    args_schema: Type[BaseModel] = LinkWorkItemsInput

    def execute(self, source_id: int, target_id: int, link_type: str, attributes: Dict[str, Any] = None):
        """Add the relation to the source work item with an appropriate attributes if any."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)

        if not self._relation_types:
            # check cached relation types and trigger its collection if it is empty by that moment
            relation_types = self._client.get_relation_types()
            for relation in relation_types:
                self._relation_types[relation.name] = relation.reference_name

        if link_type not in self._relation_types.values():
            return (
                f"Link type is incorrect. You have to use proper "
                f"relation's reference name NOT relation's name: {self._relation_types}")

        try:
            relation = {
                "rel": link_type,
                "url": f"{self.organization_url}/_apis/wit/workItems/{target_id}"
            }

            if attributes:
                relation.update({"attributes": attributes})

            self._client.update_work_item(
                document=[
                    {
                        "op": "add",
                        "path": "/relations/-",
                        "value": relation
                    }
                ],
                id=source_id
            )
            return f"Work item {source_id} linked to {target_id} with link type {link_type}"
        except Exception as e:
            logger.error(f"Error linking work items: {e}")
            return f"Error linking work items: {str(e)}"


class GetRelationTypesTool(BaseAzureDevOpsWorkItemTool):
    """Tool to get all available relation types for work items in Azure DevOps."""
    name: str = GET_RELATION_TYPES_TOOL.name
    description: str = GET_RELATION_TYPES_TOOL.description
    args_schema: Type[BaseModel] = GetRelationTypesInput

    def execute(self):
        """Returns dict of possible relation types per syntax: 'relation name': 'relation reference name'."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)

        try:
            if not self._relation_types:
                # have to be called only once for session
                relations = self._client.get_relation_types()
                for relation in relations:
                    self._relation_types[relation.name] = relation.reference_name
            return self._relation_types
        except Exception as e:
            logger.error(f"Error getting relation types: {e}")
            return f"Error getting relation types: {str(e)}"


class GetCommentsTool(BaseAzureDevOpsWorkItemTool):
    """Tool to get comments for a work item by ID from Azure DevOps."""
    name: str = GET_COMMENTS_TOOL.name
    description: str = GET_COMMENTS_TOOL.description
    args_schema: Type[BaseModel] = GetCommentsInput

    def execute(self, work_item_id: int, limit_total: Optional[int] = None, include_deleted: Optional[bool] = None,
                expand: Optional[str] = None, order: Optional[str] = None):
        """Get comments for work item by ID."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)

        try:
            # Resolve limits to extract in single portion and for whole set of comment
            limit_portion = self.limit
            limit_all = limit_total if limit_total else self.limit

            # Fetch the work item comments
            comments_portion = self._client.get_comments(
                project=self.project,
                work_item_id=work_item_id,
                top=limit_portion,
                include_deleted=include_deleted,
                expand=expand,
                order=order
            )
            comments_all = []

            while True:
                comments_all += [comment.as_dict() for comment in comments_portion.comments]

                if not comments_portion.continuation_token or len(comments_all) >= limit_all:
                    return comments_all[:limit_all]
                else:
                    comments_portion = self._client.get_comments(
                        continuation_token=comments_portion.continuation_token,
                        project=self.project,
                        work_item_id=int(work_item_id),
                        top=3,
                        include_deleted=include_deleted,
                        expand=expand,
                        order=order
                    )
        except Exception as e:
            logger.error(f"Error getting work item comments: {e}")
            return f"Error getting work item comments: {str(e)}"
