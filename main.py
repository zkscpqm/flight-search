from pathlib import Path

from secrets import SecretManager
from src.currency.exchange import ExchangeRateMap


def main():
    secrets = SecretManager(
        amadeus_cred_file=Path("secrets/amadeus_creds.secret"),
        db_cred_file=Path("secrets/db_password.secret"),
        exchange_rates_cred_file=Path("secrets/exchange_rates_apikey.secret")
    )

    fx = ExchangeRateMap(fx_exchange_api_key=secrets.exchangerates_api_key, cache_location=Path(".cache/"))

    # sess = AmadeusSession(api_key=secrets.amadeus_api_key, api_secret=secrets.amadeus_api_secret)
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
