from geopy import distance


def calculate_distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    return distance.geodesic(a, b, ellipsoid='WGS-84').km
