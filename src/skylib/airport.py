import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Airport:
    name: str
    country: str
    city: str
    latitude: float
    longitude: float
    ap_type: str
    iata: str
    icaq: str
    faa: str

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude


class AirportMatrix:

    def __init__(self, headers: list[str], matrix: list[list[float]]):
        if len(headers) != len(matrix):
            raise AssertionError(f"mismatched header and row sizes: Headers: {len(headers)}, Num Rows: {len(matrix)}")
        if len(headers) != len(matrix[0]):
            raise AssertionError(f"mismatched header and column sizes: Headers: {len(headers)}, Num Cols: {len(matrix[0])}")
        self._headers: list[str] = headers
        self._mx: list[list[float]] = matrix

    @classmethod
    def load_from_file(cls, file: Path) -> 'AirportMatrix':
        headers: list[str] = []
        matrix: list[list[float]] = []

        with open(file, "r") as mxf:
            head_ = next(mxf)
            for code in head_.split(','):
                headers.append(code)
            for i, line in enumerate(mxf):
                values = line.split(',')
                if len(values) != len(headers):
                    print(f"malformed csv. Data line {i + 1} has {len(values)} items, expected {len(headers)}")
                matrix.append([float(x) for x in values])
            if len(matrix) != len(headers):
                print(f"there are {len(matrix)} rows in the matrix.. expected {len(headers)}")
        return AirportMatrix(headers=headers, matrix=matrix)
