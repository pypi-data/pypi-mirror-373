import logging

import requests
from pydantic import BaseModel, SecretStr, field_serializer


__all__ = [
    "get_cockpit_credentials",
    "get_auth_headers",
    "CockpitAuthParams",
    "CockpitTenantCredentials",
]
logger = logging.getLogger(__name__)


class CockpitAuthParams(BaseModel):
    issuer: str
    client_id: str
    client_secret: SecretStr
    refresh_token: SecretStr

    @field_serializer("client_secret", "refresh_token", when_used="json")
    def dump_secret(self, v):  # noqa: PLR6301
        return v.get_secret_value()


class CockpitTenantCredentials(BaseModel):
    oidc: CockpitAuthParams
    url: str


def get_cockpit_credentials(cockpit_raw_credentials: dict) -> dict[str, CockpitTenantCredentials]:
    cockpit_credentials = {
        k: CockpitTenantCredentials(**v)
        for k, v in cockpit_raw_credentials.items()
    }
    return cockpit_credentials


def get_openid_connect_token(auth_params: CockpitAuthParams) -> str:
    payload = {
        "client_id": auth_params.client_id,
        "client_secret": auth_params.client_secret.get_secret_value(),
        "grant_type": "refresh_token",
        "refresh_token": auth_params.refresh_token.get_secret_value(),
    }
    response = requests.post(auth_params.issuer, data=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Auth API response returned code: {response.status_code} (text hidden)")

    return response.json()["access_token"]


def get_auth_headers(auth_params: CockpitAuthParams) -> dict:
    oidc_token = get_openid_connect_token(auth_params)
    headers = {
        "Authorization": f"Bearer {oidc_token}",
        "Content-Type": "application/json",
    }
    return headers
