from fastapi import APIRouter, HTTPException
from models.query_schema import UserQuery

from services.embedding import embed
from services.geocoding import geocode
from services.query_parser import parse_query
from services.llm_explainer import explain_results
from db.vector_db import geo_vector_search

router = APIRouter()

import os
from services.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_CITY = os.getenv("SUPPORTED_CITY", "mumbai")

#  Domain intent guard
def is_real_estate_query(text: str) -> bool:
    keywords = [
        "flat", "flats", "apartment", "house", "bhk",
        "property", "properties", "home",
        "rent", "buy", "sale", "resale",
        "lac", "lakh", "crore", "budget",
        "sqft", "square", "area",
        "gym", "parking", "lift"
    ]
    text = text.lower()
    return any(word in text for word in keywords)


#  City extraction from query
def extract_city_from_query(text: str):
    cities = ["mumbai", "pune", "delhi", "bangalore", "chennai", "hyderabad"]
    text = text.lower()
    for city in cities:
        if city in text:
            return city
    return None


#  Main endpoint
@router.post("/ask")
def ask(query: UserQuery):
    try:
        logger.info(
     f"Incoming request | query='{query.query}' | location='{query.location}'"
)

        #  Parse intent
        parsed = parse_query(query.query)

    
        bhk = query.bhk if query.bhk not in (None, 0) else parsed.get("bhk")
        max_price = (
            query.max_price
            if query.max_price not in (None, 0)
            else parsed.get("max_price")
        )
        require_gym = query.require_gym or parsed.get("require_gym", False)

        
        #  Normalize filter types (look into this later something fishy here)
      
        if bhk is not None:
            bhk = int(bhk)

        if max_price is not None:
            max_price = int(max_price)
        logger.debug(
    f"Parsed filters | bhk={bhk}, max_price={max_price}, require_gym={require_gym}"
)



        #  Reject non–real-estate queries
        if not is_real_estate_query(query.query):
            logger.warning("Rejected query: not real estate related")

            return {
                "query": query.query,
                "interpreted_filters": {},
                "results": [],
                "explanation": (
                    "Your query does not appear to be related to real estate. "
                    "Please try searching for flats, apartments, or properties."
                )
            }

        #  Enforce query–location consistency
        mentioned_city = extract_city_from_query(query.query)
        requested_location = query.location.lower()

        if mentioned_city and mentioned_city not in requested_location:

            logger.warning(
    f"Rejected query: city mismatch | query_city={mentioned_city}, "
    f"location={query.location}"
)

            
            return {
                "query": query.query,
                "interpreted_filters": {},
                "results": [],
                "explanation": (
                    f"You searched for properties in {mentioned_city.title()}, "
                    f"but the selected location is {query.location}. "
                    "Please update the location to match your query."
                )
            }

        #  Dataset scope guard (Mumbai only)
        if SUPPORTED_CITY not in requested_location:
            logger.warning(
    f"Rejected query: unsupported city '{query.location}'"
)

            return {
                "query": query.query,
                "interpreted_filters": {
                    "bhk": bhk,
                    "max_price": max_price,
                    "require_gym": require_gym
                },
                "results": [],
                "explanation": (
                    "This dataset currently supports Mumbai locations only. "
                    f"No properties were found for {query.location}."
                )
            }

        #  Geocode location
        logger.debug(f"Geocoding location: {query.location}")

        coords = geocode(f"{query.location}, India")
        if not coords:
            logger.error(f"Geocoding failed for location: {query.location}")
            raise ValueError("Location not found")

        lat, lon = coords

        #  Embed query
        query_vector = embed(query.query)

        #  Vector + geo search

        logger.debug("Calling vector + geo search")

        results = geo_vector_search(
            vector=query_vector,
            latitude=lat,
            longitude=lon,
            radius_km=query.radius_km
        )
        logger.info(f"Vector DB returned {len(results.points)} candidates")

        logger.debug("Applying filters to vector results")
        clean_results = []
        for r in results.points:
            p = r.payload

            score = r.score
            reasons = []

            #  SOFT BHK preference
            if bhk not in (None, 0):
                if p.get("bhk") == bhk:
                    score += 0.15
                    reasons.append(f"{bhk} BHK matched")
                else:
                    reasons.append("Different BHK")

            #  SOFT price preference
            if max_price not in (None, 0):
                if p.get("price") <= max_price:
                    score += 0.15
                    reasons.append("Within budget")
                else:
                    reasons.append("Above budget")

            #  SOFT gym preference
            if require_gym:
                if "Gymnasium" in p.get("amenities", []):
                    score += 0.1
                    reasons.append("Gym available")
                else:
                    reasons.append("No gym")

            if not reasons:
                reasons.append("Semantically relevant")

            clean_results.append({
                "locality": p.get("locality"),
                "price": p.get("price"),
                "bhk": p.get("bhk"),
                "area_sqft": p.get("area_sqft"),
                "amenities": p.get("amenities", [])[:5],
                "score": round(score, 3),
                "reason": ", ".join(reasons)
            })
        logger.info(f"Results after filtering: {len(clean_results)}")

        # Sort by final relevance
        clean_results.sort(key=lambda x: x["score"], reverse=True)

        #  Explanation
        if not clean_results:
            explanation = (
                f"No properties were found in {query.location}. "
                "Try adjusting filters or using a broader search."
            )
        else:
            explanation = explain_results(query.query, clean_results)

        #  Final response
        logger.info("Request processed successfully")
        return {
            "query": query.query,
            "interpreted_filters": {
                "bhk": bhk,
                "max_price": max_price,
                "require_gym": require_gym
            },
            "results": clean_results,
            "explanation": explanation
        }

    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    except Exception:
       logger.exception("Unhandled error in /api/ask")
       raise HTTPException(
        status_code=400,
        detail="Internal error while processing request"
    )







