from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PositiveInt, PositiveFloat

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    google_api_key: str = Field(..., validation_alias='Maps_API_KEY')
    search_latitude: float
    search_longitude: float
    search_radius_meters: PositiveInt = 5000 # Default 5km
    target_business_type: str = 'restaurant' # Example: find restaurants
    output_storage_type: str = 'csv' # e.g., 'csv', 'json', 'postgresql'
    output_file_path: str | None = 'businesses.csv' # Required if type is csv/json
    batch_size: int = 100
    api_timeout_seconds: PositiveInt = 10
    log_level: str = "INFO"

settings = AppSettings()
