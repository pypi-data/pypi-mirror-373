from typing import Optional

from pydantic import BaseModel


class SonarToolConfig(BaseModel):
    url: Optional[str] = None
    sonar_token: Optional[str] = None
    sonar_project_name: Optional[str] = None
