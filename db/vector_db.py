from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PayloadSchemaType,
    PointStruct,
    Filter,
    FieldCondition,
    GeoRadius,
    GeoPoint,
    SearchParams
)
from services.logger import get_logger
logger = get_logger(__name__)

# QDRANT CLIENT
import os
from dotenv import load_dotenv
load_dotenv()

QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_data")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "properties")

client = QdrantClient(path=QDRANT_PATH)



# CREATE COLLECTION
logger.info(f"Ensuring Qdrant collection exists: {COLLECTION_NAME}")

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)
logger.info("Qdrant collection ready")


# Geo index (warning OK in local mode)
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="geo",
    field_schema=PayloadSchemaType.GEO
)


# INSERT DATA
def insert(points: list[PointStruct]):
    logger.info(f"Inserting {len(points)} points into Qdrant")

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

# GEO + VECTOR SEARCH 
from qdrant_client.models import (
    Filter,
    FieldCondition,
    GeoRadius,
    GeoPoint,
    Prefetch
)

def geo_vector_search(
          
    vector,
    latitude,
    longitude,
    radius_km=5,
    limit=5
):
    logger.debug("Executing geo + vector search")

    geo_filter = Filter(
        must=[
            FieldCondition(
                key="geo",
                geo_radius=GeoRadius(
                    center=GeoPoint(
                        lat=latitude,
                        lon=longitude
                    ),
                    radius=radius_km * 1000
                )
            )
        ]
    )

    return client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=limit,
        with_payload=True,
        prefetch=[
            # Prefetch(filter=geo_filter) cant use this is not working for broder queries
        ]
    )

def debug_count():
    return client.count(collection_name=COLLECTION_NAME, exact=True)
