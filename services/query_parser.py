
import re
from services.logger import get_logger
logger = get_logger(__name__)


def parse_query(text: str) -> dict:
    logger.debug(f"Parsing query text: {text}")

    """
    Extract ONLY explicit intent from the query.
    No defaults. No guessing.
    """
    text = text.lower()

    filters = {
        "bhk": None,
        "max_price": None,
        "require_gym": False
    }

    # -------- BHK --------
    bhk_match = re.search(r"(\d+)\s*bhk", text)
    if bhk_match:
        filters["bhk"] = int(bhk_match.group(1))

    # -------- PRICE (lac/lakh) --------
    price_match = re.search(r"(\d+(?:\.\d+)?)\s*(lac|lakh)", text)
    if price_match:
        filters["max_price"] = int(float(price_match.group(1)) * 100_000)

    # -------- PRICE (crore) --------
    price_match = re.search(r"(\d+(?:\.\d+)?)\s*(cr|crore)", text)
    if price_match:
        filters["max_price"] = int(float(price_match.group(1)) * 10_000_000)

    # -------- AMENITIES --------
    if "gym" in text:
        filters["require_gym"] = True
    logger.debug(f"Parsed intent: {filters}")

    return filters


def parse_max_price(text: str):
    text = text.lower()

    # 1️⃣ lakh / lac
    match = re.search(r"(\d+(?:\.\d+)?)\s*(lac|lakh)", text)
    if match:
        return int(float(match.group(1)) * 100_000)

    # 2️⃣ crore / cr
    match = re.search(r"(\d+(?:\.\d+)?)\s*(cr|crore)", text)
    if match:
        return int(float(match.group(1)) * 10_000_000)

    # 3️⃣ under X (fallback ONLY if no unit)
    match = re.search(r"under\s*(\d+)", text)
    if match:
        # assume lakh by default (Indian context)
        return int(match.group(1)) * 100_000

    return None
