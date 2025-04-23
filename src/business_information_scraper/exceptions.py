class BusinessLocatorError(Exception):
    """Base exception class for all application-specific errors."""
    pass # No specific logic needed in the base class itself


class ConfigurationError(BusinessLocatorError):
    """Raised for errors related to application configuration.

    Examples:
        - Missing required environment variables.
        - Invalid values found during configuration loading (e.g., non-numeric radius).
        - Issues reading the .env file.
    """
    pass


class ApiClientError(BusinessLocatorError):
    """Raised for errors encountered while interacting with the Google Maps API.

    Examples:
        - Network timeouts connecting to the API.
        - Invalid API key or insufficient permissions.
        - Exceeding API quotas or rate limits.
        - Receiving unexpected error statuses from the API (4xx, 5xx).
        - Failure during client initialization.
    """
    pass


class DataProcessingError(BusinessLocatorError):
    """Raised for errors during the processing or transformation of data.

    Examples:
        - Failure to parse or validate data received from the API.
        - Errors transforming API data into the internal data model (e.g., BusinessInfo).
        - Unexpected data structures encountered.
    """
    pass


class StorageError(BusinessLocatorError):
    """Raised for errors related to data storage operations.

    Examples:
        - Failure to connect to the database.
        - Insufficient permissions to write to the output file/directory.
        - I/O errors during file writing.
        - Database constraint violations during insertion.
    """
    pass
