# tests/unit/test_data_models.py
import pytest
from pydantic import ValidationError
from src.business_information_scraper.data_models import BusinessInfo

def test_business_info_valid(sample_raw_place_details_dict):
    """Test successful creation and validation with valid data."""
    business = BusinessInfo(**sample_raw_place_details_dict)

    assert business.place_id == 'TEST_PLACE_ID_123' # Check required fields
    assert business.name == 'Test Business Name' # Check stripping
    assert business.address == '123 Test St, Test City'
    assert business.phone_number == '+1 555-123-4567' # Check cleaning
    assert business.types == [' store ', ' POINT_OF_INTEREST', 'establishment ']

def test_business_info_missing_mandatory():
    """Test validation error for missing mandatory fields."""
    with pytest.raises(ValidationError, match="Field required"): # Check specific field name if needed
         BusinessInfo(name='Only Name') # Missing place_id

@pytest.mark.parametrize(
    "field, value, expected_error_msg",
    [
        ('types', ["valid", 123], 'Input should be a valid string'),
    ]
)
def test_business_info_invalid_values(sample_raw_place_details_dict, field, value, expected_error_msg):
    """Test various single field validation errors."""
    invalid_data = sample_raw_place_details_dict.copy()
    invalid_data[field] = value
    with pytest.raises(ValidationError, match=expected_error_msg):
        BusinessInfo(**invalid_data)
