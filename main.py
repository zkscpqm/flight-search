from pathlib import Path

import pandas as pd

from config import Configuration
from secrets import SecretManager
from src.currency.exchange import ExchangeRateMap
from src.flight_search.session import AmadeusSession
from src.flight_search_manager import FlightSearchManager
from src.geo.world_map import WorldMap
from util.logging.logger import get_logger


def main():

    config = Configuration(Path("config.json"))
    secrets = SecretManager(
        amadeus_cred_file=Path("secrets/amadeus_creds.secret"),
        db_cred_file=Path("secrets/db_password.secret"),
        exchange_rates_cred_file=Path("secrets/exchange_rates_apikey.secret")
    )

    logger = get_logger(
        date_fmt=config.logging_date_fmt,
        time_fmt=config.logging_time_fmt,
        dt_fmt=config.logging_dt_fmt,
        level=config.logging_level,
        set_default=True
    )

    mgr = FlightSearchManager(
        world_map=WorldMap(
            data=pd.read_csv(filepath_or_buffer=Path(config.world_map_airports_file), sep=';', header=0)
        ),
        fx_api=ExchangeRateMap(
            fx_exchange_api_key=secrets.exchangerates_api_key,
            cache_location=Path(config.fx_exchange_cache_location)
        ),
        flight_search=AmadeusSession(
            api_key=secrets.amadeus_api_key,
            api_secret=secrets.amadeus_api_secret,
        )
    )

    # sess =
    # data = pd.read_csv(filepath_or_buffer=Path("data/airports_dataset.csv"), sep=';', header=0)
    #
    # map_ = Map(data)
    # ap = map_.lookup('Sofia Airport')
    # bs = map_.lookup('Burgas Airport')
    # # print(ap.distance_to(bs))
    # if ap:
    #     nearby = map_.find_nearby(ap, max_radius_km=400)
    #     if len(nearby) > 0:
    #         print(f"[{ap.name}] nearby ({len(nearby)}): {', '.join((f'{ap_.name} ({dist})' for ap_, dist in nearby))}")


if __name__ == "__main__":
    main()
