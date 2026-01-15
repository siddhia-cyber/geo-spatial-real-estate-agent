import requests
import time
time.sleep(1)
from services.logger import get_logger
logger = get_logger(__name__)



HEADERS = {"User-Agent": "GeoRAG/1.0"}


def geocode(location: str):
    logger.debug(f"Requesting geocode for: {location}")

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }

    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    if r.status_code != 200 or not r.json():
        logger.error(f"Geocoding API failed for location: {location}")

        return None

    data = r.json()[0]
    return float(data["lat"]), float(data["lon"])
