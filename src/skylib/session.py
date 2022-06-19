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


class SkyscannerSession:

    BASE_ENDPOINT: const(str) = "https://partners.api.skyscanner.net/apiservices/"

    def __init__(self, api_key: str, workers: int = 10):
        self._api_key: str = api_key
        self._max_workers: int = 10
        self._sess: Session = Session()
        self._initialized: bool = False

        self._access_token: nullable(str) = None

        self._init()

    @classmethod
    def _build_url(cls, *parts) -> str:
        return cls.BASE_ENDPOINT + "/".join(parts)

    def _init(self):
        self._refresh_access_token()

    @staticmethod
    def _validate_response(resp: Response) -> bool:
        if resp.status_code > 299:
            return False
        try:
            j: dict = resp.json()
            if j.get("code") > 299:
                return False
            return True
        except Exception as e:
            print(f"could not serialize response. error: {e}, resp (code {resp.status_code}): {resp.text}")
            return False

    def _refresh_access_token(self):
        if not self._api_key:
            raise AttributeError("no api key set")
        url = self._build_url("token", "v2", "gettoken")
        resp = self._sess.get(url, params={"apiKey": self._api_key})
        if not self._validate_response(resp):
            raise AuthenticationError(url, auth=self._api_key)
        if not (token := resp.json().get("message")):
            raise AttributeError("response does not contain access token!")
        self._access_token = token
        self._initialized = True
