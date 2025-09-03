from codemie_tools.base.models import ToolMetadata

UPDATE_FILE_TOOL = ToolMetadata(
    name="update_file",
    description="""
    This tool is a wrapper for the GitHub API, useful when you need to update a file in a GitHub repository.
    """,
    react_description="""
    This tool is a wrapper for the GitHub API, useful when you need to update the contents of a file in a GitHub repository. 
    **VERY IMPORTANT**: Your input to this tool MUST strictly follow these rules:
    - First you must specify which file to modify by passing a full file path (**IMPORTANT**: the path must not start with a slash)
    - Then you MUST specify detailed task description for file which must be updated or provide generated reference what should be done. It might be description or file content from implementation plan.
    
    For example, to update file 'src/main/java/Controller.java' with task to add new API endpoint you MUST pass in the following correct python Dictionary: 
    {{"file_path": "src/main/java/Controller.java", "task_details": "detailed task details or generated reference what should be done. It might be description or file content from implementation plan"}}.
    """,
)

UPDATE_FILE_DIFF_TOOL = ToolMetadata(
    name="update_file_diff",
    description="""
    This tool is a wrapper for the GitLab API, useful when you need to update a file in a GitLab repository.
    """,
    react_description="""
    This tool is a wrapper for the GitLab API, useful when you need to update the contents of a file in a GitLab repository. 
    **VERY IMPORTANT**: Your input to this tool MUST strictly follow these rules:
    - First you must specify which file to modify by passing a full file path (**IMPORTANT**: the path must not start with a slash)
    - Then you MUST specify detailed task description for file which must be updated or provide generated reference what should be done. It might be description or file content from implementation plan.
    
    For example, to update file 'src/main/java/Controller.java' with task to add new API endpoint you MUST pass in the following correct python Dictionary: 
    {{"file_path": "src/main/java/Controller.java", "task_details": "detailed task details or generated reference what should be done. It might be description or file content from implementation plan"}}.
    """,
)

CREATE_BRANCH_PROMPT = """This tool will create a new branch in the repository. **VERY IMPORTANT**: You must specify the name of the new branch as a string input parameter."""

LIST_BRANCHES_IN_REPO_PROMPT = """This tool will fetch a list of all branches in the repository. It will return the name of each branch. No input parameters are required."""

SET_ACTIVE_BRANCH_PROMPT = """This tool will set the active branch in the repository, similar to `git checkout <branch_name>` and `git switch -c <branch_name>`. **VERY IMPORTANT**: You must specify the name of the branch as a string input parameter."""

