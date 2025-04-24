import googlemaps
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
import time
from typing import List, Dict, Any
import logging

from src.business_information_scraper.exceptions import ApiClientError

logger = logging.getLogger(__name__)

class GoogleMapsClient:
    def __init__(self, api_key: str, timeout: int = 10):
        try:
            self.client = googlemaps.Client(key=api_key, timeout=timeout)
            logger.info("Google Maps client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Maps client: {e}", exc_info=True)
            raise ApiClientError(f"Failed to initialize Google Maps client: {e}")

    def find_nearby_businesses(
            self,
            latitude: float,
            longitude: float,
            radius: int,
            business_type: str
    ) -> List[Dict[str, Any]]:
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
                logger.debug("Fetching next page...")
                time.sleep(2)
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
