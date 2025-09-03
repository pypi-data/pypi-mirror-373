from pydantic import BaseModel


class EmailToolConfig(BaseModel):
    url: str
    smtp_username: str
    smtp_password: str
