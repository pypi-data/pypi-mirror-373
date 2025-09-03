import os
from typing import Type, Optional

from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from azure.devops.v7_0.core import CoreClient
from azure.devops.v7_0.wiki import WikiClient, WikiPageCreateOrUpdateParameters, WikiCreateParametersV2, \
    WikiPageMoveParameters, WikiV2
from azure.devops.v7_0.wiki.models import GitVersionDescriptor
from msrest.authentication import BasicAuthentication
from pydantic import BaseModel, Field

from codemie_tools.azure_devops.wiki.tools_vars import (
    GET_WIKI_TOOL,
    GET_WIKI_PAGE_BY_PATH_TOOL,
    GET_WIKI_PAGE_BY_ID_TOOL,
    DELETE_PAGE_BY_PATH_TOOL,
    DELETE_PAGE_BY_ID_TOOL,
    MODIFY_WIKI_PAGE_TOOL,
    RENAME_WIKI_PAGE_TOOL
)
from codemie_tools.base.codemie_tool import CodeMieTool, logger
from codemie_tools.base.errors import InvalidCredentialsError

WIKI_ID_OR_WIKI_NAME = "Wiki ID or wiki name"

CLIENT_IS_NOT_INITIALIZED = """Azure DevOps client initialisation failed: 
Please check your Azure DevOps credentials are provided in 'Integrations'"""

# Ensure Azure DevOps cache directory is set
if not os.environ.get('AZURE_DEVOPS_CACHE_DIR', None):
    os.environ['AZURE_DEVOPS_CACHE_DIR'] = ""


class GetWikiInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_ID_OR_WIKI_NAME)


class GetPageByPathInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_ID_OR_WIKI_NAME)
    page_name: str = Field(description="Wiki page path")


class GetPageByIdInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_ID_OR_WIKI_NAME)
    page_id: int = Field(description="Wiki page ID")


class ModifyPageInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_ID_OR_WIKI_NAME)
    page_name: str = Field(description="Wiki page name")
    page_content: str = Field(description="Wiki page content")
    version_identifier: str = Field(description="Version string identifier (name of tag/branch, SHA1 of commit)")
    version_type: Optional[str] = Field(
        description="Version type (branch, tag, or commit). Determines how Id is interpreted", 
        default="branch"
    )


class RenamePageInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_ID_OR_WIKI_NAME)
    old_page_name: str = Field(
        description="Old Wiki page name to be renamed", 
        examples=["/TestPageName"]
    )
    new_page_name: str = Field(
        description="New Wiki page name", 
        examples=["/RenamedName"]
    )
    version_identifier: str = Field(description="Version string identifier (name of tag/branch, SHA1 of commit)")
    version_type: Optional[str] = Field(
        description="Version type (branch, tag, or commit). Determines how Id is interpreted", 
        default="branch"
    )


class BaseAzureDevOpsWikiTool(CodeMieTool):
    """Base class for Azure DevOps Wiki tools."""
    organization_url: Optional[str] = None
    project: Optional[str] = None
    token: Optional[str] = None
    _client: Optional[WikiClient] = None
    _core_client: Optional[CoreClient] = None

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
            # Retrieve the wiki client and core client
            self._client = connection.clients.get_wiki_client()
            self._core_client = connection.clients.get_core_client()
        except Exception as e:
            logger.error(f"Failed to connect to Azure DevOps: {e}")
            return


class GetWikiTool(BaseAzureDevOpsWikiTool):
    """Tool to get information about a wiki in Azure DevOps."""
    name: str = GET_WIKI_TOOL.name
    description: str = GET_WIKI_TOOL.description
    args_schema: Type[BaseModel] = GetWikiInput

    def execute(self, wiki_identified: str):
        """Extract ADO wiki information."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)
        
        try:
            wiki: WikiV2 = self._client.get_wiki(project=self.project, wiki_identifier=wiki_identified)
            return wiki.as_dict()
        except Exception as e:
            logger.error(f"Error during the attempt to extract wiki: {str(e)}")
            return f"Error during the attempt to extract wiki: {str(e)}"


class GetWikiPageByPathTool(BaseAzureDevOpsWikiTool):
    """Tool to get wiki page content by path in Azure DevOps."""
    name: str = GET_WIKI_PAGE_BY_PATH_TOOL.name
    description: str = GET_WIKI_PAGE_BY_PATH_TOOL.description
    args_schema: Type[BaseModel] = GetPageByPathInput

    def execute(self, wiki_identified: str, page_name: str):
        """Extract ADO wiki page content."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)
        
        try:
            page = self._client.get_page(
                project=self.project, 
                wiki_identifier=wiki_identified, 
                path=page_name,
                include_content=True
            )
            return page.page.content
        except Exception as e:
            logger.error(f"Error during the attempt to extract wiki page: {str(e)}")
            return f"Error during the attempt to extract wiki page: {str(e)}"


class GetWikiPageByIdTool(BaseAzureDevOpsWikiTool):
    """Tool to get wiki page content by ID in Azure DevOps."""
    name: str = GET_WIKI_PAGE_BY_ID_TOOL.name
    description: str = GET_WIKI_PAGE_BY_ID_TOOL.description
    args_schema: Type[BaseModel] = GetPageByIdInput

    def execute(self, wiki_identified: str, page_id: int):
        """Extract ADO wiki page content."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)
        try:
            page = self._client.get_page_by_id(
                project=self.project, 
                wiki_identifier=wiki_identified, 
                id=page_id,
                include_content=True
            )
            return page.page.content
        except Exception as e:
            logger.error(f"Error during the attempt to extract wiki page: {str(e)}")
            return f"Error during the attempt to extract wiki page: {str(e)}"


class DeletePageByPathTool(BaseAzureDevOpsWikiTool):
    """Tool to delete wiki page by path in Azure DevOps."""
    name: str = DELETE_PAGE_BY_PATH_TOOL.name
    description: str = DELETE_PAGE_BY_PATH_TOOL.description
    args_schema: Type[BaseModel] = GetPageByPathInput

    def execute(self, wiki_identified: str, page_name: str):
        """Extract ADO wiki page content."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)
        
        try:
            self._client.delete_page(
                project=self.project, 
                wiki_identifier=wiki_identified, 
                path=page_name
            )
            return f"Page '{page_name}' in wiki '{wiki_identified}' has been deleted"
        except Exception as e:
            logger.error(f"Unable to delete wiki page: {str(e)}")
            return f"Unable to delete wiki page: {str(e)}"


class DeletePageByIdTool(BaseAzureDevOpsWikiTool):
    """Tool to delete wiki page by ID in Azure DevOps."""
    name: str = DELETE_PAGE_BY_ID_TOOL.name
    description: str = DELETE_PAGE_BY_ID_TOOL.description
    args_schema: Type[BaseModel] = GetPageByIdInput

    def execute(self, wiki_identified: str, page_id: int):
        """Extract ADO wiki page content."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)
        
        try:
            self._client.delete_page_by_id(
                project=self.project, 
                wiki_identifier=wiki_identified, 
                id=page_id
            )
            return f"Page with id '{page_id}' in wiki '{wiki_identified}' has been deleted"
        except Exception as e:
            logger.error(f"Unable to delete wiki page: {str(e)}")
            return f"Unable to delete wiki page: {str(e)}"


class RenameWikiPageTool(BaseAzureDevOpsWikiTool):
    """Tool to rename wiki page in Azure DevOps."""
    name: str = RENAME_WIKI_PAGE_TOOL.name
    description: str = RENAME_WIKI_PAGE_TOOL.description
    args_schema: Type[BaseModel] = RenamePageInput

    def execute(self, wiki_identified: str, old_page_name: str, new_page_name: str, version_identifier: str, version_type: str = "branch"):
        """Rename page in Azure DevOps wiki from old page name to new page name."""
        if not self._client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)
        
        try:
            try:
                result = self._client.create_page_move(
                    project=self.project,
                    wiki_identifier=wiki_identified,
                    comment=f"Page rename from '{old_page_name}' to '{new_page_name}'",
                    page_move_parameters=WikiPageMoveParameters(new_path=new_page_name, path=old_page_name),
                    version_descriptor=GitVersionDescriptor(version=version_identifier, version_type=version_type)
                )
                return {
                    "response": result,
                    "status": "Success",
                    "message": f"Page renamed from '{old_page_name}' to '{new_page_name}'"
                }
            except AzureDevOpsServiceError as e:
                if "The version '{0}' either is invalid or does not exist." in str(e):
                    # Retry the request without version_descriptor
                    result = self._client.create_page_move(
                        project=self.project,
                        wiki_identifier=wiki_identified,
                        comment=f"Page rename from '{old_page_name}' to '{new_page_name}'",
                        page_move_parameters=WikiPageMoveParameters(new_path=new_page_name, path=old_page_name),
                    )
                    return {
                        "response": result,
                        "status": "Success",
                        "message": f"Page renamed from '{old_page_name}' to '{new_page_name}' (without version)"
                    }
                else:
                    raise
        except Exception as e:
            logger.error(f"Unable to rename wiki page: {str(e)}")
            return f"Unable to rename wiki page: {str(e)}"


class ModifyWikiPageTool(BaseAzureDevOpsWikiTool):
    """Tool to create or update wiki page in Azure DevOps."""
    name: str = MODIFY_WIKI_PAGE_TOOL.name
    description: str = MODIFY_WIKI_PAGE_TOOL.description
    args_schema: Type[BaseModel] = ModifyPageInput

    def _create_wiki_if_not_exists(self, wiki_identified: str) -> Optional[str]:
        """Create wiki if it doesn't exist."""
        all_wikis = [wiki.name for wiki in self._client.get_all_wikis(project=self.project)]
        if wiki_identified in all_wikis:
            return None

        logger.info(f"Wiki name '{wiki_identified}' doesn't exist. New wiki will be created.")
        try:
            project_id = self._get_project_id()
            if not project_id:
                return "Project ID has not been found."
            
            self._client.create_wiki(
                project=self.project,
                wiki_create_params=WikiCreateParametersV2(name=wiki_identified, project_id=project_id)
            )
            logger.info(f"Wiki '{wiki_identified}' has been created")
            return None
        except Exception as create_wiki_e:
            error_msg = f"Unable to create new wiki due to error: {create_wiki_e}"
            logger.error(error_msg)
            return error_msg

    def _get_project_id(self) -> Optional[str]:
        """Get project ID from project name."""
        projects = self._core_client.get_projects()
        for project in projects:
            if project.name == self.project:
                return project.id
        return None

    def _get_page_version(self, wiki_identified: str, page_name: str) -> tuple[Optional[str], Optional[str]]:
        """Get page version (eTag) if page exists."""
        try:
            page = self._client.get_page(project=self.project, wiki_identifier=wiki_identified, path=page_name)
            version = page.eTag
            logger.info(f"Existing page found with eTag: {version}")
            return version, None
        except Exception as get_page_e:
            if "Ensure that the path of the page is correct and the page exists" in str(get_page_e):
                logger.info("Path is not found. New page will be created")
                return None, None
            error_msg = f"Unable to extract page by path {page_name}: {str(get_page_e)}"
            logger.error(error_msg)
            return None, error_msg

    def _create_or_update_page(self, wiki_identified: str, page_name: str, page_content: str,
                              version: Optional[str], version_identifier: str, version_type: str) -> dict:
        """Create or update the wiki page."""
        try:
            return self._try_create_or_update_with_version(
                wiki_identified, page_name, page_content, version, version_identifier, version_type
            )
        except AzureDevOpsServiceError as e:
            if "The version '{0}' either is invalid or does not exist." in str(e):
                return self._try_create_or_update_without_version(
                    wiki_identified, page_name, page_content, version
                )
            raise

    def _try_create_or_update_with_version(self, wiki_identified: str, page_name: str, 
                                          page_content: str, version: Optional[str],
                                          version_identifier: str, version_type: str) -> dict:
        """Attempt to create or update page with version information."""
        result = self._client.create_or_update_page(
            project=self.project,
            wiki_identifier=wiki_identified,
            path=page_name,
            parameters=WikiPageCreateOrUpdateParameters(content=page_content),
            version=version,
            version_descriptor=GitVersionDescriptor(version=version_identifier, version_type=version_type)
        )
        return self._create_result_dict(result, page_name, version)

    def _try_create_or_update_without_version(self, wiki_identified: str, page_name: str,
                                             page_content: str, version: Optional[str]) -> dict:
        """Attempt to create or update page without version information."""
        result = self._client.create_or_update_page(
            project=self.project,
            wiki_identifier=wiki_identified,
            path=page_name,
            parameters=WikiPageCreateOrUpdateParameters(content=page_content),
            version=version
        )
        return self._create_result_dict(result, page_name, version, with_version=False)

    def _create_result_dict(self, result, page_name: str, version: Optional[str], with_version: bool = True) -> dict:
        """Create a standardized result dictionary."""
        return {
            "response": result,
            "message": f"Page '{page_name}' has been {'updated' if version else 'created'}"
            f"{' (without version)' if not with_version else ''}"
        }

    def execute(self, wiki_identified: str, page_name: str, page_content: str,
                version_identifier: str, version_type: str = "branch"):
        """Create or Update ADO wiki page content."""
        if not self._client or not self._core_client:
            raise InvalidCredentialsError(CLIENT_IS_NOT_INITIALIZED)
        
        try:
            # Create wiki if needed
            error = self._create_wiki_if_not_exists(wiki_identified)
            if error:
                return error

            # Get page version
            version, error = self._get_page_version(wiki_identified, page_name)
            if error:
                return error

            # Create or update the page
            return self._create_or_update_page(
                wiki_identified, page_name, page_content,
                version, version_identifier, version_type
            )
        except Exception as e:
            error_msg = f"Unable to modify wiki page: {str(e)}"
            logger.error(error_msg)
            return error_msg
