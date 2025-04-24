from pydantic import BaseModel, Field
from typing import List, Optional

class BusinessInfo(BaseModel):
    place_id: str
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    types: List[str] = Field(default_factory=list)
