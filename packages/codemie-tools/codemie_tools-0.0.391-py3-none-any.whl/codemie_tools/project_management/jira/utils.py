import logging

from atlassian import Jira

from codemie_tools.base.errors import InvalidCredentialsError

logger = logging.getLogger(__name__)


def validate_jira_creds(jira: Jira):
    if jira.url is None or jira.url == "":
        logger.error("Jira URL is required. Seems there no Jira credentials provided.")
        raise InvalidCredentialsError("Jira URL is required. You should provide Jira credentials in 'Integrations'.")


