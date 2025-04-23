import logging
from typing import List, Optional

from business_information_scraper.maps_api_client import GoogleMapsClient
from business_information_scraper.data_models import BusinessInfo
from business_information_scraper.storage import DataStorage
from business_information_scraper.exceptions import ApiClientError

logger = logging.getLogger(__name__)

class BusinessDataProcessor:
    def __init__(self, api_client: GoogleMapsClient, storage: DataStorage):
        self.api_client = api_client
        self.storage = storage

    def _transform_details_to_model(self, details: Optional[dict]) -> Optional[BusinessInfo]:
        """Transforms raw API detail response into our Pydantic model."""
        if not details or 'place_id' not in details:
            return None

        try:
            # Mapping API fields to our model fields
            business = BusinessInfo(
                place_id=details['place_id'],
                name=details.get('name', 'N/A'),
                address=details.get('formatted_address'),
                phone_number=details.get('international_phone_number'),
                types=details.get('types', []),
                # Pydantic handles URL validation if HttpUrl type is used
                website=details.get('website'),
                Maps_url=details.get('url'),
                latitude=details['geometry']['location']['lat'] if 'geometry' in details and 'location' in details['geometry'] else None,
                longitude=details['geometry']['location']['lng'] if 'geometry' in details and 'location' in details['geometry'] else None,
            )
            return business
        except Exception as e:
             # Catch potential Pydantic validation errors or unexpected structure issues
             logger.error(f"Error transforming details for place_id {details.get('place_id', 'UNKNOWN')}: {e}", exc_info=True)
             # Decide: skip this record or raise? Skipping allows partial success.
             return None


    def process_location(self, latitude: float, longitude: float, radius: int, business_type: str):
        """Fetches, processes, and stores business data for a location."""
        logger.info(f"Starting business data processing for location ({latitude}, {longitude}), radius={radius}, type={business_type}")

        try:
            nearby_places = self.api_client.find_nearby_businesses(latitude, longitude, radius, business_type)
        except ApiClientError as e:
            logger.error(f"Failed to fetch nearby places: {e}. Aborting process for this location.")
            # Depending on requirements, you might want to retry or just fail
            return # Or raise an exception

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

            try:
                details = self.api_client.get_place_details(place_id)
                if details:
                    business_info = self._transform_details_to_model(details)
                    if business_info:
                        processed_businesses.append(business_info)
                        processed_count += 1
                    else:
                        # Error logged within _transform_details_to_model
                        failed_detail_fetches += 1
                else:
                    # Place details couldn't be fetched (e.g., NOT_FOUND or API error)
                    # Error/Warning logged within get_place_details
                    failed_detail_fetches += 1

                # Optional: Add a small delay between Place Details calls to avoid hitting query limits rapidly
                # time.sleep(0.1)

            except ApiClientError as e:
                 # Error logged within get_place_details
                 logger.warning(f"Skipping place {place_id} due to API client error during detail fetch: {e}")
                 failed_detail_fetches += 1
            except Exception as e:
                logger.error(f"Unexpected error processing place {place_id}: {e}", exc_info=True)
                failed_detail_fetches += 1


            # Optional: Save data in batches to avoid holding too much in memory
            if len(processed_businesses) >= 50: # Example batch size
                logger.info(f"Saving batch of {len(processed_businesses)} processed businesses...")
                try:
                    self.storage.save(processed_businesses)
                    processed_businesses = [] # Clear the batch
                except Exception as e:
                    logger.error(f"Failed to save data batch: {e}. Continuing processing, but data may be lost.", exc_info=True)
                    # Potentially implement retry logic or dead-letter queue here

        # Save any remaining data
        if processed_businesses:
            logger.info(f"Saving final batch of {len(processed_businesses)} processed businesses...")
            try:
                self.storage.save(processed_businesses)
            except Exception as e:
                 logger.error(f"Failed to save final data batch: {e}.", exc_info=True)


        logger.info(f"Processing complete for location ({latitude}, {longitude}).")
        logger.info(f"Successfully processed and attempted to save: {processed_count} businesses.")
        logger.info(f"Failed to fetch or process details for: {failed_detail_fetches} places.")