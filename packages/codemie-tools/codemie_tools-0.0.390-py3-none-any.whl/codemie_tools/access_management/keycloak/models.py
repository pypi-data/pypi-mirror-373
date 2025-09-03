from typing import Dict, Any

from pydantic import BaseModel, model_validator


class KeycloakConfig(BaseModel):
    base_url: str
    realm: str
    client_id: str
    client_secret: str

    @classmethod
    @model_validator(mode='before')
    def validate_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for field_name in cls.model_fields.keys():
            if field_name not in values or not values[field_name]:
                raise ValueError(f"{field_name} is a required field and must be provided.")
        return values
