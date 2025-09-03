import logging

from atlassian import Confluence
from langchain_core.tools import ToolException
from markdown import markdown

logger = logging.getLogger(__name__)


def validate_creds(confluence: Confluence):
    if confluence.url is None or confluence.url == "":
        logger.error("Confluence URL is required. Seems there no Confluence credentials provided.")
        raise ToolException("Confluence URL is required. Seems there no Confluence credentials provided.")


def prepare_page_payload(payload: dict) -> dict:
    """Convert Confluence payload from Markdown to HTML format for body.storage.value field."""
    if value := payload.get("body", {}).get("storage", {}).get("value"):
        payload["body"]["storage"]["value"] = markdown(value) # convert markdown to HTML

    return payload
