from codemie_tools.base.models import ToolMetadata

EMAIL_TOOL = ToolMetadata(
    name="Email",
    description="Use this tool when you asked to send an email notification.",
    label="Email",
    user_description="""The purpose of the email tool is to send emails using SMTP protocol. 
    Before using it it is necessary to add a new integration for the tool providing your: 
    1. SMTP Server URL;
    2. SMTP Server User Name;
    3. SMTP Server User Password.
    
    NOTE: Accounts with enabled MFA must use App Password instead of account password. App Password creation must be allowed by your organization policy.
    For example: support.google.com/mail/answer/185833
    """
)

TELEGRAM_TOOL = ToolMetadata(
    name="Telegram",
    description="""
    Tool to interact with the Telegram Bot API.
    You must provide the following args: relative_url, method, params. 
    1. 'method': The HTTP method, e.g. 'GET', 'POST', 'PUT', 'DELETE' etc.
    2. 'relative_url': Required relative URI of the Telegram Bot API. E.g. 'sendMessage'.
    Do not include query parameters in the URL, they must be provided separately in 'params'.
    3. 'params': Optional JSON of parameters to be sent in request body or query params. MUST be string with valid JSON. 
    Important: to send message, you MUST get "chat_id" parameter first.
    """,
    label="Telegram",
    user_description="""
    Provides access to the Telegram Bot API, enabling interaction with Telegram users and groups through a bot. This tool allows the AI assistant to send messages, receive updates, and perform various bot-related operations on the Telegram platform.
    Before using it, it is necessary to add a new integration for the tool by providing:
    1. Alias (A friendly name for the Telegram bot integration)
    2. Telegram Bot Token
    Usage Note:
    Use this tool when you need to interact with Telegram users or groups via a bot, such as sending notifications, responding to commands, or managing group chats.
    """.strip()
)
