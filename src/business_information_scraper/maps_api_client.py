import googlemaps
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
import time
from typing import List, Dict, Any, Optional
import logging

from business_information_scraper.exceptions import ApiClientError

logger = logging.getLogger(__name__)

class GoogleMapsClient:
    def __init__(self, api_key: str, timeout: int = 10):
        try:
            self.client = googlemaps.Client(key=api_key, timeout=timeout)
            logger.info("Google Maps client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Maps client: {e}", exc_info=True)
            raise ApiClientError(f"Failed to initialize Google Maps client: {e}")

    def find_nearby_businesses(self, latitude: float, longitude: float, radius: int, business_type: str) -> List[Dict[str, Any]]:
        """Finds businesses using Nearby Search, handling pagination."""
        all_results = []
        location = (latitude, longitude)
        try:
            logger.info(f"Initiating Nearby Search: location={location}, radius={radius}, type={business_type}")
            response = self.client.places_nearby(
                location=location,
                radius=radius,
                type=business_type
            )
            all_results.extend(response.get('results', []))
            logger.debug(f"Nearby Search initial page returned {len(response.get('results', []))} results.")

            next_page_token = response.get('next_page_token')
            while next_page_token:
                logger.debug(f"Fetching next page with token: {next_page_token[:10]}...") # Avoid logging full token
                time.sleep(2) # Google requires a short delay before requesting the next page
                response = self.client.places_nearby(page_token=next_page_token)
                page_results = response.get('results', [])
                all_results.extend(page_results)
                logger.debug(f"Nearby Search next page returned {len(page_results)} results.")
                next_page_token = response.get('next_page_token')

            logger.info(f"Nearby Search completed. Found {len(all_results)} total potential places.")
            return all_results

        except (ApiError, HTTPError, Timeout, TransportError) as e:
            logger.error(f"Google Maps API error during Nearby Search: {e}", exc_info=True)
            raise ApiClientError(f"API error during Nearby Search: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Nearby Search: {e}", exc_info=True)
            raise ApiClientError(f"Unexpected error during Nearby Search: {e}")


    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Fetches detailed information for a specific place."""
        try:
            logger.debug(f"Fetching Place Details for place_id: {place_id}")
            # Specify fields to control costs and data fetched
            fields = ['place_id', 'name', 'formatted_address', 'international_phone_number',
                      'type', 'website', 'url', 'geometry']
            response = self.client.place(place_id=place_id, fields=fields)
            details = response.get('result')
            if details:
                 logger.debug(f"Successfully fetched details for place_id: {place_id}")
                 return details
            else:
                logger.warning(f"No details found for place_id: {place_id}. Response: {response}")
                return None
        except (ApiError, HTTPError, Timeout, TransportError) as e:
            # Specific handling: Not Found errors are common if a place is removed
            if isinstance(e, ApiError) and e.status == 'NOT_FOUND':
                 logger.warning(f"Place Details not found for place_id: {place_id} (API status: NOT_FOUND)")
                 return None
            logger.error(f"Google Maps API error fetching Place Details for {place_id}: {e}", exc_info=True)
            # Decide whether to raise or just log and return None
            # raise ApiClientError(f"API error fetching details for {place_id}: {e}")
            return None # Continue processing other places if one fails
        except Exception as e:
            logger.error(f"Unexpected error fetching Place Details for {place_id}: {e}", exc_info=True)
            # raise ApiClientError(f"Unexpected error fetching details for {place_id}: {e}")
            return None
