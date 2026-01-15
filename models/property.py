from pydantic import BaseModel

class Property(BaseModel):
    id: str
    price: float
    bhk: int
    area_sqft: float | None
    description: str
    city: str
    locality: str
    latitude: float
    longitude: float
