import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Type, Optional, Tuple

from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.notification.email.models import EmailToolConfig
from codemie_tools.notification.tools_vars import EMAIL_TOOL


class EmailToolInput(BaseModel):
    recipient_emails: list[str] = Field(None, description="A list of recipient email addresses")
    subject: str = Field(None, description="The email subject")
    body: str = Field(None, description="The body of the email")
    cc_emails: Optional[list[str]] = Field(
        None, description="A list of cc (carbon copy) email addresses"
    )


class EmailTool(CodeMieTool):
    name: str = EMAIL_TOOL.name
    email_creds: Optional[EmailToolConfig] = Field(exclude=True, default=None)
    args_schema: Type[BaseModel] = EmailToolInput
    description: str = EMAIL_TOOL.description

    def execute(
        self,
        recipient_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
    ) -> str:
        if not self.email_creds:
            raise ValueError("Email configuration is not provided.")
        try:
            host, port = self.email_creds.url.split(":")
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_creds.smtp_username
            msg["To"] = ", ".join(recipient_emails)
            if cc_emails:
                msg["Cc"] = ", ".join(cc_emails)

            part = MIMEText(body, "html")
            msg.attach(part)

            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(self.email_creds.smtp_username, self.email_creds.smtp_password)
                all_recipients_emails = recipient_emails + (cc_emails if cc_emails else [])
                server.sendmail(
                    self.email_creds.smtp_username, all_recipients_emails, msg.as_string()
                )
                server.quit()

            return f"Email sent successfully to {all_recipients_emails}"
        except Exception as e:
            return f"Failed to send email: {e}"

    def integration_healthcheck(self) -> Tuple[bool, str]:
        if not self.email_creds:
            return False, "Email configuration is not provided."
        try:
            host, port = self.email_creds.url.split(":")
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(self.email_creds.smtp_username, self.email_creds.smtp_password)
                server.noop()
                server.quit()
            return True, ""
        except smtplib.SMTPResponseException as e:
            return False, f"SMTP Code: {e.smtp_code}. SMTP error: {e.smtp_error}"
        except smtplib.SMTPException as e:
            return False, str(e)
