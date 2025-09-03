from pydantic import BaseModel
from typing import Optional, List


class OpenApiConfig(BaseModel):
    spec: str
    is_basic_auth: bool = False
    username: Optional[str] = None
    api_key: str
    timeout: int = 120
    auth_header_name: Optional[str] = None  # Custom auth header name, if not provided, default is 'Authorization'
