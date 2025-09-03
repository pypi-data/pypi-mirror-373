import datetime as dt
from base64 import b64encode
from collections.abc import Generator
from typing import Literal, TypedDict

import httpx
from httpx import Request, Response


class AccessToken(TypedDict):
    token_type: Literal["access_token"]
    access_token: str
    expires_in: int


class AnbimaAuth(httpx.Auth):
    requires_response_body = True

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ""
        self.expires_at = dt.datetime.min.replace(tzinfo=dt.timezone.utc)

    def should_refresh(self) -> bool:
        return self.expires_at < (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=3))

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        if self.should_refresh():
            yield from self.authenticate()

        request.headers["client_id"] = self.client_id
        request.headers["access_token"] = self.access_token
        yield request

    def authenticate(self) -> Generator[Request, Response, None]:
        token = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        response = yield httpx.Request(
            method="POST",
            url="https://api.anbima.com.br/oauth/access-token",
            headers={
                "Authorization": f"Basic {token}",
            },
            json={
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        body: AccessToken = response.json()

        self.access_token = body["access_token"]
        self.expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=body["expires_in"])
