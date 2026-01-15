
from pydantic import BaseModel
from typing import Optional

class UserQuery(BaseModel):
    query: str
    location: str = "Mumbai"
    radius_km: float = 15

    bhk: Optional[int] = None
    max_price: Optional[float] = None
    require_gym: bool = False
