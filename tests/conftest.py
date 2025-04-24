import pytest
from src.business_information_scraper.data_models import BusinessInfo

@pytest.fixture
def sample_raw_place_details_dict() -> dict:
    """Provides a sample raw dictionary mimicking Google Place Details API response."""
    return {
        'place_id': 'TEST_PLACE_ID_123',
        'name': 'Test Business Name',
        'address': '123 Test St, Test City',
        'phone_number': '+1 555-123-4567',
        'types': [' store ', ' POINT_OF_INTEREST', 'establishment '],
    }

@pytest.fixture
def sample_business_info(sample_raw_place_details_dict) -> BusinessInfo:
    """Provides a valid BusinessInfo instance based on raw data."""
    # Instantiate to ensure validation logic runs implicitly via fixture setup
    return BusinessInfo(**sample_raw_place_details_dict)

@pytest.fixture
def sample_nearby_result_page_1() -> dict:
    """Sample first page response for places_nearby."""
    return {
        'results': [
            {'place_id': 'PLACE_A', 'name': 'Place A'},
            {'place_id': 'PLACE_B', 'name': 'Place B'}
        ],
        'next_page_token': 'TOKEN_FOR_PAGE_2',
        'status': 'OK'
    }

@pytest.fixture
def sample_nearby_result_page_2() -> dict:
    """Sample second page response for places_nearby."""
    return {
        'results': [
            {'place_id': 'PLACE_C', 'name': 'Place C'}
        ],
        'next_page_token': None, # Last page
        'status': 'OK'
    }