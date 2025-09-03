import logging
import re
import traceback
from typing import Optional, Tuple, Dict, Any

from atlassian.bitbucket.cloud.repositories import Repository
from pydantic import BaseModel, Field

from codemie_tools.base.errors import InvalidCredentialsError
from codemie_tools.git.bitbucket.custom_bitbucket_wrapper import (
    CustomBitbucketApiWrapper,
)
from codemie_tools.git.github.custom_github_api_wrapper import CustomGitHubAPIWrapper
from codemie_tools.git.gitlab.custom_gitlab_api_wrapper import CustomGitLabAPIWrapper
from codemie_tools.git.azure_devops.tools import AzureDevOpsClient


logger = logging.getLogger(__name__)

NO_GIT_CREDS_FOUND_LOG = "No Git credentials found for this repository"
CLIENT_ERROR_MESSAGE = "Client is not initialized"
NO_GIT_CREDS_FOUND_MESSAGE = (
    "No Git credentials found for repository. Provide Git credentials in 'Integrations'"
)

TYPE_GITHUB: str = "github"
TYPE_GITLAB: str = "gitlab"
TYPE_BITBUCKET: str = "bitbucket"
TYPE_AZURE_DEVOPS: str = "azure_devops"
TYPE_UNKNOWN: str = "unknown"


class GitCredentials(BaseModel):
    token: str
    token_name: Optional[str] = None
    repo_link: str
    base_branch: str
    repo_type: str = Field(default=TYPE_UNKNOWN)


def init_gitlab_api_wrapper(
    git_creds: GitCredentials,
) -> Optional[CustomGitLabAPIWrapper]:
    base_url, repo_name = split_git_url(git_creds.repo_link)
    try:
        if not git_creds.token:
            return None
        return CustomGitLabAPIWrapper(
            gitlab_base_url=base_url,
            gitlab_repository=repo_name.replace(".git", "").replace("/", "", 1),
            gitlab_base_branch=git_creds.base_branch,
            gitlab_branch=git_creds.base_branch,
            gitlab_personal_access_token=git_creds.token,
        )
    except Exception:
        stacktrace = traceback.format_exc()
        logger.error(
            f"GitLab API wrapper initialisation failed with error: {stacktrace}",
            exc_info=True,
        )
        return None


def init_github_api_wrapper(git_creds: GitCredentials):
    try:
        if not git_creds.token:
            return None
        if git_creds.repo_link is not None:
            _, repo_name = split_git_url(git_creds.repo_link)
            github = CustomGitHubAPIWrapper(
                github_repository=repo_name.replace(".git", "").replace("/", "", 1),
                github_base_branch=git_creds.base_branch,
                active_branch=git_creds.base_branch,
                github_access_token=git_creds.token,
            )
        else:
            github = CustomGitHubAPIWrapper(github_access_token=git_creds.token)
        return github
    except Exception:
        stacktrace = traceback.format_exc()
        logger.error(
            f"GitHub API wrapper initialisation failed with error: {stacktrace}",
            exc_info=True,
        )
        return None


def init_bitbucket_api_wrapper(git_creds: GitCredentials):
    try:
        if not git_creds.token:
            return None
        base_url, project_and_repo_str = split_git_url(git_creds.repo_link)
        project_and_repo = project_and_repo_str.replace("/", "", 1).split("/")
        project_key = project_and_repo[0]
        repo_name = project_and_repo[1].replace(".git", "").replace("/", "", 1)
        return CustomBitbucketApiWrapper(
            url=base_url,
            token=git_creds.token,
            project_key=project_key,
            repository_slug=repo_name,
            base_branch=git_creds.base_branch,
            active_branch=git_creds.base_branch,
        )
    except Exception:
        stacktrace = traceback.format_exc()
        logger.error(
            f"Bitbucket API wrapper initialisation failed with error: {stacktrace}",
            exc_info=True,
        )
        return None


def validate_azure_devops_credentials(*, configs: Dict[str, Any]):
    try:
        azure_credentials = AzureDevOpsClient.init_credentials(configs=configs)
        client = AzureDevOpsClient(azure_credentials)
        client.verify_connection()
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error(
            f"AzureDevOpsClient initialization failed with error: {stacktrace}",
            exc_info=True,
        )
        raise InvalidCredentialsError(f"Azure DevOps API client initialization failed: {str(e)}")


def validate_gitlab_wrapper(api_wrapper: [CustomGitLabAPIWrapper], git_creds: GitCredentials):
    if api_wrapper is not None:
        return
    if git_creds.token is None or git_creds.token == "":
        logger.error(NO_GIT_CREDS_FOUND_LOG)
        raise InvalidCredentialsError(NO_GIT_CREDS_FOUND_MESSAGE)
    try:
        gitlab_api_wrapper = init_gitlab_api_wrapper(git_creds)
        if gitlab_api_wrapper is None:
            raise InvalidCredentialsError(CLIENT_ERROR_MESSAGE)
        return gitlab_api_wrapper
    except Exception:
        stacktrace = traceback.format_exc()
        logger.error(
            f"GitLab API client initialisation failed with error: {stacktrace}",
            exc_info=True,
        )
        raise InvalidCredentialsError(
            "GitLab API client initialisation failed: Please check your GitLab credentials are "
            "provided in 'User Settings'"
        )


def validate_bitbucket(bitbucket: Optional[Repository], git_creds: GitCredentials):
    if bitbucket is not None:
        return

    if git_creds.token is None or git_creds.token == "":
        logger.error(NO_GIT_CREDS_FOUND_LOG)
        raise InvalidCredentialsError(NO_GIT_CREDS_FOUND_MESSAGE)
    try:
        bitbucket = init_bitbucket_api_wrapper(git_creds)
        if bitbucket is None:
            raise InvalidCredentialsError(CLIENT_ERROR_MESSAGE)
        return bitbucket
    except Exception:
        stacktrace = traceback.format_exc()
        logger.error(
            f"Bitbucket API client initialisation failed with error: {stacktrace}",
            exc_info=True,
        )
        raise InvalidCredentialsError(
            "Bitbucket API client initialisation failed: Please check your Git credentials "
            "are provided in 'User Settings'"
        )


def validate_github_wrapper(
    api_wrapper: Optional[CustomGitHubAPIWrapper], git_creds: GitCredentials
):
    if api_wrapper is not None:
        return

    if git_creds.token is None or git_creds.token == "":
        logger.error(NO_GIT_CREDS_FOUND_LOG)
        raise InvalidCredentialsError(NO_GIT_CREDS_FOUND_MESSAGE)
    try:
        github_api_wrapper = init_github_api_wrapper(git_creds)
        if github_api_wrapper is None:
            raise InvalidCredentialsError(CLIENT_ERROR_MESSAGE)
        return github_api_wrapper
    except Exception:
        stacktrace = traceback.format_exc()
        logger.error(
            f"GitHub API client initialisation failed with error: {stacktrace}",
            exc_info=True,
        )
        raise InvalidCredentialsError(
            "GitHub API client initialisation failed: Please check your Git credentials "
            "are provided in 'User Settings'"
        )


def split_git_url(git_url: str) -> Tuple[str, str]:
    regexp_split_url_and_repo = r"(https?:\/\/[^\/]+)(\/.*)"
    url_and_repo = re.split(regexp_split_url_and_repo, git_url)
    url_and_repo = list(filter(None, url_and_repo))

    base_url = url_and_repo[0]
    token_regexp = r"(?<=://).*@" #NOSONAR
    match = re.search(token_regexp, base_url)

    if match:
        token = match.group().split("@")[0] + "@"
        base_url = base_url.replace(token, "")

    return base_url, url_and_repo[1].rstrip("/")
