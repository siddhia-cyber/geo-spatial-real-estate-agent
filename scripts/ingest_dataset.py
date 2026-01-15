
import pandas as pd
import json
from pathlib import Path
from qdrant_client.models import PointStruct
from services.geocoding import geocode
from services.embedding import embed
from db.vector_db import insert

CSV_PATH = "data/raw/Mumbai1.csv"
CITY = "Mumbai"

geo_cache = {}

def cached_geocode(location):
    if location in geo_cache:
        return geo_cache[location]
    coords = geocode(location)
    geo_cache[location] = coords
    return coords


# 🔹 Load dataset
df = pd.read_csv(CSV_PATH)

points = []

# 🔐 Dataset geographic bounds (initialized)
min_lat = float("inf")
max_lat = float("-inf")
min_lon = float("inf")
max_lon = float("-inf")

# 🔹 Ingest loop
for idx, row in df.iterrows():

    if idx % 10 == 0:
        print(f"⏳ Processed {idx} rows...")

    locality = row["Location"]
    bhk = int(row["No. of Bedrooms"])
    price = float(row["Price"])
    area = float(row["Area"])

    # 🔹 Build amenities list
    amenities = []
    for col in [
        "Gymnasium",
        "Lift Available",
        "Car Parking",
        "24x7 Security",
        "Children's Play Area",
        "Clubhouse",
        "Swimming Pool",
        "Jogging Track",
        "Gas Connection"
    ]:
        if col in df.columns and row[col] == 1:
            amenities.append(col)

    # 🔹 Geocode (cached)
    coords = cached_geocode(f"{locality}, {CITY}, India")
    if not coords:
        continue

    lat, lon = coords

    #  Update dataset bounds (ONLY for valid rows)
    min_lat = min(min_lat, lat)
    max_lat = max(max_lat, lat)
    min_lon = min(min_lon, lon)
    max_lon = max(max_lon, lon)

    # Text for embedding
    text = f"""
    {bhk} BHK apartment in {locality}, {CITY}.
    Area: {area} sqft.
    Price: {price}.
    Amenities: {', '.join(amenities) if amenities else 'Basic amenities'}.
    """

    vector = embed(text)

    points.append(
        PointStruct(
            id=idx,
            vector=vector,
            payload={
                "city": CITY,
                "locality": locality,
                "price": price,
                "bhk": bhk,
                "area_sqft": area,
                "amenities": amenities,
                "geo": {
                    "lat": lat,
                    "lon": lon
                }
            }
        )
    )

#  Insert into Qdrant
insert(points)

print(f"✅ Ingested {len(points)} properties successfully")

#  Save dataset geographic metadata
metadata = {
    "dataset_name": f"{CITY} Real Estate Dataset",
    "min_lat": min_lat,
    "max_lat": max_lat,
    "min_lon": min_lon,
    "max_lon": max_lon
}

Path("data").mkdir(exist_ok=True)

with open("data/dataset_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(" Dataset geographic bounds saved to data/dataset_metadata.json")
