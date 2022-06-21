from pathlib import Path

import pandas as pd

from src.db.pg_connect import FlightSearchPostgresDB, DBConnectConfig
from src.skylib.airport import Airport
from src.skylib.session import AmadeusSession
from src.skylib.world_map import Map


def main():
    with open("amadeus_creds.secret", "r") as creds_file:
        api_key, api_secret = creds_file.read().split(' ')
    with open("db_pass.secret", "r") as db_pass_file:
        db_pass = db_pass_file.read()
    # sess = AmadeusSession(api_key=api_key, api_secret=api_secret)
    data = pd.read_csv(filepath_or_buffer=Path("data/airports_dataset.csv"), sep=';', header=0)
    # db = FlightSearchPostgresDB(
    #     config=DBConnectConfig(
    #         db_pass=db_pass
    #     )
    # )
    # mx.build_from_dataset(data, batch_size=100000)
    map_ = Map()
    map_.populate(data)
    for i, ap in enumerate(data.itertuples(index=False)):
        airport = Airport.from_namedtuple(ap)
        nearby = map_.find_nearby(airport, max_radius_km=50)
        if len(nearby) > 0:
            print(f"[{airport.name}] nearby: {', '.join((f'{ap_.name} ({dist})' for ap_, dist in nearby))}")


if __name__ == "__main__":
    main()
