from typing import Optional
from pydantic import BaseModel, Field

class ListBranchesToolInput(BaseModel):
    query: Optional[str] = Field(
        default="",
        description="User initial request should be passed as a string.",
    )
