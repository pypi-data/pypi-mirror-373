from codemie_tools.base.models import ToolMetadata

GET_WIKI_TOOL = ToolMetadata(
    name="get_wiki",
    description="""
        Extract ADO wiki information. Takes a wiki identifier (name or ID) and returns detailed information about the wiki,
        including its ID, name, URL, remote URL, type, and associated project and repository IDs.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name to extract information about.
        Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        E.g. https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
        "CodeMie.wiki" is the wiki identifier in this case.
        "How-to-Create-Angular-Application" is the page name.
        """,
    label="Get Wiki",
    user_description="""
        Retrieves information about a specific Azure DevOps wiki. The tool provides details about the wiki
        such as its ID, name, URL, and other metadata from the Azure DevOps project.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

GET_WIKI_PAGE_BY_PATH_TOOL = ToolMetadata(
    name="get_wiki_page_by_path",
    description="""
        Extract ADO wiki page content by path. Retrieves the full content of a wiki page using the page path.
        The content is returned as Markdown text.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_name (str): Wiki page path (e.g. "/Home", "/Folder/Page")
        E.g. https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
        "CodeMie.wiki" is the wiki identifier in this case.
        "How-to-Create-Angular-Application" is the page name.
        """,
    label="Get Wiki Page By Path",
    user_description="""
        Retrieves the content of a wiki page by its path. The tool returns the Markdown content of the specified
        wiki page in the Azure DevOps project.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

GET_WIKI_PAGE_BY_ID_TOOL = ToolMetadata(
    name="get_wiki_page_by_id",
    description="""
        Extract ADO wiki page content by ID. Retrieves the full content of a wiki page using the page ID.
        The content is returned as Markdown text.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_id (int): Wiki page ID (numeric identifier)
        E.g. https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
        "CodeMie.wiki" is the wiki identifier in this case.
        "10" is the page id.
        """,
    label="Get Wiki Page By ID",
    user_description="""
        Retrieves the content of a wiki page by its ID. The tool returns the Markdown content of the specified
        wiki page in the Azure DevOps project.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

DELETE_PAGE_BY_PATH_TOOL = ToolMetadata(
    name="delete_page_by_path",
    description="""
        Delete a wiki page by its path. Permanently removes the specified wiki page from the project's wiki.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_name (str): Wiki page path to delete (e.g. "/Home", "/Folder/Page")
        E.g. https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
        "CodeMie.wiki" is the wiki identifier in this case.
        "How-to-Create-Angular-Application" is the page name.
        """,
    label="Delete Wiki Page By Path",
    user_description="""
        Deletes a wiki page identified by its path. The tool removes the specified wiki page from the
        Azure DevOps project wiki.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

DELETE_PAGE_BY_ID_TOOL = ToolMetadata(
    name="delete_page_by_id",
    description="""
        Delete a wiki page by its ID. Permanently removes the specified wiki page from the project's wiki.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_id (int): Wiki page ID to delete (numeric identifier)
        """,
    label="Delete Wiki Page By ID",
    user_description="""
        Deletes a wiki page identified by its ID. The tool removes the specified wiki page from the
        Azure DevOps project wiki.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
)

RENAME_WIKI_PAGE_TOOL = ToolMetadata(
    name="rename_wiki_page",
    description="""
        Rename page in Azure DevOps wiki from old page name to new page name.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - old_page_name (str): Current page path to be renamed (e.g. "/OldName")
        - new_page_name (str): New page path (e.g. "/NewName")
        - version_identifier (str): Version string identifier (name of tag/branch, SHA1 of commit)
        - version_type (str, optional): Version type (branch, tag, or commit). Determines how Id is interpreted. Default is "branch"
        E.g. https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
        "CodeMie.wiki" is the wiki identifier in this case.
        "How-to-Create-Angular-Application" is the page name.
        """,
    label="Rename Wiki Page",
    user_description="""
        Renames an existing wiki page from the old path to a new path. The tool updates the path of the 
        specified wiki page in the Azure DevOps project.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        4. Version identifier (e.g., branch name or commit SHA)
        """.strip(),
)

MODIFY_WIKI_PAGE_TOOL = ToolMetadata(
    name="modify_wiki_page",
    description="""
        Create or Update ADO wiki page content. If the wiki doesn't exist, it will be automatically created.
        If the page doesn't exist, a new page will be created; otherwise the existing page will be updated.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_name (str): Wiki page path to create or update (e.g. "/Home", "/Folder/Page")
        - page_content (str): Markdown content for the wiki page
        - version_identifier (str): Version string identifier (name of tag/branch, SHA1 of commit)
        - version_type (str, optional): Version type (branch, tag, or commit). Determines how Id is interpreted. Default is "branch".
        E.g. https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
        "CodeMie.wiki" is the wiki identifier in this case.
        "How-to-Create-Angular-Application" is the page name.
        """,
    label="Modify Wiki Page",
    user_description="""
        Creates a new wiki page or updates an existing one with the specified content. If the wiki doesn't exist,
        it will be created. The tool handles both creation and updates of wiki pages in Azure DevOps.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        4. Version identifier (e.g., branch name or commit SHA)
        """.strip(),
)
