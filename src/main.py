import logging
import sys

from business_information_scraper.maps_api_client import GoogleMapsClient
from business_information_scraper.storage import get_storage_strategy
from business_information_scraper.processor import BusinessDataProcessor
from config import settings
from business_information_scraper.exceptions import ApiClientError, DataProcessingError

# Configure logging (consider using structlog for richer, structured logs)
logging.basicConfig(
    level=settings.log_level.upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout # Or configure file logging
)
# Suppress overly verbose logs from libraries if needed
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("googlemaps").setLevel(logging.INFO) # Adjust as needed

logger = logging.getLogger(__name__)


def run():
    logger.info("Starting Business Locator application.")
    logger.info(f"Configuration loaded: Search Location=({settings.search_latitude}, {settings.search_longitude}), Radius={settings.search_radius_meters}m, Type={settings.target_business_type}, Storage={settings.output_storage_type}")

    try:
        # 1. Initialize API Client
        api_client = GoogleMapsClient(
            api_key=settings.google_api_key,
            timeout=settings.api_timeout_seconds
        )

        # 2. Initialize Storage Strategy
        storage = get_storage_strategy(
            storage_type=settings.output_storage_type,
            file_path=settings.output_file_path, # Pass relevant config
        )
        storage.setup()

        # 3. Initialize Processor (Dependency Injection)
        processor = BusinessDataProcessor(api_client=api_client, storage=storage)

        # 4. Execute the main logic
        processor.process_location(
            latitude=settings.search_latitude,
            longitude=settings.search_longitude,
            radius=settings.search_radius_meters,
            business_type=settings.target_business_type
        )

        logger.info("Business Locator application finished successfully.")

    except ApiClientError as e:
         logger.critical(f"API Client critical error: {e}", exc_info=True)
         sys.exit(1) # Exit with error code
    except (DataProcessingError, ValueError, NotImplementedError) as e: # Catch specific config/storage errors
        logger.critical(f"Configuration or Processing error: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()