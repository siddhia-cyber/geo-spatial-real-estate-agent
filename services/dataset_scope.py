import json

# Load dataset geographic bounds
with open("data/dataset_metadata.json", "r") as f:
    DATASET_BOUNDS = json.load(f)


def is_inside_dataset(lat: float, lon: float) -> bool:
    """
    Checks whether a given latitude and longitude
    fall inside the geographic bounds of the dataset.
    """
    return (
        DATASET_BOUNDS["min_lat"] <= lat <= DATASET_BOUNDS["max_lat"]
        and DATASET_BOUNDS["min_lon"] <= lon <= DATASET_BOUNDS["max_lon"]
    )
