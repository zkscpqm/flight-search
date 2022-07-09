import dataclasses
import json

from requests import Session, Response

from util.types import const


@dataclasses.dataclass
class ExchangeRateResponse:
    base: str
    rates: dict[str, float] = None
    error_code: int = None
    error_text: str = None


class ExchangeRatesSession:

    BASE_ENDPOINT: const(str) = "https://api.apilayer.com/exchangerates_data/latest"

    MONTHLY_LIMIT: const(str) = "x-ratelimit-limit-month"
    MONTHLY_REMAINING: const(str) = "x-ratelimit-remaining-month"
    DAILY_LIMIT: const(str) = "x-ratelimit-limit-day"
    DAILY_REMAINING: const(str) = "x-ratelimit-remaining-day"

    def __init__(self, api_key: str):
        self._api_key: str = api_key
        self._sess: Session = Session()
        self._rate_limiting: dict[str, int] = {
            self.MONTHLY_LIMIT: -1,
            self.MONTHLY_REMAINING: -1,
            self.DAILY_LIMIT: -1,
            self.DAILY_REMAINING: -1
        }

    def _build_url(self, base: str) -> str:
        return f"{self.BASE_ENDPOINT}?base={base}"

    def _perform_request(self, url: str) -> Response:
        return self._sess.get(url, headers={"apikey": self._api_key}, data={})

    def get_rates(self, base: str) -> ExchangeRateResponse:
        url = self._build_url(base)
        resp = self._perform_request(url)
        if resp.ok:
            return ExchangeRateResponse(
                base=base,
                rates=json.loads(resp.text).get("rates")
            )
        return ExchangeRateResponse(
            base=base,
            error_code=resp.status_code,
            error_text=json.loads(resp.text).get("error")
        )
