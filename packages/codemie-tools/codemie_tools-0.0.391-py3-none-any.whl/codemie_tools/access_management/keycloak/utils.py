import requests

from codemie_tools.access_management.keycloak.models import KeycloakConfig


def get_keycloak_admin_token(config: KeycloakConfig):
    url = f"{config.base_url}/realms/{config.realm}/protocol/openid-connect/token"
    payload = {
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']
