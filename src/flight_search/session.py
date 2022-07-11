from datetime import datetime, timedelta

from requests import Session, Response

from src.currency.money import Money
from src.flight_search.airport import Airport
from src.flight_search.search_query import FlightSearchQuery
from util.goroutine import Channel
from util.logging.logger import Logger, get_default_logger
from util.types import nullable, const


class AmadeusSession:

    logger: Logger = get_default_logger()
    BASE_ENDPOINT: const(str) = "https://test.api.amadeus.com/"

    def __init__(self, api_key: str, api_secret: str, lazy_init: bool = False, logger: Logger = None):
        if logger:
            self.logger: Logger = logger
            self.__class__.logger = logger
        self._api_key: str = api_key
        self._api_secret: str = api_secret
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
        self.logger.info("Trying to get Amadeus API token...")
        if not self._api_key or not self._api_secret:
            self.logger.error("Cannot refresh Amadeus Session. No api key and/or secret set")
            return
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
            self.logger.error(f"Failed to get Amadeus token from `{url}`:"
                              f"[{resp.status_code}] {resp.text}")
            return
        if not (token := resp.json().get("access_token")):
            self.logger.error(f"Response does not contain access token! Resp:\n{resp.text}")
            return
        self._access_token = token
        self._initialized = True
        self._token_expiry = datetime.now() + timedelta(minutes=30)
        self.logger.info("Amadeus access token set!")

    def find_flights_o2o(self, depart: Airport, arrive: Airport, budget: Money, dates: list[datetime],
                         channel: Channel):
        ...

    def find_flights_m2o(self, depart: list[Airport], arrive: Airport, budget: Money, dates: list[datetime],
                         channel: Channel):
        ...

    def find_flights_o2m(self, depart: Airport, arrive: list[Airport], budget: Money, dates: list[datetime],
                         channel: Channel):
        ...

    def find_flights_m2m(self, depart: list[Airport], arrive: list[Airport], budget: Money, dates: list[datetime],
                         channel: Channel):
        ...

    def search(self, query: FlightSearchQuery) -> Channel:

        chan = Channel()
        if (len_dep := len(query.depart_from)) < 1:
            raise ValueError("You need to choose at least one departure point")
        if (len_arr := len(query.arrive_at)) < 1:
            raise ValueError("You need to choose at least one arrival point")

        match [len_dep > 1, len_arr > 1]:
            case [True, True]:
                self.find_flights_m2m(
                    depart=query.depart_from,
                    arrive=query.arrive_at,
                    budget=query.budget,
                    dates=query.departure_dates,
                    channel=chan
                )
            case [True, False]:
                self.find_flights_m2o(
                    depart=query.depart_from,
                    arrive=query.arrive_at[0],
                    budget=query.budget,
                    dates=query.departure_dates,
                    channel=chan
                )
            case [False, True]:
                self.find_flights_o2m(
                    depart=query.depart_from[0],
                    arrive=query.arrive_at,
                    budget=query.budget,
                    dates=query.departure_dates,
                    channel=chan
                )
            case [False, False]:
                self.find_flights_o2o(
                    depart=query.depart_from[0],
                    arrive=query.arrive_at[0],
                    budget=query.budget,
                    dates=query.departure_dates,
                    channel=chan
                )
        return chan
