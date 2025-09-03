from codemie_tools.base.models import ToolMetadata

CREATE_GIT_BRANCH_TOOL = ToolMetadata(
    name="create_branch",
)

CREATE_PULL_REQUEST_TOOL = ToolMetadata(
    name="create_pull_request",
)

CREATE_FILE_TOOL = ToolMetadata(
    name="create_file",
)

DELETE_FILE_TOOL = ToolMetadata(
    name="delete_file",
)

LIST_BRANCHES_TOOL = ToolMetadata(
    name="list_branches_in_repo",
)

UPDATE_FILE_TOOL = ToolMetadata(
    name="update_file",
)

UPDATE_FILE_DIFF_TOOL = ToolMetadata(
    name="update_file_diff",
)

SET_ACTIVE_BRANCH_TOOL = ToolMetadata(
    name="set_active_branch",
)
GET_PR_CHANGES = ToolMetadata(
    name="get_pr_changes",
)
CREATE_PR_CHANGE_COMMENT = ToolMetadata(
    name="create_pr_change_comment",
)
