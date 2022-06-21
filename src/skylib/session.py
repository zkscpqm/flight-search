from datetime import datetime, timedelta
from typing import Callable

from requests import Session, Response

from util.types import nullable, const


class AuthenticationError(Exception):
    def __init__(self, endpoint: str, auth: str = None):
        self.endpoint: const(str) = endpoint
        self.auth: nullable(str) = auth

    def __str__(self) -> str:
        msg = f"failed to authenticate for {self.endpoint}"
        if self.auth:
            msg = f"{msg} with provided auth: `{self.auth}`"
        return msg


class AmadeusSession:

    BASE_ENDPOINT: const(str) = "https://test.api.amadeus.com/"

    def __init__(self, api_key: str, api_secret: str, workers: int = 10, lazy_init: bool = False):
        self._api_key: str = api_key
        self._api_secret: str = api_secret
        self._max_workers: int = 10
        self._sess: Session = Session()
        self._initialized: bool = False

        self._token_expiry: nullable(datetime) = None
        self._access_token: nullable(str) = None
        if not lazy_init:
            self._init()

    @classmethod
    def _build_url(cls, *parts) -> str:
        return cls.BASE_ENDPOINT + "/".join(parts)

    def _init(self):
        self._refresh_access_token()

    def _cycle_token(self):
        if self._token_expiry < datetime.now():
            self._refresh_access_token()

    def _request(self, url: str, method: str = "GET", **kwargs) -> Response:
        self._cycle_token()
        headers = {"Authorization": f"Bearer {self._access_token}"} | kwargs.pop("headers", {})
        return self._sess.request(method=method, url=url, headers=headers, **kwargs)

    def _refresh_access_token(self):
        if not self._api_key or not self._api_secret:
            raise AttributeError("no api key and/or secret set")
        url = self._build_url("v1", "security", "oauth2", "token")
        resp = self._sess.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self._api_key,
                "client_secret": self._api_secret
            }
        )
        if not resp.ok:
            raise AuthenticationError(url, auth=self._api_key)
        if not (token := resp.json().get("access_token")):
            raise AttributeError("response does not contain access token!")
        self._access_token = token
        self._initialized = True
        self._token_expiry = datetime.now() + timedelta(minutes=30)
