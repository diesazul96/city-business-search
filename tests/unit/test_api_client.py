import pytest
from unittest.mock import MagicMock, call
from googlemaps.exceptions import ApiError, Timeout, TransportError, HTTPError

from src.business_information_scraper.maps_api_client import GoogleMapsClient
from src.business_information_scraper.exceptions import ApiClientError

@pytest.fixture
def mock_google_client(mocker):
    """Fixture to mock the googlemaps.Client instance."""
    mock = mocker.patch('googlemaps.Client', autospec=True)
    # Configure the instance returned by the constructor mock
    mock_instance = mock.return_value
    return mock_instance

def test_Maps_client_init_success(mocker):
    """Test successful initialization."""
    mock_client_constructor = mocker.patch('googlemaps.Client')
    api_client = GoogleMapsClient(api_key="fake_key", timeout=5)
    assert api_client.client is not None
    mock_client_constructor.assert_called_once_with(key="fake_key", timeout=5)

def test_Maps_client_init_failure(mocker):
    """Test failure during initialization."""
    mocker.patch('googlemaps.Client', side_effect=Exception("Init failed"))
    with pytest.raises(ApiClientError, match="Failed to initialize Google Maps client"):
        GoogleMapsClient(api_key="fake_key")

def test_find_nearby_businesses_single_page(mock_google_client, sample_nearby_result_page_1):
    """Test nearby search with a single page of results."""
    # Configure mock response
    page1_response = sample_nearby_result_page_1.copy()
    page1_response['next_page_token'] = None # Ensure only one page
    mock_google_client.places_nearby.return_value = page1_response

    client = GoogleMapsClient(api_key="fake_key")
    results = client.find_nearby_businesses(latitude=1.0, longitude=2.0, radius=100, business_type='test')

    assert results == page1_response['results']
    mock_google_client.places_nearby.assert_called_once_with(
        location=(1.0, 2.0), radius=100, type='test'
    )

def test_find_nearby_businesses_multiple_pages(mock_google_client, mocker, sample_nearby_result_page_1, sample_nearby_result_page_2):
    """Test nearby search handling pagination."""
    mock_sleep = mocker.patch('time.sleep') # Mock time.sleep

    # Configure mock responses for pagination
    mock_google_client.places_nearby.side_effect = [
        sample_nearby_result_page_1,
        sample_nearby_result_page_2
    ]

    client = GoogleMapsClient(api_key="fake_key")
    results = client.find_nearby_businesses(latitude=1.0, longitude=2.0, radius=100, business_type='test')

    # Check combined results
    expected_results = sample_nearby_result_page_1['results'] + sample_nearby_result_page_2['results']
    assert results == expected_results

    # Check calls to places_nearby
    expected_calls = [
        call(location=(1.0, 2.0), radius=100, type='test'),
        call(page_token=sample_nearby_result_page_1['next_page_token'])
    ]
    assert mock_google_client.places_nearby.call_args_list == expected_calls

    # Check that sleep was called between page requests
    mock_sleep.assert_called_once_with(2) # Check sleep duration

@pytest.mark.parametrize(
    "api_exception",
    [
        ApiError("API_KEY_INVALID"),
        Timeout("Request timed out"),
        TransportError("Network issue"),
        HTTPError(404)
    ]
)
def test_find_nearby_businesses_api_errors(mock_google_client, api_exception):
    """Test handling of various API errors during nearby search."""
    mock_google_client.places_nearby.side_effect = api_exception

    client = GoogleMapsClient(api_key="fake_key")
    with pytest.raises(ApiClientError, match="API error during Nearby Search"):
         client.find_nearby_businesses(latitude=1.0, longitude=2.0, radius=100, business_type='test')

def test_find_nearby_businesses_unexpected_error(mock_google_client):
    """Test handling of unexpected non-API errors."""
    mock_google_client.places_nearby.side_effect = ValueError("Something weird happened")

    client = GoogleMapsClient(api_key="fake_key")
    with pytest.raises(ApiClientError, match="Unexpected error during Nearby Search"):
         client.find_nearby_businesses(latitude=1.0, longitude=2.0, radius=100, business_type='test')
