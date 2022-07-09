from pathlib import Path

from util.singleton import SingletonMeta
from util.types import nullable


class SecretManager(metaclass=SingletonMeta):

    def __init__(self, amadeus_cred_file: Path = None, db_cred_file: Path = None, exchange_rates_cred_file: Path = None):

        self.amadeus_cred_file: Path = amadeus_cred_file
        self.db_cred_file: Path = db_cred_file
        self.exchange_rates_cred_file: Path = exchange_rates_cred_file

        self.amadeus_api_key: nullable(str) = None
        self.amadeus_api_secret: nullable(str) = None
        self.db_password: nullable(str) = None
        self.exchangerates_api_key: nullable(str) = None
        self._init()

    def _init(self):
        if amadeus_creds := self.get_secret(self.amadeus_cred_file):
            self.amadeus_api_key, self.amadeus_api_secret = amadeus_creds.split(' ')
        self.db_password = self.get_secret(self.db_cred_file)
        self.exchangerates_api_key = self.get_secret(self.exchange_rates_cred_file)

    def reinitialize(self, amadeus_cred_file: Path = None, db_cred_file: Path = None, exchange_rates_cred_file: Path = None):
        self.amadeus_cred_file = amadeus_cred_file or self.amadeus_cred_file
        self.db_cred_file = db_cred_file or self.db_cred_file
        self.exchange_rates_cred_file = exchange_rates_cred_file or self.exchange_rates_cred_file
        self._init()

    @staticmethod
    def get_secret(file: Path) -> nullable(str):
        if file.exists() and file.is_file():
            with open(file) as h:
                return h.read()
