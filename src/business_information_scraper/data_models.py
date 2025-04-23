from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional

class BusinessInfo(BaseModel):
    place_id: str
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    types: List[str] = Field(default_factory=list)
    website: Optional[HttpUrl] = None
    Maps_url: Optional[HttpUrl] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator('phone_number', mode='before')
    @classmethod
    def format_phone(cls, v):
         # Example: basic cleaning - real world needs more robust parsing
        if isinstance(v, str):
            return ''.join(filter(str.isdigit, v))
        return v