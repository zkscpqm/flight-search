import dataclasses
import json

from requests import Session, Response

from util.logging.logger import Logger, get_default_logger
from util.types import const


@dataclasses.dataclass
class ExchangeRateResponse:
    base: str
    rates: dict[str, float] = None
    error_code: int = None
    error_text: str = None


class ExchangeRatesSession:

    logger: Logger = get_default_logger()

    BASE_ENDPOINT: const(str) = "https://api.apilayer.com/exchangerates_data/latest"

    _MONTHLY_LIMIT_KEY: const(str) = "X-RateLimit-Limit-Month"
    _MONTHLY_REMAINING_KEY: const(str) = "X-RateLimit-Remaining-Month"
    _DAILY_LIMIT_KEY: const(str) = "X-RateLimit-Limit-Day"
    _DAILY_REMAINING_KEY: const(str) = "X-RateLimit-Remaining-Day"

    def __init__(self, api_key: str, logger: Logger = None):
        if logger:
            self.logger: Logger = logger
            self.__class__.logger = logger
        self._api_key: str = api_key
        self._sess: Session = Session()
        self._rate_limiting: dict[str, int] = {
            self._MONTHLY_LIMIT_KEY: -1,
            self._MONTHLY_REMAINING_KEY: -1,
            self._DAILY_LIMIT_KEY: -1,
            self._DAILY_REMAINING_KEY: -1
        }

    @property
    def monthly_requests_limit(self) -> int:
        return self._rate_limiting[self._MONTHLY_LIMIT_KEY]

    @property
    def monthly_requests_remaining(self) -> int:
        return self._rate_limiting[self._MONTHLY_REMAINING_KEY]

    @property
    def daily_requests_limit(self) -> int:
        return self._rate_limiting[self._DAILY_LIMIT_KEY]

    @property
    def daily_requests_remaining(self) -> int:
        return self._rate_limiting[self._DAILY_REMAINING_KEY]

    def _build_url(self, base: str) -> str:
        return f"{self.BASE_ENDPOINT}?base={base}"

    def _perform_request(self, url: str) -> Response:
        return self._sess.get(url, headers={"apikey": self._api_key}, data={})

    def get_rates(self, base: str) -> ExchangeRateResponse:
        url = self._build_url(base)
        self.logger.info(f"Attempting to load FX rates from `{url}`...")
        resp = self._perform_request(url)
        if resp.ok:
            self.logger.info(f"FX rates fetched successfully! ({resp.status_code})")
            for key in self._rate_limiting.keys():
                self._rate_limiting[key] = resp.headers.get(key, -1)
            return ExchangeRateResponse(
                base=base,
                rates=json.loads(resp.text).get("rates")
            )
        self.logger.error(f"Could not fetch FX rates!")
        return ExchangeRateResponse(
            base=base,
            error_code=resp.status_code,
            error_text=json.loads(resp.text).get("error")
        )
