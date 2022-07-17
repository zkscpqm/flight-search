from datetime import timedelta

from geopy import distance


def calculate_distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    return distance.geodesic(a, b, ellipsoid='WGS-84').km


def format_timedelta_string(t: timedelta) -> str:
    if t.seconds == 0:
        return f"{t.microseconds / 1000}ms"
    mm, ss = divmod(t.seconds, 60)
    if mm == 0:
        return f"{ss}s"
    hh, mm = divmod(mm, 60)
    if hh == 0:
        return f"{mm}m {ss}s"
    return f"{hh}h {mm}m {ss}s"
