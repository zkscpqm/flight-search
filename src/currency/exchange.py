import json
from datetime import datetime
from pathlib import Path

from src.currency.money import Money, Currency
from src.currency.session import ExchangeRatesSession
from util.logging.logger import Logger, get_default_logger
from util.singleton import SingletonMeta
from util.types import nullable


class ExchangeRateMap(metaclass=SingletonMeta):

    logger: Logger = get_default_logger()

    def __init__(self, fx_exchange_api_key: str, cache_location: Path, base_currency: str = Currency.EUR,
                 preload: bool = True, logger: Logger = None):
        if logger:
            self.logger: Logger = logger
            self.__class__.logger = logger
        self._cache_location: Path = cache_location
        self._rates: dict[str, dict[str, float]] = {}
        self._base_currency: str = base_currency
        self._fx_sess: ExchangeRatesSession = ExchangeRatesSession(api_key=fx_exchange_api_key)
        if preload:
            self.load_rates(cache_base_path=cache_location)

    def _set_rate(self, currency1: str, currency2: str, rate: float, inverse: bool = True):
        if mapping := self._rates[currency1]:
            mapping[currency2] = rate
        else:
            self._rates[currency1] = {currency2: rate}
        if inverse:
            if mapping := self._rates[currency2]:
                mapping[currency2] = 1 / rate
            else:
                self._rates[currency2] = {currency1: 1 / rate}

    def get_rate(self, currency1: str, currency2: str) -> nullable(float):
        if mapping := self._rates.get(currency1):
            return mapping.get(currency2)

    def change_base_currency(self, new_base_currency: str, repopulate: bool = True, cache_location: Path = None):
        self._base_currency = new_base_currency
        self.logger.debug(f"Updated base currency to `{new_base_currency}`")
        if repopulate:
            self.load_rates(cache_base_path=cache_location, overwrite=True)

    def load_rates(self, cache_base_path: Path = None, overwrite: bool = False):
        now_ = datetime.now().strftime("%Y-%m-%d")
        self.logger.info(f"Attempting to load FX rates for {now_}...")
        today_filename = f"{now_}_exchange_rates.json"
        cachepath = (cache_base_path or self._cache_location) / today_filename
        if self._load_fx_rates_from_file(cachepath) and not overwrite:
            return
        self._load_rates()
        self._dump_fx_rates_to_file(to_=cachepath, overwrite=overwrite)

    def _load_rates(self):
        self.logger.info(f"loading rates from online FX exchange...")
        base_rates = self._fx_sess.get_rates(self._base_currency)
        if base_rates.error_code:
            self.logger.error(f"Failed to get FX rates from online exchange: "
                              f"[{base_rates.error_code}] `{base_rates.error_text}`")
            return
        self.logger.info(f"FX rates for {self._base_currency} loaded. Attempting to populate FX table...")
        start_ = datetime.now()

        self._rates[self._base_currency] = base_rates.rates
        for currency, rate in base_rates.rates.items():
            if currency != self._base_currency:
                self._rates[currency] = {
                    self._base_currency: 1 / rate
                }

        for currency1, mapping in self._rates.items():
            if currency1 == self._base_currency:
                continue
            if base_vs_first := self.get_rate(self._base_currency, currency1):
                for currency2 in Currency.ALL_CURRENCIES:
                    if currency1 == currency2:
                        self._set_rate(currency1, currency2, 1.)
                    else:
                        if base_vs_second := self.get_rate(self._base_currency, currency2):
                            self._set_rate(currency1, currency2, base_vs_second / base_vs_first)
        time_taken = datetime.now() - start_
        self.logger.info(f"FX table populated! Time taken: {time_taken.seconds}s.")

    def _load_fx_rates_from_file(self, from_: Path) -> bool:
        self.logger.info(f"Attempting to load fx rates from file `{from_}`...")
        if from_.exists() and from_.is_file():
            try:
                with open(from_) as h:
                    self._rates = json.load(h)
                self.logger.info(f"FX rates successfully loaded!")
                return True
            except Exception as e:
                self.logger.error(f"failed to load exchange rate cache from file `{from_}`. error: {e}")
        return False

    def _dump_fx_rates_to_file(self, to_: Path, overwrite: bool = False) -> bool:
        to_ = to_.absolute()
        self.logger.debug(f"Attempting to dump FX rates to cache file: {to_}")
        parent = to_.parents[0]
        if not parent.exists():
            parent.mkdir(parents=True)
        if to_.exists() and to_.is_file():
            if not overwrite:
                self.logger.warning(f"Cache file {to_} already exists and overwrite is disabled. Aborting...")
                return False
        try:
            with open(to_, mode="w+") as h:
                json.dump(self._rates, h, indent=4)
            self.logger.debug(f"Exchange rates successfully saved to file {to_}")
            return True
        except Exception as e:
            self.logger.error(f"failed to dump exchange rate cache to file {to_}. error: {e}")
            return False

    def convert(self, amount: float, from_: str, to_: str) -> float:
        return self.get_rate(from_, to_) or 0. * amount

    def exchange(self, money: Money, other: str, in_place: bool = False) -> Money:
        new_amount = self.convert(money.amount, money.currency, other)
        if in_place:
            money.amount = new_amount
            money.currency = other
            return money
        return Money(amount=new_amount, currency=other)
