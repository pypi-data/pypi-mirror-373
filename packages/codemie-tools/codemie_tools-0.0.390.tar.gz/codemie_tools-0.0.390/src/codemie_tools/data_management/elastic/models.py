from typing import Tuple, Optional

from pydantic import BaseModel


class ElasticConfig(BaseModel):
    url: str
    api_key: Optional[Tuple[str, str]] = None


