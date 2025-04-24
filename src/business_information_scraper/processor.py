import logging
import time
from typing import List, Optional

from business_information_scraper.maps_api_client import GoogleMapsClient
from business_information_scraper.data_models import BusinessInfo
from business_information_scraper.storage import DataStorage
from business_information_scraper.exceptions import ApiClientError

logger = logging.getLogger(__name__)

class BusinessDataProcessor:
    def __init__(self, api_client: GoogleMapsClient, storage: DataStorage, batch_size: int):
        self.api_client = api_client
        self.storage = storage
        self.batch_size = batch_size

    @staticmethod
    def _transform_details_to_model(details: Optional[dict]) -> Optional[BusinessInfo]:
        """Transforms raw API detail response into our Pydantic model."""
        if not details or 'place_id' not in details:
            return None

        try:
            business = BusinessInfo(
                place_id=details['place_id'],
                name=details.get('name', 'N/A'),
                address=details.get('formatted_address', 'unknown_address'),
                phone_number=details.get('international_phone_number', 'unknown_phone_number'),
                types=details.get('types', []),
            )
            return business
        except Exception as e:
             logger.error(f"Error transforming details for place_id {details.get('place_id', 'UNKNOWN')}: {e}", exc_info=True)
             return None


    def process_location(self, latitude: float, longitude: float, radius: int, business_type: str):
        """Fetches, processes, and stores business data for a location."""
        logger.info(f"Starting business data processing for location ({latitude}, {longitude}), radius={radius}, type={business_type}")

        try:
            nearby_places = self.api_client.find_nearby_businesses(latitude, longitude, radius, business_type)
        except ApiClientError as e:
            logger.error(f"Failed to fetch nearby places: {e}. Aborting process for this location.")
            raise ApiClientError from e

        processed_businesses: List[BusinessInfo] = []
        processed_count = 0
        failed_detail_fetches = 0

        for i, place in enumerate(nearby_places):
            place_id = place.get('place_id')
            place_name = place.get('name', 'Unknown Name')
            if not place_id:
                logger.warning(f"Skipping place without place_id: {place_name}")
                continue

            logger.debug(f"Processing place {i+1}/{len(nearby_places)}: {place_name} ({place_id})")

            business_info = self._transform_details_to_model(place)
            if business_info:
                processed_businesses.append(business_info)
                processed_count += 1
            else:
                failed_detail_fetches += 1

            if len(processed_businesses) >= 50:
                logger.info(f"Saving batch of {len(processed_businesses)} processed businesses...")
                try:
                    self.storage.save(processed_businesses)
                    processed_businesses = []
                except Exception as e:
                    logger.error(f"Failed to save data batch: {e}. Continuing processing, but data may be lost.", exc_info=True)

        if processed_businesses:
            logger.info(f"Saving final batch of {len(processed_businesses)} processed businesses...")
            try:
                self.storage.save(processed_businesses)
            except Exception as e:
                 logger.error(f"Failed to save final data batch: {e}.", exc_info=True)


        logger.info(f"Processing complete for location ({latitude}, {longitude}).")
        logger.info(f"Successfully processed and attempted to save: {processed_count} businesses.")
        logger.info(f"Failed to fetch or process details for: {failed_detail_fetches} places.")
